import os
import sys
import time
import random
import threading
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit

# ==========================================
# CONFIGURACIÓN DEL JUEGO
# ==========================================
SECTORES = [
    {"nombre": "Tecnología", "color": "#3b82f6", "volatilidad": 0.15},
    {"nombre": "Energía", "color": "#eab308", "volatilidad": 0.10},
    {"nombre": "Finanzas", "color": "#10b981", "volatilidad": 0.05},
    {"nombre": "Salud", "color": "#ef4444", "volatilidad": 0.08},
    {"nombre": "Consumo", "color": "#f97316", "volatilidad": 0.06},
    {"nombre": "Industrial", "color": "#6366f1", "volatilidad": 0.07},
    {"nombre": "Inmobiliario", "color": "#8b5cf6", "volatilidad": 0.09},
    {"nombre": "Materiales", "color": "#14b8a6", "volatilidad": 0.11}
]

EMPRESAS_INIT = [
    {"nombre": "TechGiant", "sector": 0, "precio": 100},
    {"nombre": "NanoChip", "sector": 0, "precio": 45},
    {"nombre": "OilCorp", "sector": 1, "precio": 80},
    {"nombre": "GreenPower", "sector": 1, "precio": 60},
    {"nombre": "BankGlobal", "sector": 2, "precio": 120},
    {"nombre": "InsureCo", "sector": 2, "precio": 55},
    {"nombre": "PharmaLife", "sector": 3, "precio": 90},
    {"nombre": "BioGen", "sector": 3, "precio": 35},
    {"nombre": "FoodMart", "sector": 4, "precio": 70},
    {"nombre": "LuxuryBrand", "sector": 4, "precio": 150},
    {"nombre": "AutoMotive", "sector": 5, "precio": 85},
    {"nombre": "SteelWorks", "sector": 5, "precio": 40},
    {"nombre": "BuildIt", "sector": 6, "precio": 65},
    {"nombre": "EstatePro", "sector": 6, "precio": 110},
    {"nombre": "MineCorp", "sector": 7, "precio": 50},
    {"nombre": "ChemicalX", "sector": 7, "precio": 75}
]

EVENTOS_MERCADO = [
    {"texto": "Crisis Tecnológica: Las tech caen un 20%", "sector_afectado": 0, "modificador": -0.20},
    {"texto": "Boom Energético: La energía sube un 15%", "sector_afectado": 1, "modificador": 0.15},
    {"texto": "Regulación Bancaria: Finanzas caen un 10%", "sector_afectado": 2, "modificador": -0.10},
    {"texto": "Nueva Vacuna: Salud sube un 25%", "sector_afectado": 3, "modificador": 0.25},
    {"texto": "Inflación Global: Todos los sectores bajan un 5%", "sector_afectado": -1, "modificador": -0.05},
    {"texto": "Innovación Industrial: Industrial sube un 12%", "sector_afectado": 5, "modificador": 0.12},
]

def aplicar_evento(empresas, evento):
    sector = evento['sector_afectado']
    mod = evento['modificador']
    
    for emp in empresas:
        if sector == -1 or emp['sector'] == sector:
            emp['precio'] = max(1, emp['precio'] * (1 + mod))

# ==========================================
# LÓGICA DEL JUEGO (BACKEND)
# ==========================================
class StockMarketGame:
    def __init__(self, modo='rapida'):
        self.modo = modo
        self.jugadores = []
        self.empresas = []
        self.ronda = 1
        self.turno_actual = 0
        self.estado = "esperando"
        self.tiempo_por_turno = 30
        self.historico_precios = {i: [e['precio']] for i, e in enumerate(EMPRESAS_INIT)}
        self.eventos_ocurridos = []
        self.sid_mapping = {} # Mapeo SID -> jugador_id
        
        if modo == 'rapida':
            self.max_rondas = 10
            self.tiempo_por_turno = 20
        elif modo == 'estandar':
            self.max_rondas = 20
            self.tiempo_por_turno = 30
        else:
            self.max_rondas = 40
            self.tiempo_por_turno = 45

        for i, e in enumerate(EMPRESAS_INIT):
            self.empresas.append({
                "id": i,
                "nombre": e['nombre'],
                "sector": e['sector'],
                "precio": e['precio'],
                "accionistas": {}
            })

    def add_jugador(self, nombre, es_bot=False, sid=None):
        jugador_id = len(self.jugadores)
        self.jugadores.append({
            "id": jugador_id,
            "nombre": nombre,
            "dinero": 5000,
            "acciones": {},
            "es_bot": es_bot,
            "banca_rota": False
        })
        if sid:
            self.sid_mapping[sid] = jugador_id
        return jugador_id

    def iniciar_partida(self):
        self.estado = "jugando"
        self.ronda = 1
        self.turno_actual = 0
        return self.get_estado_completo()

    def get_estado_completo(self):
        return {
            "ronda": self.ronda,
            "turno_actual": self.turno_actual,
            "max_rondas": self.max_rondas,
            "tiempo_turno": self.tiempo_por_turno,
            "jugadores": self.jugadores,
            "empresas": self.empresas,
            "sectores": SECTORES,
            "historico": self.historico_precios,
            "ultimo_evento": self.eventos_ocurridos[-1] if self.eventos_ocurridos else None,
            "estado": self.estado
        }

    def siguiente_turno(self):
        if self.estado != "jugando":
            return self.get_estado_completo()

        self.turno_actual += 1
        if self.turno_actual >= len(self.jugadores):
            self.turno_actual = 0
            self.ronda += 1
            self.procesar_evento_mercado()
            
            if self.ronda > self.max_rondas:
                self.finalizar_partida()
                return self.get_estado_completo()

        jugador_sig = self.jugadores[self.turno_actual]
        if jugador_sig['es_bot'] and not jugador_sig['banca_rota']:
            threading.Timer(1.5, self.ejecutar_turno_bot, args=[jugador_sig]).start()
        elif jugador_sig['banca_rota']:
            threading.Timer(0.5, self.siguiente_turno).start()

        return self.get_estado_completo()

    def ejecutar_turno_bot(self, bot):
        accion = random.choice(['comprar', 'vender', 'esperar'])
        
        if accion == 'comprar' and bot['dinero'] > 100:
            empresa_obj = random.choice(self.empresas)
            if bot['dinero'] >= empresa_obj['precio']:
                self.comprar_accion(bot['id'], empresa_obj['id'], 1)
        elif accion == 'vender':
            if bot['acciones']:
                emp_id = random.choice(list(bot['acciones'].keys()))
                if bot['acciones'][emp_id] > 0:
                    self.vender_accion(bot['id'], emp_id, 1)
        
        self.siguiente_turno()

    def comprar_accion(self, jugador_id, empresa_id, cantidad):
        jugador = self.jugadores[jugador_id]
        empresa = self.empresas[empresa_id]
        costo = empresa['precio'] * cantidad

        if jugador['dinero'] >= costo:
            jugador['dinero'] -= costo
            jugador['acciones'][empresa_id] = jugador['acciones'].get(empresa_id, 0) + cantidad
            empresa['accionistas'][str(jugador_id)] = empresa['accionistas'].get(str(jugador_id), 0) + cantidad
            empresa['precio'] *= 1.02
            self.actualizar_historico(empresa_id, empresa['precio'])
            return True
        return False

    def vender_accion(self, jugador_id, empresa_id, cantidad):
        jugador = self.jugadores[jugador_id]
        empresa = self.empresas[empresa_id]
        
        if jugador['acciones'].get(empresa_id, 0) >= cantidad:
            ganancia = empresa['precio'] * cantidad
            jugador['dinero'] += ganancia
            jugador['acciones'][empresa_id] -= cantidad
            if jugador['acciones'][empresa_id] == 0:
                del jugador['acciones'][empresa_id]
            
            empresa['accionistas'][str(jugador_id)] -= cantidad
            if str(jugador_id) in empresa['accionistas'] and empresa['accionistas'][str(jugador_id)] == 0:
                del empresa['accionistas'][str(jugador_id)]

            empresa['precio'] *= 0.98
            self.actualizar_historico(empresa_id, empresa['precio'])
            return True
        return False

    def actualizar_historico(self, empresa_id, nuevo_precio):
        if empresa_id not in self.historico_precios:
            self.historico_precios[empresa_id] = []
        historial = self.historico_precios[empresa_id]
        historial.append(nuevo_precio)
        if len(historial) > 20:
            historial.pop(0)

    def procesar_evento_mercado(self):
        if random.random() < 0.4:
            evento = random.choice(EVENTOS_MERCADO)
            aplicar_evento(self.empresas, evento)
            self.eventos_ocurridos.append(evento['texto'])
            for emp in self.empresas:
                self.actualizar_historico(emp['id'], emp['precio'])

    def finalizar_partida(self):
        self.estado = "terminado"
        for j in self.jugadores:
            valor_acciones = sum(self.empresas[eid]['precio'] * cant for eid, cant in j['acciones'].items())
            j['puntuacion_final'] = j['dinero'] + valor_acciones
        self.jugadores.sort(key=lambda x: x.get('puntuacion_final', 0), reverse=True)

# ==========================================
# INTERFAZ WEB (HTML/CSS/JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Market Tycoon</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --bg: #0f172a; --panel: #1e293b; --text: #f1f5f9; --accent: #3b82f6; --danger: #ef4444; --success: #10b981; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; overflow-x: hidden; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #334155; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 250px 1fr 300px; gap: 20px; }
        .panel { background: var(--panel); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        .btn { background: var(--accent); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; width: 100%; margin-top: 10px; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .btn-danger { background: var(--danger); }
        .btn-success { background: var(--success); }
        .btn:disabled { background: #475569; cursor: not-allowed; transform: none; }
        .timer-box { text-align: center; font-size: 2.5rem; font-weight: bold; color: var(--accent); margin: 10px 0; }
        .timer-warning { color: var(--danger); animation: pulse 1s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .list-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155; font-size: 0.9rem; }
        .list-item:last-child { border-bottom: none; }
        .sector-badge { padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; color: #000; font-weight: bold; }
        #login-screen, #game-screen { display: none; }
        .active { display: block !important; }
        .chart-container { position: relative; height: 200px; width: 100%; margin-top: 10px; }
        #news-ticker { background: #334155; padding: 10px; text-align: center; border-radius: 8px; margin-bottom: 15px; font-style: italic; color: #fbbf24; }
    </style>
</head>
<body>

<div class="container">
    <div id="login-screen" class="active" style="text-align: center; margin-top: 100px;">
        <h1 style="font-size: 3rem; margin-bottom: 10px;">📈 Stock Market Tycoon</h1>
        <p style="color: #94a3b8; margin-bottom: 40px;">Simulador de Mercado Bursátil Competitivo</p>
        <div class="panel" style="max-width: 400px; margin: 0 auto; text-align: left;">
            <label>Nombre del Jugador:</label>
            <input type="text" id="player-name" value="Inversionista 1" style="width: 100%; padding: 10px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 6px;">
            <label>Modo de Juego:</label>
            <select id="game-mode" style="width: 100%; padding: 10px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 6px;">
                <option value="rapida">Rápida (15 min, 10 Rondas)</option>
                <option value="estandar">Estándar (45 min, 20 Rondas)</option>
                <option value="extendida">Extendida (90 min, 40 Rondas)</option>
            </select>
            <button class="btn" onclick="iniciarJuego()">Crear / Unirse a Partida</button>
        </div>
    </div>

    <div id="game-screen">
        <header>
            <div>
                <h2 style="margin:0;">📈 Stock Market Tycoon</h2>
                <span id="round-display" style="color: #94a3b8;">Ronda 1 / 10</span>
            </div>
            <div style="text-align: right;">
                <div id="turn-indicator">Turno: Jugador 1</div>
                <div id="timer" class="timer-box">30</div>
            </div>
        </header>

        <div id="news-ticker">Esperando inicio de partida...</div>

        <div class="grid">
            <div class="panel">
                <h3>👥 Jugadores</h3>
                <div id="players-list"></div>
            </div>

            <div class="panel">
                <h3>🏢 Mercado de Valores</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px;" id="market-grid"></div>
                <div style="margin-top: 20px; border-top: 1px solid #334155; pt: 20px;">
                    <h3>📊 Análisis Técnico</h3>
                    <select id="chart-selector" onchange="updateChart()" style="width: 100%; padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 4px;"></select>
                    <div class="chart-container"><canvas id="priceChart"></canvas></div>
                </div>
            </div>

            <div class="panel">
                <h3>💼 Mi Cartera</h3>
                <div style="font-size: 1.2rem; margin-bottom: 15px;">Dinero: <span id="my-money" style="color: var(--success); font-weight: bold;">$5000</span></div>
                <div id="my-portfolios"></div>
                <hr style="border-color: #334155; margin: 20px 0;">
                <h3>⚡ Acciones Rápidas</h3>
                <div style="display: grid; gap: 10px;">
                    <button id="btn-skip" class="btn btn-danger" onclick="saltarTurno()">Saltar Turno</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    const socket = io();
    let miId = null;
    let juegoActivo = false;
    let timerLocal = null;
    let tiempoRestante = 30;
    let chartInstance = null;

    function iniciarJuego() {
        const nombre = document.getElementById('player-name').value;
        const modo = document.getElementById('game-mode').value;
        socket.emit('crear_partida', { nombre, modo });
    }

    socket.on('partida_creada', (data) => {
        miId = data.jugador_id;
        document.getElementById('login-screen').classList.remove('active');
        document.getElementById('game-screen').classList.add('active');
        juegoActivo = true;
    });

    socket.on('actualizar_estado', (estado) => {
        actualizarUI(estado);
        if (estado.estado === 'jugando') {
            reiniciarTemporizador(estado.tiempo_turno);
        } else {
            clearInterval(timerLocal);
            document.getElementById('timer').innerText = "--";
        }
    });

    socket.on('fin_partida', (resultado) => {
        clearInterval(timerLocal);
        alert("¡Partida Terminada! Ganador: " + (resultado.ganador || 'Desconocido'));
        location.reload();
    });

    // TEMPORIZADOR INDEPENDIENTE PERO SINCRONIZADO
    function reiniciarTemporizador(segundos) {
        clearInterval(timerLocal);
        tiempoRestante = segundos;
        actualizarVisualizacionTimer();

        timerLocal = setInterval(() => {
            tiempoRestante--;
            actualizarVisualizacionTimer();

            if (tiempoRestante <= 0) {
                clearInterval(timerLocal);
                if (juegoActivo) saltarTurno();
            }
        }, 1000);
    }

    function actualizarVisualizacionTimer() {
        const timerEl = document.getElementById('timer');
        timerEl.innerText = tiempoRestante;
        if (tiempoRestante <= 5) timerEl.classList.add('timer-warning');
        else timerEl.classList.remove('timer-warning');
    }

    function actualizarUI(estado) {
        document.getElementById('round-display').innerText = `Ronda ${estado.ronda} / ${estado.max_rondas}`;
        const jugadorActual = estado.jugadores[estado.turno_actual];
        const turnEl = document.getElementById('turn-indicator');
        turnEl.innerText = `Turno: ${jugadorActual.nombre} ${jugadorActual.es_bot ? '(BOT)' : ''}`;
        turnEl.style.color = jugadorActual.id === miId ? '#10b981' : '#f1f5f9';

        if (estado.ultimo_evento) document.getElementById('news-ticker').innerText = "📰 NOTICIA: " + estado.ultimo_evento;

        const playersList = document.getElementById('players-list');
        playersList.innerHTML = '';
        estado.jugadores.forEach((j) => {
            const valAcciones = Object.keys(j.acciones).reduce((acc, key) => {
                const emp = estado.empresas.find(e => e.id == key);
                return acc + (emp ? emp.precio * j.acciones[key] : 0);
            }, 0);
            const total = j.dinero + valAcciones;
            playersList.innerHTML += `
                <div class="list-item" style="${j.id === miId ? 'background:#334155; padding:5px; border-radius:4px;' : ''}">
                    <div><strong>${j.nombre}</strong> ${j.es_bot ? '🤖' : ''}<div style="font-size:0.8rem; color:#94a3b8;">Patrimonio: $${Math.floor(total)}</div></div>
                    <div style="text-align:right;"><div style="color:var(--success);">$${Math.floor(j.dinero)}</div></div>
                </div>`;
        });

        const marketGrid = document.getElementById('market-grid');
        const chartSelect = document.getElementById('chart-selector');
        const selectedChart = chartSelect.value;
        marketGrid.innerHTML = '';
        chartSelect.innerHTML = '<option value="0">Seleccionar Empresa...</option>';

        estado.empresas.forEach((emp) => {
            const sector = estado.sectores[emp.sector];
            const misAcciones = (estado.jugadores[miId]?.acciones || {})[emp.id] || 0;
            marketGrid.innerHTML += `
                <div class="panel" style="padding:10px; text-align:center;">
                    <div style="font-weight:bold; margin-bottom:5px;">${emp.nombre}</div>
                    <span class="sector-badge" style="background:${sector.color}">${sector.nombre}</span>
                    <div style="font-size:1.4rem; font-weight:bold; margin:10px 0;">$${Math.floor(emp.precio)}</div>
                    <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">Tus acciones: ${misAcciones}</div>
                    ${estado.turno_actual === miId ? `
                        <button class="btn btn-success" style="font-size:0.8rem; padding:5px;" onclick="operar('comprar', ${emp.id})">Comprar</button>
                        <button class="btn btn-danger" style="font-size:0.8rem; padding:5px;" onclick="operar('vender', ${emp.id})">Vender</button>
                    ` : '<div style="font-size:0.8rem; color:#64748b;">Espera tu turno</div>'}
                </div>`;
            chartSelect.innerHTML += `<option value="${emp.id}">${emp.nombre}</option>`;
        });

        if (selectedChart) chartSelect.value = selectedChart;
        else if (estado.empresas.length > 0) chartSelect.value = estado.empresas[0].id;
        updateChart(estado);

        const myPortfolio = document.getElementById('my-portfolios');
        const miJugador = estado.jugadores[miId];
        myPortfolio.innerHTML = '';
        if (miJugador && miJugador.acciones) {
            Object.entries(miJugador.acciones).forEach(([eid, cant]) => {
                if (cant > 0) {
                    const emp = estado.empresas.find(e => e.id == eid);
                    if (emp) myPortfolio.innerHTML += `<div class="list-item"><span>${emp.nombre} (x${cant})</span><span>$${Math.floor(emp.precio * cant)}</span></div>`;
                }
            });
            if (Object.keys(miJugador.acciones).length === 0) myPortfolio.innerHTML = '<div style="color:#64748b; text-align:center;">No tienes acciones</div>';
        }
        document.getElementById('my-money').innerText = `$${Math.floor(miJugador?.dinero || 0)}`;
        document.getElementById('btn-skip').disabled = (estado.turno_actual !== miId);
    }

    function operar(tipo, empresaId) {
        if (!juegoActivo) return;
        socket.emit('accion_jugador', { tipo, empresaId, cantidad: 1, jugador_id: miId });
    }

    function saltarTurno() {
        if (!juegoActivo) return;
        socket.emit('saltar_turno');
    }

    function updateChart(estadoGlobal = null) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        const empId = parseInt(document.getElementById('chart-selector').value);
        if (!estadoGlobal) return;

        const historial = estadoGlobal.historico[empId] || [];
        const labels = historial.map((_, i) => i + 1);
        const empresa = estadoGlobal.empresas.find(e => e.id === empId);
        const color = empresa ? estadoGlobal.sectores[empresa.sector].color : '#3b82f6';

        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Historial: ${empresa ? empresa.nombre : ''}`,
                    data: historial,
                    borderColor: color,
                    backgroundColor: color + '20',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }
</script>
</body>
</html>
"""

# ==========================================
# SERVIDOR FLASK + SOCKET.IO
# ==========================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secreto_super_seguro_bolsa'
socketio = SocketIO(app, cors_allowed_origins="*")

game_instance = None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def connect():
    print(f"Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def disconnect():
    print(f"Cliente desconectado: {request.sid}")

@socketio.on('crear_partida')
def crear_partida(data):
    global game_instance
    nombre = data.get('nombre', 'Jugador')
    modo = data.get('modo', 'rapida')
    sid = request.sid
    
    if game_instance is None:
        game_instance = StockMarketGame(modo=modo)
        gid = game_instance.add_jugador(nombre, es_bot=False, sid=sid)
        game_instance.add_jugador("Bot Conservador", es_bot=True)
        game_instance.add_jugador("Bot Arriesgado", es_bot=True)
        game_instance.iniciar_partida()
        emit('partida_creada', {'jugador_id': gid})
        socketio.emit('actualizar_estado', game_instance.get_estado_completo())
    else:
        emit('error', {'msg': 'Ya hay una partida en curso. Recarga la página.'})

@socketio.on('accion_jugador')
def accion_jugador(data):
    global game_instance
    if not game_instance or game_instance.estado != 'jugando':
        return
    
    jugador_id = data.get('jugador_id')
    if jugador_id is None or jugador_id != game_instance.turno_actual:
        return # Solo el jugador actual puede actuar

    tipo = data.get('tipo')
    emp_id = data.get('empresaId')
    
    if tipo == 'comprar':
        game_instance.comprar_accion(jugador_id, emp_id, 1)
    elif tipo == 'vender':
        game_instance.vender_accion(jugador_id, emp_id, 1)
    
    socketio.emit('actualizar_estado', game_instance.get_estado_completo())

@socketio.on('saltar_turno')
def saltar_turno():
    global game_instance
    if game_instance and game_instance.estado == 'jugando':
        estado = game_instance.siguiente_turno()
        socketio.emit('actualizar_estado', estado)
        if estado['estado'] == 'terminado':
            socketio.emit('fin_partida', {'ganador': estado['jugadores'][0]['nombre']})

if __name__ == '__main__':
    print("🚀 Iniciando Stock Market Tycoon...")
    print("🌐 Abre tu navegador en: http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
