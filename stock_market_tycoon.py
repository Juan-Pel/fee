import os
import sys
import time
import random
import threading
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit

# ==========================================
# CONFIGURACIÓN E IMPORTACIONES
# ==========================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secreto_bolsa_tycoon_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Estado global del juego (en memoria)
game_state = {
    'active': False,
    'players': [],
    'companies': [],
    'market_events': [],
    'turn': 0,
    'current_player_idx': 0,
    'logs': [],
    'mode': 'standard',
    'start_time': 0,
    'duration': 1800,
    'game_id': None
}

# ==========================================
# DATOS DEL JUEGO
# ==========================================

SECTORS = {
    'Tecnología': {'color': '#3b82f6', 'volatility': 1.5},
    'Energía': {'color': '#eab308', 'volatility': 1.2},
    'Turismo': {'color': '#ec4899', 'volatility': 1.3},
    'Finanzas': {'color': '#10b981', 'volatility': 1.1},
    'Salud': {'color': '#ef4444', 'volatility': 1.0},
    'Inmobiliario': {'color': '#8b5cf6', 'volatility': 1.4},
    'Consumo': {'color': '#f97316', 'volatility': 1.1},
    'Industrial': {'color': '#64748b', 'volatility': 1.2}
}

COMPANY_NAMES = [
    ("TechCorp", "Tecnología"), ("NanoSoft", "Tecnología"),
    ("OilMax", "Energía"), ("GreenPower", "Energía"),
    ("TravelAir", "Turismo"), ("HotelLux", "Turismo"),
    ("BankGlobal", "Finanzas"), ("InsureSafe", "Finanzas"),
    ("PharmaLife", "Salud"), ("BioGen", "Salud"),
    ("Constructa", "Inmobiliario"), ("EstatePro", "Inmobiliario"),
    ("FoodMart", "Consumo"), ("AutoDrive", "Industrial"),
    ("SteelWorks", "Industrial"), ("RoboTech", "Tecnología")
]

EVENTS_POSITIVE = [
    {"name": "Boom Tecnológico", "effect": "tech_up", "desc": "Las acciones tecnológicas suben un 20%"},
    {"name": "Descubrimiento Energético", "effect": "energy_up", "desc": "La energía se revaloriza un 15%"},
    {"name": "Temporada Turística", "effect": "tourism_up", "desc": "El turismo alcanza máximos históricos (+15%)"},
    {"name": "Estabilidad Financiera", "effect": "finance_up", "desc": "Los mercados financieros ganan confianza (+10%)"}
]

EVENTS_NEGATIVE = [
    {"name": "Crisis Petrolera", "effect": "energy_down", "desc": "El precio del petróleo cae en picado (-20%)"},
    {"name": "Pandemia Global", "effect": "tourism_down", "desc": "El turismo se desploma (-25%)"},
    {"name": "Burbuja Inmobiliaria", "effect": "realestate_down", "desc": "El mercado inmobiliario corrige (-20%)"},
    {"name": "Regulación Estricta", "effect": "tech_down", "desc": "Nuevas leyes frenan a las tecnológicas (-15%)"}
]

CARDS_SPECIAL = [
    {"name": "Compra Inteligente", "desc": "Compra acciones al 80% del precio actual"},
    {"name": "Venta Premium", "desc": "Vende acciones al 120% del precio actual"},
    {"name": "Fusión Hostil", "desc": "Intenta absorber una empresa rival"},
    {"name": "Rescate Gubernamental", "desc": "Recibe $5000 de ayuda estatal"},
    {"name": "Información Privilegiada", "desc": "Conoce el próximo evento de mercado"}
]

# ==========================================
# LÓGICA DEL JUEGO
# ==========================================

def init_game(mode, player_name="Jugador 1"):
    """Inicializa una nueva partida"""
    global game_state
    
    duration_map = {'quick': 900, 'standard': 2700, 'extended': 5400}
    
    game_state = {
        'active': True,
        'players': [{
            'id': 'human',
            'name': player_name,
            'capital': 10000,
            'stocks': {},
            'influence': 0,
            'cards': [],
            'is_bot': False
        }],
        'companies': [],
        'market_events': [],
        'turn': 1,
        'current_player_idx': 0,
        'logs': ["¡Mercado abierto! Comienza la sesión."],
        'mode': mode,
        'start_time': time.time(),
        'duration': duration_map.get(mode, 2700),
        'game_id': str(random.randint(1000, 9999))
    }
    
    # Añadir bots según modo
    bot_count = {'quick': 1, 'standard': 3, 'extended': 5}.get(mode, 3)
    for i in range(bot_count):
        game_state['players'].append({
            'id': f'bot_{i}',
            'name': f'Bot Corporación {i+1}',
            'capital': 10000,
            'stocks': {},
            'influence': 0,
            'cards': [],
            'is_bot': True
        })
    
    # Crear empresas
    for name, sector in COMPANY_NAMES:
        base_price = random.randint(10, 50)
        game_state['companies'].append({
            'id': name.lower().replace(' ', ''),
            'name': name,
            'sector': sector,
            'price': base_price,
            'history': [base_price],
            'owner': None,
            'shares_available': 100
        })
    
    # Inicializar stocks de jugadores
    for player in game_state['players']:
        player['stocks'] = {comp['id']: 0 for comp in game_state['companies']}
    
    log_message(f"Partida {mode} iniciada con {len(game_state['players'])} jugadores")
    return game_state

def log_message(msg):
    game_state['logs'].append(f"[Turno {game_state['turn']}] {msg}")
    if len(game_state['logs']) > 50:
        game_state['logs'] = game_state['logs'][-50:]

def update_market():
    """Actualiza precios del mercado con volatilidad"""
    for company in game_state['companies']:
        sector_info = SECTORS.get(company['sector'], {'volatility': 1.0})
        change = random.uniform(-0.05, 0.05) * sector_info['volatility']
        
        # Aplicar efectos de eventos
        for event in game_state['market_events'][-3:]:
            if event['effect'] == 'tech_up' and company['sector'] == 'Tecnología':
                change += 0.20
            elif event['effect'] == 'tech_down' and company['sector'] == 'Tecnología':
                change -= 0.15
            elif event['effect'] == 'energy_up' and company['sector'] == 'Energía':
                change += 0.15
            elif event['effect'] == 'energy_down' and company['sector'] == 'Energía':
                change -= 0.20
            elif event['effect'] == 'tourism_up' and company['sector'] == 'Turismo':
                change += 0.15
            elif event['effect'] == 'tourism_down' and company['sector'] == 'Turismo':
                change -= 0.25
            elif event['effect'] == 'finance_up' and company['sector'] == 'Finanzas':
                change += 0.10
            elif event['effect'] == 'realestate_down' and company['sector'] == 'Inmobiliario':
                change -= 0.20
        
        new_price = max(1, company['price'] * (1 + change))
        company['price'] = round(new_price, 2)
        company['history'].append(company['price'])
        if len(company['history']) > 20:
            company['history'] = company['history'][-20:]

def trigger_random_event():
    """Dispara un evento aleatorio de mercado"""
    if random.random() < 0.3:  # 30% de probabilidad por turno
        if random.random() < 0.5:
            event = random.choice(EVENTS_POSITIVE)
        else:
            event = random.choice(EVENTS_NEGATIVE)
        
        game_state['market_events'].append(event)
        log_message(f"📰 EVENTO: {event['name']} - {event['desc']}")
        
        if len(game_state['market_events']) > 5:
            game_state['market_events'] = game_state['market_events'][-5:]

def bot_action(bot):
    """IA simple para bots"""
    action = random.choice(['buy', 'sell', 'hold'])
    
    if action == 'hold':
        return
    
    available_companies = [c for c in game_state['companies'] if c['shares_available'] > 0]
    if not available_companies:
        return
    
    company = random.choice(available_companies)
    comp_id = company['id']
    
    if action == 'buy' and bot['capital'] >= company['price']:
        max_affordable = int(bot['capital'] / company['price'])
        qty = min(random.randint(1, max(1, max_affordable)), company['shares_available'])
        if qty > 0:
            cost = qty * company['price']
            bot['capital'] -= cost
            bot['stocks'][comp_id] += qty
            company['shares_available'] -= qty
            company['price'] *= 1.02  # La compra sube ligeramente el precio
            log_message(f"{bot['name']} compró {qty} acciones de {company['name']}")
    
    elif action == 'sell' and bot['stocks'].get(comp_id, 0) > 0:
        qty = min(random.randint(1, bot['stocks'][comp_id]), 10)
        if qty > 0:
            revenue = qty * company['price']
            bot['capital'] += revenue
            bot['stocks'][comp_id] -= qty
            company['shares_available'] += qty
            company['price'] *= 0.98  # La venta baja ligeramente el precio
            log_message(f"{bot['name']} vendió {qty} acciones de {company['name']}")

def check_game_over():
    """Verifica si el juego terminó"""
    elapsed = time.time() - game_state['start_time']
    if elapsed >= game_state['duration']:
        game_state['active'] = False
        # Calcular ganador
        scores = []
        for player in game_state['players']:
            stock_value = sum(player['stocks'].get(c['id'], 0) * c['price'] for c in game_state['companies'])
            total_value = player['capital'] + stock_value
            scores.append({'name': player['name'], 'value': total_value, 'capital': player['capital'], 'stocks': stock_value})
        
        scores.sort(key=lambda x: x['value'], reverse=True)
        winner = scores[0]
        log_message(f"🏆 JUEGO TERMINADO! Ganador: {winner['name']} con ${winner['value']:,.2f}")
        return True
    return False

# ==========================================
# HTML TEMPLATE (INTERFAZ WEB)
# ==========================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Market Tycoon</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-panel: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #3b82f6;
            --success: #22c55e;
            --danger: #ef4444;
            --warning: #eab308;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid var(--accent);
            margin-bottom: 30px;
        }
        
        h1 { font-size: 2.5em; color: var(--accent); margin-bottom: 10px; }
        .subtitle { color: var(--text-muted); }
        
        /* Pantalla de Inicio */
        #start-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
        }
        
        .mode-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            width: 100%;
            max-width: 1000px;
            margin-top: 30px;
        }
        
        .mode-card {
            background: var(--bg-panel);
            border: 2px solid var(--accent);
            border-radius: 12px;
            padding: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .mode-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        }
        
        .mode-card h3 { color: var(--accent); margin-bottom: 10px; font-size: 1.5em; }
        .mode-card .time { color: var(--warning); font-weight: bold; margin: 10px 0; }
        .mode-card p { color: var(--text-muted); line-height: 1.6; }
        
        /* Dashboard del Juego */
        #game-dashboard { display: none; }
        
        .game-header {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: var(--bg-panel);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid var(--accent);
        }
        
        .stat-card.capital { border-color: var(--success); }
        .stat-card.turn { border-color: var(--warning); }
        .stat-card.mode { border-color: var(--danger); }
        
        .stat-value { font-size: 1.8em; font-weight: bold; margin-top: 5px; }
        .stat-label { color: var(--text-muted); font-size: 0.9em; }
        
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        
        .panel {
            background: var(--bg-panel);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .panel-title {
            font-size: 1.3em;
            color: var(--accent);
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--text-muted);
        }
        
        /* Tabla de Empresas */
        .company-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .company-table th, .company-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .company-table th { color: var(--text-muted); font-weight: 600; }
        
        .sector-badge {
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .price-up { color: var(--success); }
        .price-down { color: var(--danger); }
        
        .action-btn {
            padding: 6px 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 5px;
            transition: all 0.2s;
        }
        
        .btn-buy { background: var(--success); color: white; }
        .btn-buy:hover { background: #16a34a; }
        
        .btn-sell { background: var(--danger); color: white; }
        .btn-sell:hover { background: #dc2626; }
        
        .btn-disabled { 
            background: var(--text-muted); 
            cursor: not-allowed; 
            opacity: 0.5;
        }
        
        /* Log de Eventos */
        .log-container {
            height: 300px;
            overflow-y: auto;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .log-entry {
            margin-bottom: 8px;
            padding: 5px;
            border-left: 3px solid var(--accent);
            padding-left: 10px;
        }
        
        .log-event { border-color: var(--warning); color: var(--warning); }
        .log-turn { border-color: var(--success); color: var(--success); }
        
        /* Controles */
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn-primary {
            background: var(--accent);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .btn-primary:hover { background: #2563eb; transform: scale(1.05); }
        
        .btn-next { background: var(--warning); }
        .btn-next:hover { background: #ca8a04; }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background: var(--bg-panel);
            padding: 30px;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            text-align: center;
        }
        
        .modal input {
            width: 100%;
            padding: 10px;
            margin: 15px 0;
            border-radius: 6px;
            border: 1px solid var(--text-muted);
            background: var(--bg-dark);
            color: var(--text-main);
        }
        
        /* Gráfico */
        .chart-container {
            height: 250px;
            margin-top: 20px;
        }
        
        /* Ranking */
        .ranking-list {
            list-style: none;
        }
        
        .ranking-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .ranking-item:first-child {
            background: rgba(234, 179, 8, 0.2);
            border-radius: 6px;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: var(--text-muted);
        }
        
        .spinner {
            border: 4px solid var(--bg-panel);
            border-top: 4px solid var(--accent);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📈 Stock Market Tycoon</h1>
            <p class="subtitle">Simulador de Mercado Bursátil Competitivo</p>
        </header>
        
        <!-- Pantalla de Inicio -->
        <div id="start-screen">
            <h2 style="margin-bottom: 20px;">Selecciona Modo de Juego</h2>
            <div class="mode-cards">
                <div class="mode-card" onclick="selectMode('quick')">
                    <h3>⚡ Partida Rápida</h3>
                    <div class="time">15 minutos</div>
                    <p>Ideal para 2-4 jugadores. Objetivo: Mayor valor de mercado al finalizar.</p>
                </div>
                <div class="mode-card" onclick="selectMode('standard')">
                    <h3>📊 Partida Estándar</h3>
                    <div class="time">30-45 minutos</div>
                    <p>4-6 jugadores. Objetivo: Alcanzar 50 puntos de influencia.</p>
                </div>
                <div class="mode-card" onclick="selectMode('extended')">
                    <h3>🏛️ Partida Extendida</h3>
                    <div class="time">90 minutos</div>
                    <p>6-8 jugadores. Controla 3 sectores completos y supera el umbral de capital.</p>
                </div>
            </div>
        </div>
        
        <!-- Dashboard del Juego -->
        <div id="game-dashboard">
            <div class="game-header">
                <div class="stat-card capital">
                    <div class="stat-label">Tu Capital</div>
                    <div class="stat-value" id="player-capital">$10,000</div>
                </div>
                <div class="stat-card turn">
                    <div class="stat-label">Turno Actual</div>
                    <div class="stat-value" id="current-turn">1</div>
                </div>
                <div class="stat-card mode">
                    <div class="stat-label">Modo</div>
                    <div class="stat-value" id="game-mode">Estándar</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Tiempo Restante</div>
                    <div class="stat-value" id="time-remaining">--:--</div>
                </div>
            </div>
            
            <div class="main-grid">
                <div>
                    <div class="panel">
                        <h3 class="panel-title">📊 Mercado de Valores</h3>
                        <table class="company-table">
                            <thead>
                                <tr>
                                    <th>Empresa</th>
                                    <th>Sector</th>
                                    <th>Precio</th>
                                    <th>Tu Posición</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody id="market-table-body">
                                <tr><td colspan="5" class="loading">Cargando mercado...</td></tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="panel">
                        <h3 class="panel-title">📈 Gráfico de Rendimiento</h3>
                        <div class="chart-container">
                            <canvas id="market-chart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div>
                    <div class="panel">
                        <h3 class="panel-title">🎮 Acciones</h3>
                        <div class="controls">
                            <button class="btn-primary btn-next" onclick="nextTurn()">Siguiente Turno</button>
                        </div>
                    </div>
                    
                    <div class="panel">
                        <h3 class="panel-title">🏆 Ranking</h3>
                        <ul class="ranking-list" id="ranking-list">
                            <li class="loading">Calculando...</li>
                        </ul>
                    </div>
                    
                    <div class="panel">
                        <h3 class="panel-title">📰 Noticias del Mercado</h3>
                        <div class="log-container" id="game-log">
                            <div class="log-entry">Esperando inicio del juego...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal de Nombre -->
    <div id="name-modal" class="modal">
        <div class="modal-content">
            <h2>Bienvenido al Mercado</h2>
            <p>Ingresa tu nombre de corporación</p>
            <input type="text" id="player-name-input" placeholder="Ej: MegaCorp Industries" maxlength="20">
            <button class="btn-primary" onclick="confirmName()">Comenzar</button>
        </div>
    </div>
    
    <!-- Modal de Compra/Venta -->
    <div id="trade-modal" class="modal">
        <div class="modal-content">
            <h2 id="trade-title">Comprar Acciones</h2>
            <p id="trade-info"></p>
            <input type="number" id="trade-qty" min="1" value="1">
            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 15px;">
                <button class="btn-primary btn-buy" id="confirm-trade-btn">Confirmar</button>
                <button class="btn-primary btn-sell" onclick="closeTradeModal()">Cancelar</button>
            </div>
        </div>
    </div>
    
    <script>
        let socket;
        let selectedMode = '';
        let playerName = '';
        let currentGameId = null;
        let tradeAction = ''; // 'buy' or 'sell'
        let selectedCompany = null;
        let marketChart = null;
        
        // Conectar al servidor
        function connectSocket() {
            socket = io();
            
            socket.on('connect', () => {
                console.log('Conectado al servidor');
            });
            
            socket.on('game_started', (data) => {
                console.log('Juego iniciado:', data);
                currentGameId = data.game_id;
                showDashboard();
                updateUI(data);
            });
            
            socket.on('game_update', (data) => {
                console.log('Actualización recibida');
                updateUI(data);
            });
            
            socket.on('game_over', (data) => {
                alert('🏆 Juego Terminado!\\n' + data.message);
                location.reload();
            });
            
            socket.on('error', (data) => {
                alert('Error: ' + data.message);
            });
        }
        
        // Seleccionar modo
        function selectMode(mode) {
            selectedMode = mode;
            document.getElementById('name-modal').style.display = 'flex';
            document.getElementById('player-name-input').focus();
        }
        
        // Confirmar nombre
        function confirmName() {
            playerName = document.getElementById('player-name-input').value.trim();
            if (!playerName) {
                alert('Por favor ingresa un nombre');
                return;
            }
            document.getElementById('name-modal').style.display = 'none';
            startGame();
        }
        
        // Iniciar juego
        function startGame() {
            fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mode: selectedMode, player_name: playerName})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    connectSocket();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                console.error(err);
                alert('Error de conexión');
            });
        }
        
        // Mostrar dashboard
        function showDashboard() {
            document.getElementById('start-screen').style.display = 'none';
            document.getElementById('game-dashboard').style.display = 'block';
        }
        
        // Actualizar interfaz
        function updateUI(data) {
            // Actualizar estadísticas
            const humanPlayer = data.players.find(p => p.id === 'human');
            if (humanPlayer) {
                document.getElementById('player-capital').textContent = '$' + humanPlayer.capital.toLocaleString();
            }
            
            document.getElementById('current-turn').textContent = data.turn;
            
            const modeNames = {'quick': 'Rápida', 'standard': 'Estándar', 'extended': 'Extendida'};
            document.getElementById('game-mode').textContent = modeNames[data.mode] || data.mode;
            
            // Tiempo restante
            const elapsed = Date.now() / 1000 - data.start_time;
            const remaining = Math.max(0, data.duration - elapsed);
            const mins = Math.floor(remaining / 60);
            const secs = Math.floor(remaining % 60);
            document.getElementById('time-remaining').textContent = 
                `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            
            // Actualizar tabla de mercado
            const tbody = document.getElementById('market-table-body');
            tbody.innerHTML = '';
            
            data.companies.forEach(comp => {
                const prevPrice = comp.history.length > 1 ? comp.history[comp.history.length - 2] : comp.price;
                const priceChange = comp.price - prevPrice;
                const priceClass = priceChange >= 0 ? 'price-up' : 'price-down';
                const priceIcon = priceChange >= 0 ? '↑' : '↓';
                
                const playerStocks = humanPlayer ? humanPlayer.stocks[comp.id] || 0 : 0;
                const canBuy = humanPlayer && humanPlayer.capital >= comp.price && comp.shares_available > 0;
                const canSell = humanPlayer && playerStocks > 0;
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${comp.name}</strong></td>
                    <td><span class="sector-badge" style="background: ${getSectorColor(comp.sector)}">${comp.sector}</span></td>
                    <td class="${priceClass}">$${comp.price.toFixed(2)} ${priceIcon}</td>
                    <td>${playerStocks} acciones</td>
                    <td>
                        <button class="action-btn ${canBuy ? 'btn-buy' : 'btn-disabled'}" 
                                onclick="openTradeModal('buy', '${comp.id}', '${comp.name}', ${comp.price})"
                                ${!canBuy ? 'disabled' : ''}>Comprar</button>
                        <button class="action-btn ${canSell ? 'btn-sell' : 'btn-disabled'}" 
                                onclick="openTradeModal('sell', '${comp.id}', '${comp.name}', ${comp.price})"
                                ${!canSell ? 'disabled' : ''}>Vender</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            
            // Actualizar ranking
            const rankingList = document.getElementById('ranking-list');
            rankingList.innerHTML = '';
            
            const sortedPlayers = [...data.players].sort((a, b) => {
                const aValue = a.capital + Object.entries(a.stocks).reduce((sum, [id, qty]) => {
                    const comp = data.companies.find(c => c.id === id);
                    return sum + (qty * (comp ? comp.price : 0));
                }, 0);
                const bValue = b.capital + Object.entries(b.stocks).reduce((sum, [id, qty]) => {
                    const comp = data.companies.find(c => c.id === id);
                    return sum + (qty * (comp ? comp.price : 0));
                }, 0);
                return bValue - aValue;
            });
            
            sortedPlayers.forEach((player, idx) => {
                const stockValue = Object.entries(player.stocks).reduce((sum, [id, qty]) => {
                    const comp = data.companies.find(c => c.id === id);
                    return sum + (qty * (comp ? comp.price : 0));
                }, 0);
                const totalValue = player.capital + stockValue;
                
                const li = document.createElement('li');
                li.className = 'ranking-item';
                li.innerHTML = `
                    <span>${idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : ''} ${player.name} ${player.is_bot ? '(Bot)' : ''}</span>
                    <span>$${totalValue.toLocaleString(undefined, {maximumFractionDigits: 0})}</span>
                `;
                rankingList.appendChild(li);
            });
            
            // Actualizar log
            const logContainer = document.getElementById('game-log');
            logContainer.innerHTML = '';
            data.logs.slice(-20).forEach(log => {
                const div = document.createElement('div');
                div.className = 'log-entry';
                if (log.includes('EVENTO')) div.classList.add('log-event');
                if (log.includes('Turno')) div.classList.add('log-turn');
                div.textContent = log;
                logContainer.appendChild(div);
            });
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Actualizar gráfico
            updateChart(data);
        }
        
        // Obtener color de sector
        function getSectorColor(sector) {
            const colors = {
                'Tecnología': '#3b82f6', 'Energía': '#eab308', 'Turismo': '#ec4899',
                'Finanzas': '#10b981', 'Salud': '#ef4444', 'Inmobiliario': '#8b5cf6',
                'Consumo': '#f97316', 'Industrial': '#64748b'
            };
            return colors[sector] || '#64748b';
        }
        
        // Actualizar gráfico
        function updateChart(data) {
            const ctx = document.getElementById('market-chart').getContext('2d');
            
            if (marketChart) {
                marketChart.destroy();
            }
            
            // Tomar las últimas 20 rondas de datos
            const labels = Array.from({length: Math.min(20, data.turn)}, (_, i) => i + 1);
            
            const datasets = data.companies.slice(0, 5).map(comp => ({
                label: comp.name,
                data: comp.history.slice(-20),
                borderColor: getSectorColor(comp.sector),
                backgroundColor: getSectorColor(comp.sector) + '20',
                tension: 0.4,
                fill: false
            }));
            
            marketChart = new Chart(ctx, {
                type: 'line',
                data: { labels: labels, datasets: datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#f8fafc' } }
                    },
                    scales: {
                        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                    }
                }
            });
        }
        
        // Siguiente turno
        function nextTurn() {
            fetch('/api/next_turn', {method: 'POST'})
                .then(res => res.json())
                .then(data => {
                    if (!data.success) alert('Error: ' + data.error);
                })
                .catch(err => console.error(err));
        }
        
        // Abrir modal de comercio
        function openTradeModal(action, compId, compName, price) {
            tradeAction = action;
            selectedCompany = compId;
            
            const modal = document.getElementById('trade-modal');
            const title = document.getElementById('trade-title');
            const info = document.getElementById('trade-info');
            const btn = document.getElementById('confirm-trade-btn');
            
            title.textContent = action === 'buy' ? 'Comprar Acciones' : 'Vender Acciones';
            info.textContent = `${compName} - Precio: $${price.toFixed(2)} por acción`;
            
            btn.textContent = action === 'buy' ? 'Comprar' : 'Vender';
            btn.className = 'btn-primary ' + (action === 'buy' ? 'btn-buy' : 'btn-sell');
            
            btn.onclick = confirmTrade;
            
            modal.style.display = 'flex';
        }
        
        // Cerrar modal
        function closeTradeModal() {
            document.getElementById('trade-modal').style.display = 'none';
        }
        
        // Confirmar comercio
        function confirmTrade() {
            const qty = parseInt(document.getElementById('trade-qty').value);
            if (!qty || qty < 1) {
                alert('Cantidad inválida');
                return;
            }
            
            fetch('/api/trade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    action: tradeAction,
                    company_id: selectedCompany,
                    quantity: qty
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    closeTradeModal();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                console.error(err);
                alert('Error de conexión');
            });
        }
        
        // Enter en el input de nombre
        document.getElementById('player-name-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') confirmName();
        });
        
        // Enter en el input de cantidad
        document.getElementById('trade-qty').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') confirmTrade();
        });
    </script>
</body>
</html>
'''

# ==========================================
# RUTAS DE LA API
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/start', methods=['POST'])
def api_start():
    try:
        data = request.get_json()
        mode = data.get('mode', 'standard')
        player_name = data.get('player_name', 'Jugador 1')
        
        if mode not in ['quick', 'standard', 'extended']:
            return jsonify({'success': False, 'error': 'Modo inválido'}), 400
        
        game = init_game(mode, player_name)
        
        socketio.emit('game_started', {
            'success': True,
            'game_id': game['game_id'],
            'mode': game['mode'],
            'players': game['players'],
            'companies': game['companies'],
            'turn': game['turn'],
            'logs': game['logs'],
            'start_time': game['start_time'],
            'duration': game['duration']
        })
        
        return jsonify({'success': True, 'game_id': game['game_id']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trade', methods=['POST'])
def api_trade():
    try:
        if not game_state['active']:
            return jsonify({'success': False, 'error': 'No hay juego activo'}), 400
        
        data = request.get_json()
        action = data.get('action')
        company_id = data.get('company_id')
        quantity = int(data.get('quantity', 1))
        
        if action not in ['buy', 'sell']:
            return jsonify({'success': False, 'error': 'Acción inválida'}), 400
        
        player = game_state['players'][0]  # Jugador humano
        company = next((c for c in game_state['companies'] if c['id'] == company_id), None)
        
        if not company:
            return jsonify({'success': False, 'error': 'Empresa no encontrada'}), 400
        
        if action == 'buy':
            cost = quantity * company['price']
            if player['capital'] < cost:
                return jsonify({'success': False, 'error': 'Capital insuficiente'}), 400
            if company['shares_available'] < quantity:
                return jsonify({'success': False, 'error': 'No hay suficientes acciones disponibles'}), 400
            
            player['capital'] -= cost
            player['stocks'][company_id] += quantity
            company['shares_available'] -= quantity
            company['price'] *= 1.01  # Impacto de mercado
            log_message(f"{player['name']} compró {quantity} acciones de {company['name']} a ${company['price']:.2f}")
        
        elif action == 'sell':
            if player['stocks'].get(company_id, 0) < quantity:
                return jsonify({'success': False, 'error': 'No tienes suficientes acciones'}), 400
            
            revenue = quantity * company['price']
            player['capital'] += revenue
            player['stocks'][company_id] -= quantity
            company['shares_available'] += quantity
            company['price'] *= 0.99  # Impacto de mercado
            log_message(f"{player['name']} vendió {quantity} acciones de {company['name']} a ${company['price']:.2f}")
        
        # Emitir actualización
        socketio.emit('game_update', get_game_state())
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/next_turn', methods=['POST'])
def api_next_turn():
    try:
        if not game_state['active']:
            return jsonify({'success': False, 'error': 'No hay juego activo'}), 400
        
        game_state['turn'] += 1
        log_message(f"--- Turno {game_state['turn']} ---")
        
        # Actualizar mercado
        update_market()
        
        # Trigger eventos aleatorios
        trigger_random_event()
        
        # Turnos de bots
        for player in game_state['players'][1:]:
            if player['is_bot']:
                bot_action(player)
        
        # Verificar fin del juego
        check_game_over()
        
        # Emitir actualización
        socketio.emit('game_update', get_game_state())
        
        if not game_state['active']:
            # Calcular ganador
            scores = []
            for player in game_state['players']:
                stock_value = sum(player['stocks'].get(c['id'], 0) * c['price'] for c in game_state['companies'])
                total_value = player['capital'] + stock_value
                scores.append({'name': player['name'], 'value': total_value})
            
            scores.sort(key=lambda x: x['value'], reverse=True)
            winner = scores[0]
            
            socketio.emit('game_over', {
                'message': f"Ganador: {winner['name']} con ${winner['value']:,.2f}"
            })
        
        return jsonify({'success': True, 'turn': game_state['turn']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_game_state():
    """Retorna el estado actual del juego"""
    return {
        'active': game_state['active'],
        'game_id': game_state['game_id'],
        'players': game_state['players'],
        'companies': game_state['companies'],
        'turn': game_state['turn'],
        'logs': game_state['logs'],
        'mode': game_state['mode'],
        'start_time': game_state['start_time'],
        'duration': game_state['duration']
    }

# ==========================================
# SOCKET.IO EVENTS
# ==========================================

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    print("🚀 Iniciando Stock Market Tycoon...")
    print("🌐 Abre tu navegador en: http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
