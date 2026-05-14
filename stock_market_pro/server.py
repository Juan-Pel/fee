"""
Stock Market Tycoon - Server Principal
Gestiona conexiones Socket.IO, lógica de salas y coordinación de partidas
"""
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import time
import threading
from game_logic.core import StockMarketGame

app = Flask(__name__, static_folder='public')
app.config['SECRET_KEY'] = 'stock-market-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Almacenamiento de salas activas
rooms = {}
room_locks = {}

def get_game_state(room_id):
    """Obtiene el estado serializable del juego"""
    if room_id not in rooms:
        return None
    
    game = rooms[room_id]
    players_data = []
    
    for pid, player in game.players.items():
        players_data.append({
            'id': pid,
            'name': player.name,
            'capital': player.capital,
            'portfolio': player.portfolio,
            'is_bot': player.is_bot,
            'market_value': player.get_market_value(game.companies)
        })
    
    # Ordenar por valor de mercado para el ranking
    players_data.sort(key=lambda x: x['market_value'], reverse=True)
    
    companies_data = []
    for cid, company in game.companies.items():
        companies_data.append({
            'id': cid,
            'name': company.name,
            'sector': company.sector,
            'price': company.price,
            'trend': company.get_trend(),
            'total_shares': company.total_shares,
            'available_shares': company.get_available_shares()
        })
    
    return {
        'current_turn': game.current_turn,
        'turn_timer': game.turn_timer,
        'max_turns': game.max_turns,
        'current_round': game.current_round,
        'phase': game.phase,
        'players': players_data,
        'companies': companies_data,
        'events': game.event_log[-5:],  # Últimos 5 eventos
        'game_over': game.game_over,
        'winner': game.get_winner()
    }

@socketio.on('connect')
def handle_connect():
    print(f'Cliente conectado: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    room_id = None
    for rid, lock in room_locks.items():
        with lock:
            if request.sid in [p['id'] for p in rooms[rid].players.values() if not p['is_bot']]:
                room_id = rid
                break
    
    if room_id:
        leave_room(room_id)
        # Si era el último humano, cerrar la sala
        humans = [p for p in rooms[room_id].players.values() if not p.is_bot]
        if len(humans) == 0:
            del rooms[room_id]
            del room_locks[room_id]
            print(f'Sala {room_id} cerrada')
        else:
            emit('player_left', {'player_id': request.sid}, room=room_id)

@socketio.on('create_room')
def handle_create_room(data):
    room_id = str(uuid.uuid4())[:6].upper()
    config = data.get('config', {})
    
    rooms[room_id] = StockMarketGame(
        max_turns=config.get('max_turns', 20),
        turn_duration=config.get('turn_duration', 60),
        enable_events=config.get('enable_events', True)
    )
    room_locks[room_id] = threading.Lock()
    
    # Añadir jugador creador
    game = rooms[room_id]
    player_id = request.sid
    game.add_player(player_id, data['name'], is_bot=False)
    
    join_room(room_id)
    
    emit('room_created', {
        'room_id': room_id,
        'players': [{'id': player_id, 'name': data['name'], 'is_bot': False}]
    })
    print(f'Sala {room_id} creada por {data["name"]}')

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id'].upper()
    player_name = data['name']
    
    if room_id not in rooms:
        emit('error', {'message': 'Sala no encontrada'})
        return
    
    with room_locks[room_id]:
        game = rooms[room_id]
        player_id = request.sid
        
        if len([p for p in game.players.values() if not p.is_bot]) >= 6:
            emit('error', {'message': 'Sala llena'})
            return
        
        game.add_player(player_id, player_name, is_bot=False)
        join_room(room_id)
        
        players_data = [{'id': p_id, 'name': p.name, 'is_bot': p.is_bot} 
                       for p_id, p in game.players.items()]
        
        emit('room_joined', {
            'room_id': room_id,
            'players': players_data
        }, room=room_id)
        
        # Enviar estado actual al nuevo jugador
        emit('game_state_update', get_game_state(room_id))
        
        print(f'{player_name} se unió a la sala {room_id}')

@socketio.on('start_game')
def handle_start_game(data):
    room_id = data['room_id']
    
    if room_id not in rooms:
        return
    
    with room_locks[room_id]:
        game = rooms[room_id]
        humans = [p for p in game.players.values() if not p.is_bot]
        
        # Rellenar con bots si hay menos de 4 jugadores humanos
        while len(game.players) < 4:
            bot_name = f"Bot Corp {len(game.players) + 1}"
            game.add_player(str(uuid.uuid4()), bot_name, is_bot=True)
        
        game.start()
        
        # Iniciar hilo del temporizador
        def turn_timer():
            while not game.game_over:
                time.sleep(1)
                with room_locks[room_id]:
                    if game.phase == 'PLAYING':
                        game.turn_timer -= 1
                        if game.turn_timer <= 0:
                            game.next_turn()
                        
                        state = get_game_state(room_id)
                        socketio.emit('game_state_update', state, room=room_id)
                        
                        if game.game_over:
                            break
        
        timer_thread = threading.Thread(target=turn_timer, daemon=True)
        timer_thread.start()
        
        emit('game_started', get_game_state(room_id), room=room_id)
        print(f'Juego iniciado en sala {room_id}')

@socketio.on('buy_shares')
def handle_buy_shares(data):
    room_id = data['room_id']
    company_id = data['company_id']
    quantity = data['quantity']
    
    if room_id not in rooms:
        return
    
    with room_locks[room_id]:
        game = rooms[room_id]
        success, message = game.buy_shares(request.sid, company_id, quantity)
        
        state = get_game_state(room_id)
        emit('game_state_update', state, room=room_id)
        
        if not success:
            emit('error', {'message': message})

@socketio.on('sell_shares')
def handle_sell_shares(data):
    room_id = data['room_id']
    company_id = data['company_id']
    quantity = data['quantity']
    
    if room_id not in rooms:
        return
    
    with room_locks[room_id]:
        game = rooms[room_id]
        success, message = game.sell_shares(request.sid, company_id, quantity)
        
        state = get_game_state(room_id)
        emit('game_state_update', state, room=room_id)
        
        if not success:
            emit('error', {'message': message})

@socketio.on('next_turn')
def handle_next_turn(data):
    room_id = data['room_id']
    
    if room_id not in rooms:
        return
    
    with room_locks[room_id]:
        game = rooms[room_id]
        current_player = game.players.get(request.sid)
        
        if current_player and not current_player.is_bot:
            game.next_turn()
            state = get_game_state(room_id)
            emit('game_state_update', state, room=room_id)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    print("🚀 Stock Market Tycoon Server")
    print("🌐 Servidor iniciado en http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
