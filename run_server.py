#!/usr/bin/env python3
"""
Servidor Web para Stock Market Tycoon
Backend Flask que sirve la interfaz HTML/JS y conecta con la lógica del juego en Python.

Ejecutar: python run_server.py
Abrir navegador: http://localhost:5000
"""

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import os

# Importar lógica del juego
from game.game import StockMarketGame
from modes import QuickMode, StandardMode, ExtendedMode

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el navegador

# Estado global (en producción usaría base de datos o sesiones)
game_instance = None

@app.route('/')
def index():
    """Sirve el archivo HTML principal"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/create_game', methods=['POST'])
def create_game():
    """Crea una nueva partida"""
    global game_instance
    
    data = request.json
    mode_name = data.get('mode', 'standard')
    player_names = data.get('players', [])
    
    if len(player_names) < 2:
        return jsonify({'status': 'error', 'message': 'Se necesitan al menos 2 jugadores'})
    
    try:
        # Crear instancia del modo
        if mode_name == 'quick':
            mode_instance = QuickMode()
        elif mode_name == 'extended':
            mode_instance = ExtendedMode()
        else:
            mode_instance = StandardMode()
        
        # Iniciar juego
        game_instance = StockMarketGame(mode=mode_instance.mode_config['name'].lower())
        
        # Añadir jugadores
        for i, name in enumerate(player_names):
            game_instance.add_player(f"player_{i}", name, is_ai=False)
        
        return jsonify({'status': 'success', 'message': 'Partida creada'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    """Obtiene el estado actual del juego"""
    global game_instance
    
    if not game_instance:
        return jsonify({'error': 'No hay partida activa'})
    
    # Obtener empresas por sector
    market_data = {}
    for sector_name, sector in game_instance.market.sectors.items():
        market_data[sector_name] = {
            "companies": [
                {
                    "id": comp.company_id,
                    "name": comp.name,
                    "price": comp.current_price,
                    "total_shares": comp.total_shares,
                    "available_shares": comp.available_shares
                } for comp in sector.companies.values()
            ]
        }
    
    state = {
        "round": game_instance.round_number,
        "current_player": game_instance.current_player_idx,
        "players": [
            {
                "id": pid,
                "name": p.name,
                "cash": p.cash,
                "portfolio": dict(p.shares),
                "influence": p.influence_points,
                "bankrupt": p.is_bankrupt,
                "cards": list(p.cards)
            } for pid, p in game_instance.players.items()
        ],
        "market": market_data,
        "events": getattr(game_instance.event_manager, 'event_log', [])[-5:]
    }
    
    return jsonify(state)

@app.route('/api/buy_stock', methods=['POST'])
def buy_stock():
    """Compra acciones"""
    global game_instance
    
    if not game_instance:
        return jsonify({'status': 'error', 'message': 'No hay partida activa'})
    
    data = request.json
    player_idx = data.get('player_idx', 0)
    company_id = data.get('company_id')
    quantity = data.get('quantity', 1)
    
    try:
        player_ids = list(game_instance.players.keys())
        player_id = player_ids[player_idx]
        
        success, cost, msg = game_instance.buy_shares(player_id, company_id, int(quantity))
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': msg,
            'cost': cost
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/sell_stock', methods=['POST'])
def sell_stock():
    """Vende acciones"""
    global game_instance
    
    if not game_instance:
        return jsonify({'status': 'error', 'message': 'No hay partida activa'})
    
    data = request.json
    player_idx = data.get('player_idx', 0)
    company_id = data.get('company_id')
    quantity = data.get('quantity', 1)
    
    try:
        player_ids = list(game_instance.players.keys())
        player_id = player_ids[player_idx]
        
        success, value, msg = game_instance.sell_shares(player_id, company_id, int(quantity))
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': msg,
            'value': value
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/next_turn', methods=['POST'])
def next_turn():
    """Pasa al siguiente turno"""
    global game_instance
    
    if not game_instance:
        return jsonify({'status': 'error', 'message': 'No hay partida activa'})
    
    game_instance.next_turn()
    
    # Retornar nuevo estado
    return get_game_state()

@app.route('/api/trigger_event', methods=['POST'])
def trigger_event():
    """Activa un evento aleatorio"""
    global game_instance
    
    if not game_instance:
        return jsonify({'status': 'error', 'message': 'No hay partida activa'})
    
    event = game_instance.event_manager.generate_event(game_instance.round_number)
    if event:
        msg = game_instance.event_manager.apply_event(event, game_instance.market)
        return jsonify({
            'status': 'success',
            'message': msg,
            'event': event.name
        })
    
    return jsonify({'status': 'info', 'message': 'No se activó ningún evento'})

if __name__ == '__main__':
    print("=" * 60)
    print("📈 STOCK MARKET TYCOON - Servidor Web")
    print("=" * 60)
    print("\nIniciando servidor en http://localhost:5000")
    print("Abre tu navegador y empieza a jugar!\n")
    print("Presiona Ctrl+C para detener el servidor.\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
