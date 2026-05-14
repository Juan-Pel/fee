from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string
import threading
import time
import sys
import os

# Agregar backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.game_logic import StockMarketGame
from backend.bot_ai import BotAI

app = Flask(__name__, 
            template_folder='frontend',
            static_folder='frontend')
app.config['SECRET_KEY'] = 'stock_market_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Almacenamiento de juegos activos
active_games = {}
bot_instances = {}

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def bot_player_thread(game_id, player_id):
    """Hilo para controlar las decisiones del bot"""
    game = active_games.get(game_id)
    if not game or player_id not in game.players:
        return
        
    bot = bot_instances.get(f"{game_id}_{player_id}")
    if not bot:
        bot = BotAI(difficulty='medium')
        bot_instances[f"{game_id}_{player_id}"] = bot
        
    while True:
        # Verificar si es el turno del bot
        current_state = game.get_game_state(player_id)
        if current_state['status'] != 'playing':
            break
            
        if current_state['active_player'] == player_id:
            # Es el turno del bot
            player_obj = game.players[player_id]
            action_type, action_data = bot.decide_action(
                player_obj, 
                game.companies, 
                current_state
            )
            
            # Pequeña pausa para simular pensamiento
            time.sleep(random.uniform(1.0, 2.5))
            
            # Ejecutar acción
            result = game.process_turn(player_id, action_type, action_data)
            
            # Notificar a todos
            socketio.emit('game_update', {
                'state': game.get_game_state(player_id),
                'last_action': f"Bot {player_obj.name} {result['message']}",
                'notification': result['message']
            }, room=game_id)
            
            # Pasar turno automáticamente después de la acción del bot
            next_player = game.advance_turn()
            if next_player is None: # Juego terminado
                scores = game.end_game()
                socketio.emit('game_over', {'scores': scores}, room=game_id)
                break
                
            socketio.emit('turn_change', {
                'active_player': next_player,
                'round': game.current_round,
                'time_left': game.config['turn_time']
            }, room=game_id)
            
        else:
            # No es su turno, esperar
            time.sleep(1)
            
        # Verificar si el juego sigue activo
        if game.game_status == 'finished':
            break

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<room_code>')
def game_room(room_code):
    return render_template('index.html', room_code=room_code)

@socketio.on('connect')
def handle_connect():
    print(f'Cliente conectado: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Cliente desconectado: {request.sid}')

@socketio.on('create_game')
def handle_create_game(data):
    player_name = data.get('name', 'Jugador')
    config = data.get('config', {})
    
    room_code = generate_room_code()
    game = StockMarketGame(room_code, request.sid, config)
    
    # Añadir jugador humano
    game.add_player(request.sid, player_name, is_bot=False)
    
    # Añadir bots si es partida local
    if data.get('mode') == 'local':
        bot_count = data.get('bots', 3)
        for i in range(bot_count):
            bot_name = f"Bot {i+1}"
            bot_id = f"bot_{room_code}_{i}"
            game.add_player(bot_id, bot_name, is_bot=True)
            
            # Iniciar hilo para el bot
            thread = socketio.start_background_task(bot_player_thread, room_code, bot_id)
    
    active_games[room_code] = game
    
    join_room(room_code)
    
    emit('room_created', {
        'room_code': room_code,
        'player_id': request.sid,
        'players': [{'id': p.id, 'name': p.name, 'is_bot': p.is_bot} for p in game.players.values()]
    })

@socketio.on('join_game')
def handle_join_game(data):
    room_code = data.get('room_code')
    player_name = data.get('name', 'Jugador')
    
    if room_code not in active_games:
        emit('error', {'message': 'Sala no encontrada'})
        return
        
    game = active_games[room_code]
    if game.game_status == 'playing':
        emit('error', {'message': 'El juego ya ha comenzado'})
        return
        
    game.add_player(request.sid, player_name, is_bot=False)
    join_room(room_code)
    
    emit('room_joined', {
        'room_code': room_code,
        'player_id': request.sid,
        'players': [{'id': p.id, 'name': p.name, 'is_bot': p.is_bot} for p in game.players.values()]
    }, room=room_code)

@socketio.on('start_game')
def handle_start_game(data):
    room_code = data.get('room_code')
    
    if room_code not in active_games:
        emit('error', {'message': 'Sala no encontrada'})
        return
        
    game = active_games[room_code]
    if game.host_id != request.sid:
        emit('error', {'message': 'Solo el anfitrión puede iniciar'})
        return
        
    if len(game.players) < 2:
        emit('error', {'message': 'Se necesitan al menos 2 jugadores'})
        return
        
    game.start_game()
    
    # Iniciar hilos para bots si existen
    for pid, player in game.players.items():
        if player.is_bot:
            thread = socketio.start_background_task(bot_player_thread, room_code, pid)
    
    initial_state = game.get_game_state(game.player_order[0])
    emit('game_started', {
        'state': initial_state,
        'active_player': game.player_order[0],
        'time_left': game.config['turn_time']
    }, room=room_code)

@socketio.on('player_action')
def handle_player_action(data):
    room_code = data.get('room_code')
    action_type = data.get('action_type')
    action_data = data.get('action_data', {})
    
    if room_code not in active_games:
        emit('error', {'message': 'Sala no encontrada'})
        return
        
    game = active_games[room_code]
    result = game.process_turn(request.sid, action_type, action_data)
    
    if result['success']:
        # Pasar turno
        next_player = game.advance_turn()
        
        if next_player is None: # Juego terminado
            scores = game.end_game()
            emit('game_over', {'scores': scores}, room=room_code)
            return
            
        # Enviar actualización a todos
        state = game.get_game_state(next_player)
        emit('game_update', {
            'state': state,
            'last_action': result['message']
        }, room=room_code)
        
        emit('turn_change', {
            'active_player': next_player,
            'round': game.current_round,
            'time_left': game.config['turn_time']
        }, room=room_code)
    else:
        emit('action_result', result, room=request.sid)

@socketio.on('resolve_trade')
def handle_resolve_trade(data):
    room_code = data.get('room_code')
    trade_id = data.get('trade_id')
    accept = data.get('accept', False)
    
    if room_code not in active_games:
        return
        
    game = active_games[room_code]
    success = game.resolve_trade(trade_id, accept)
    
    state = game.get_game_state(request.sid)
    emit('game_update', {'state': state}, room=room_code)

@socketio.on('update_board_rotation')
def handle_board_rotation(data):
    room_code = data.get('room_code')
    rotation = data.get('rotation', 0)
    
    if room_code not in active_games:
        return
        
    game = active_games[room_code]
    game.update_board_rotation(request.sid, rotation)
    
    # Solo enviar al jugador que rotó (vista individual)
    emit('board_rotated', {'rotation': rotation}, room=request.sid)

@socketio.on('request_state')
def handle_request_state(data):
    room_code = data.get('room_code')
    if room_code in active_games:
        game = active_games[room_code]
        state = game.get_game_state(request.sid)
        emit('game_update', {'state': state}, room=request.sid)

if __name__ == '__main__':
    print("🚀 Iniciando Stock Market Tycoon Server...")
    print("🌐 Abre tu navegador en: http://127.0.0.1:8080")
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
