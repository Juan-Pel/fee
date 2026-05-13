"""
Web API - Flask backend para Stock Market Tycoon
Proporciona endpoints REST y WebSocket para la interfaz web
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sys
import os

# Añadir el directorio padre al path para importar los módulos del juego
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import StockMarketGame, GameMode
from game.player import Player

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stock-market-tycoon-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Juego global (en producción usaríamos una mejor gestión de sesiones)
game: StockMarketGame = None
players_session = {}  # Mapea ID de sesión a ID de jugador


@app.route('/')
def index():
    """Página principal del juego"""
    return render_template('index.html')


@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Crea una nueva partida"""
    global game
    
    data = request.get_json() or {}
    mode = data.get('mode', 'standard')
    
    try:
        game = StockMarketGame(mode=mode)
        return jsonify({
            'success': True,
            'message': f'Partida {mode} creada exitosamente',
            'mode': mode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@app.route('/api/game/state')
def get_game_state():
    """Obtiene el estado actual del juego"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    return jsonify(game.get_game_state())


@app.route('/api/game/leaderboard')
def get_leaderboard():
    """Obtiene la clasificación actual"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    return jsonify(game.get_leaderboard())


@app.route('/api/player/add', methods=['POST'])
def add_player():
    """Añade un jugador a la partida"""
    global game
    
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    data = request.get_json()
    player_id = data.get('player_id')
    name = data.get('name')
    is_ai = data.get('is_ai', False)
    
    if not player_id or not name:
        return jsonify({'error': 'player_id y name son requeridos'}), 400
    
    try:
        player = game.add_player(player_id, name, is_ai)
        socketio.emit('player_added', {
            'player_id': player_id,
            'name': name,
            'cash': player.cash
        })
        
        return jsonify({
            'success': True,
            'player': {
                'player_id': player_id,
                'name': name,
                'cash': player.cash,
                'is_ai': is_ai
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/player/<player_id>')
def get_player(player_id):
    """Obtiene información de un jugador"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    player = game.get_player(player_id)
    if not player:
        return jsonify({'error': 'Jugador no encontrado'}), 404
    
    return jsonify(player.get_portfolio_summary({
        cid: c.get_info() for cid, c in game.market.companies.items()
    }))


@app.route('/api/market/companies')
def get_companies():
    """Obtiene todas las empresas del mercado"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    companies = {}
    for cid, company in game.market.companies.items():
        companies[cid] = company.get_info()
    
    return jsonify(companies)


@app.route('/api/market/sectors')
def get_sectors():
    """Obtiene todos los sectores del mercado"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    sectors = {}
    for sid, sector in game.market.sectors.items():
        sectors[sid] = {
            'name': sector.name,
            'modifier': sector.modifier,
            'companies': [c.company_id for c in sector.companies],
            'trend': sector.get_trend()
        }
    
    return jsonify(sectors)


@app.route('/api/action/buy', methods=['POST'])
def buy_shares():
    """Compra acciones"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    data = request.get_json()
    player_id = data.get('player_id')
    company_id = data.get('company_id')
    quantity = data.get('quantity', 1)
    
    if not player_id or not company_id:
        return jsonify({'error': 'player_id y company_id son requeridos'}), 400
    
    success, cost, message = game.buy_shares(player_id, company_id, quantity)
    
    if success:
        socketio.emit('shares_bought', {
            'player_id': player_id,
            'company_id': company_id,
            'quantity': quantity,
            'cost': cost
        })
    
    return jsonify({
        'success': success,
        'message': message,
        'cost': cost
    })


@app.route('/api/action/sell', methods=['POST'])
def sell_shares():
    """Vende acciones"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    data = request.get_json()
    player_id = data.get('player_id')
    company_id = data.get('company_id')
    quantity = data.get('quantity', 1)
    
    if not player_id or not company_id:
        return jsonify({'error': 'player_id y company_id son requeridos'}), 400
    
    success, value, message = game.sell_shares(player_id, company_id, quantity)
    
    if success:
        socketio.emit('shares_sold', {
            'player_id': player_id,
            'company_id': company_id,
            'quantity': quantity,
            'value': value
        })
    
    return jsonify({
        'success': success,
        'message': message,
        'value': value
    })


@app.route('/api/action/merge', methods=['POST'])
def merge_companies():
    """Fusiona dos empresas"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    data = request.get_json()
    player_id = data.get('player_id')
    company1_id = data.get('company1_id')
    company2_id = data.get('company2_id')
    
    if not player_id or not company1_id or not company2_id:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    
    success, message = game.attempt_merge(player_id, company1_id, company2_id)
    
    if success:
        socketio.emit('companies_merged', {
            'player_id': player_id,
            'company1_id': company1_id,
            'company2_id': company2_id
        })
    
    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/api/action/card', methods=['POST'])
def play_card():
    """Juega una carta"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    data = request.get_json()
    player_id = data.get('player_id')
    card_id = data.get('card_id')
    target = data.get('target')
    
    if not player_id or not card_id:
        return jsonify({'error': 'player_id y card_id son requeridos'}), 400
    
    result = game.play_card(player_id, card_id, target)
    
    if result['success']:
        socketio.emit('card_played', {
            'player_id': player_id,
            'card_id': card_id,
            'result': result
        })
    
    return jsonify(result)


@app.route('/api/turn/next', methods=['POST'])
def next_turn():
    """Pasa al siguiente turno"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    data = request.get_json() or {}
    player_id = data.get('player_id')
    
    # Verificar que es el turno del jugador
    if player_id and game.get_current_player().player_id != player_id:
        return jsonify({'error': 'No es tu turno'}), 403
    
    current_player = game.get_current_player().player_id
    game.next_turn()
    next_player = game.get_current_player().player_id
    
    socketio.emit('turn_changed', {
        'previous_player': current_player,
        'current_player': next_player,
        'round': game.round_number
    })
    
    # Si el siguiente jugador es IA, procesar su turno automáticamente
    if game.get_player(next_player).is_ai:
        socketio.emit('ai_turn', {'player_id': next_player})
        _process_ai_turn(next_player)
    
    return jsonify({
        'success': True,
        'current_player': next_player,
        'round': game.round_number
    })


def _process_ai_turn(player_id):
    """Procesa el turno de la IA"""
    if not game or not game.get_player(player_id):
        return
    
    player = game.get_player(player_id)
    
    # IA simple: compra acciones aleatorias si tiene dinero
    if player.cash > 5000:
        available_companies = [
            cid for cid, c in game.market.companies.items()
            if c.current_price * 10 <= player.cash
        ]
        
        if available_companies:
            import random
            company_id = random.choice(available_companies)
            quantity = min(10, int(player.cash / (game.market.get_company(company_id).current_price * 1.1)))
            
            if quantity > 0:
                game.buy_shares(player_id, company_id, quantity)
                socketio.emit('ai_action', {
                    'player_id': player_id,
                    'action': 'buy',
                    'company_id': company_id,
                    'quantity': quantity
                })
    
    # Pasar turno
    game.next_turn()
    next_player = game.get_current_player().player_id
    
    socketio.emit('turn_changed', {
        'previous_player': player_id,
        'current_player': next_player,
        'round': game.round_number
    })
    
    # Si el siguiente también es IA, continuar
    if game.get_player(next_player).is_ai:
        socketio.emit('ai_turn', {'player_id': next_player})
        _process_ai_turn(next_player)


@app.route('/api/events/current')
def get_current_events():
    """Obtiene eventos activos"""
    if not game:
        return jsonify({'error': 'No hay partida activa'}), 404
    
    events = []
    for event in game.event_manager.active_events:
        events.append({
            'event_id': event.event_id,
            'name': event.name,
            'description': event.description,
            'type': event.type,
            'remaining_rounds': event.duration
        })
    
    return jsonify(events)


@socketio.on('connect')
def handle_connect():
    """Maneja la conexión de un cliente"""
    print('Cliente conectado')
    emit('connected', {'message': 'Conectado al servidor'})


@socketio.on('disconnect')
def handle_disconnect():
    """Maneja la desconexión de un cliente"""
    print('Cliente desconectado')


@socketio.on('join_game')
def handle_join(data):
    """Un jugador se une a la partida"""
    player_id = data.get('player_id')
    if player_id:
        players_session[request.sid] = player_id
        emit('joined', {'player_id': player_id})


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
