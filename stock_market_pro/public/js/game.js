// Stock Market Tycoon - Cliente JavaScript
let socket = null;
let currentRoom = null;
let gameState = null;
let selectedCompany = null;
let localTimer = null;

// Elementos del DOM
const screens = {
    start: document.getElementById('start-screen'),
    localConfig: document.getElementById('local-config-screen'),
    online: document.getElementById('online-screen'),
    lobby: document.getElementById('lobby-screen'),
    game: document.getElementById('game-screen'),
    gameOver: document.getElementById('game-over-screen')
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Navegación entre pantallas
    document.getElementById('btn-local').addEventListener('click', () => showScreen('localConfig'));
    document.getElementById('btn-online').addEventListener('click', () => showScreen('online'));
    document.getElementById('btn-back-local').addEventListener('click', () => showScreen('start'));
    document.getElementById('btn-back-online').addEventListener('click', () => showScreen('start'));
    
    // Partida Local
    document.getElementById('btn-start-local').addEventListener('click', startLocalGame);
    
    // Multijugador
    document.getElementById('btn-create-room').addEventListener('click', createRoom);
    document.getElementById('btn-join-room').addEventListener('click', joinRoom);
    document.getElementById('btn-start-game').addEventListener('click', startGame);
    document.getElementById('btn-copy-code').addEventListener('click', copyRoomCode);
    
    // Juego
    document.getElementById('btn-buy').addEventListener('click', buyShares);
    document.getElementById('btn-sell').addEventListener('click', sellShares);
    document.getElementById('btn-next-turn').addEventListener('click', nextTurn);
    document.getElementById('btn-new-game').addEventListener('click', () => location.reload());
    
    // Selección de empresa para trading
    document.getElementById('trade-company-select').addEventListener('change', (e) => {
        selectedCompany = e.target.value;
    });
}

function showScreen(screenName) {
    Object.values(screens).forEach(screen => screen.classList.remove('active'));
    screens[screenName].classList.add('active');
}

// Conectar al servidor Socket.IO
function connectSocket() {
    if (socket) socket.disconnect();
    
    socket = io();
    
    socket.on('connect', () => {
        console.log('Conectado al servidor');
    });
    
    socket.on('room_created', (data) => {
        currentRoom = data.room_id;
        document.getElementById('lobby-room-code').textContent = data.room_id;
        updateLobbyPlayers(data.players);
        showScreen('lobby');
    });
    
    socket.on('room_joined', (data) => {
        currentRoom = data.room_id;
        document.getElementById('lobby-room-code').textContent = data.room_id;
        updateLobbyPlayers(data.players);
        showScreen('lobby');
    });
    
    socket.on('game_started', (state) => {
        gameState = state;
        initializeGame(state);
        showScreen('game');
    });
    
    socket.on('game_state_update', (state) => {
        gameState = state;
        updateGameUI(state);
        
        if (state.game_over) {
            showGameOver(state);
        }
    });
    
    socket.on('error', (data) => {
        alert(data.message);
    });
    
    socket.on('player_left', (data) => {
        console.log('Jugador se fue:', data.player_id);
    });
}

// Partida Local (simulada con bots)
function startLocalGame() {
    const name = document.getElementById('local-player-name').value || 'Jugador 1';
    const rounds = parseInt(document.getElementById('local-rounds').value);
    const turnTime = parseInt(document.getElementById('local-turn-time').value);
    const enableEvents = document.getElementById('local-events').checked;
    
    connectSocket();
    
    // Crear sala local
    socket.emit('create_room', {
        name: name,
        config: {
            max_turns: rounds,
            turn_duration: turnTime,
            enable_events: enableEvents
        }
    });
    
    // Auto-iniciar cuando esté lista la sala
    setTimeout(() => {
        if (currentRoom) {
            socket.emit('start_game', { room_id: currentRoom });
        }
    }, 500);
}

// Crear sala online
function createRoom() {
    const name = prompt('Ingresa tu nombre:');
    if (!name) return;
    
    const rounds = prompt('Rondas (10-40):', '20');
    const turnTime = prompt('Tiempo por turno (30-90 seg):', '60');
    
    connectSocket();
    
    socket.emit('create_room', {
        name: name,
        config: {
            max_turns: parseInt(rounds) || 20,
            turn_duration: parseInt(turnTime) || 60,
            enable_events: true
        }
    });
}

// Unirse a sala
function joinRoom() {
    const code = document.getElementById('room-code-input').value.trim().toUpperCase();
    if (!code) {
        alert('Ingresa un código de sala');
        return;
    }
    
    const name = prompt('Ingresa tu nombre:');
    if (!name) return;
    
    connectSocket();
    
    socket.emit('join_room', {
        room_id: code,
        name: name
    });
}

// Iniciar juego desde lobby
function startGame() {
    if (!currentRoom) return;
    socket.emit('start_game', { room_id: currentRoom });
}

// Copiar código de sala
function copyRoomCode() {
    if (!currentRoom) return;
    
    navigator.clipboard.writeText(currentRoom).then(() => {
        alert('Código copiado: ' + currentRoom);
    });
}

// Actualizar lista de jugadores en lobby
function updateLobbyPlayers(players) {
    const container = document.getElementById('lobby-players');
    container.innerHTML = players.map(p => `
        <div class="player-item">
            <span>${p.is_bot ? '🤖' : '👤'} ${p.name}</span>
            <span>${p.is_bot ? 'Bot' : 'Humano'}</span>
        </div>
    `).join('');
}

// Inicializar juego
function initializeGame(state) {
    updateGameUI(state);
    startTimer(state.turn_timer);
}

// Iniciar temporizador local
function startTimer(seconds) {
    if (localTimer) clearInterval(localTimer);
    
    let timeLeft = seconds;
    const timerElement = document.getElementById('turn-timer');
    
    timerElement.textContent = timeLeft;
    timerElement.classList.remove('warning');
    
    localTimer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        
        if (timeLeft <= 10) {
            timerElement.classList.add('warning');
        }
        
        if (timeLeft <= 0) {
            clearInterval(localTimer);
        }
    }, 1000);
}

// Actualizar interfaz del juego
function updateGameUI(state) {
    if (!state) return;
    
    // Actualizar información de turno
    document.getElementById('current-round').textContent = state.current_round;
    document.getElementById('max-rounds').textContent = state.max_turns;
    
    const currentPlayer = state.players.find(p => p.id === state.current_turn);
    if (currentPlayer) {
        document.getElementById('current-player-display').textContent = 
            `Turno: ${currentPlayer.name}`;
    }
    
    // Actualizar temporizador si cambió
    if (state.turn_timer !== undefined) {
        const timerElement = document.getElementById('turn-timer');
        if (parseInt(timerElement.textContent) !== state.turn_timer) {
            startTimer(state.turn_timer);
        }
    }
    
    // Actualizar ranking
    updateRanking(state.players);
    
    // Actualizar empresas
    updateCompanies(state.companies);
    
    // Actualizar portfolio del jugador actual
    updatePortfolio(state);
    
    // Actualizar eventos
    updateEvents(state.events);
}

// Actualizar ranking
function updateRanking(players) {
    const container = document.getElementById('players-ranking');
    container.innerHTML = players.map((p, index) => `
        <div class="rank-item" style="${index === 0 ? 'border-left: 3px solid #ffd700;' : ''}">
            <span>#${index + 1} ${p.name} ${p.is_bot ? '🤖' : ''}</span>
            <span>$${Math.round(p.market_value).toLocaleString()}</span>
        </div>
    `).join('');
}

// Actualizar grid de empresas
function updateCompanies(companies) {
    const container = document.getElementById('companies-grid');
    const select = document.getElementById('trade-company-select');
    
    container.innerHTML = companies.map(company => `
        <div class="company-card ${selectedCompany === company.id ? 'selected' : ''}" 
             onclick="selectCompany('${company.id}')">
            <div class="company-name">${company.name}</div>
            <div class="company-sector">${company.sector}</div>
            <div class="company-price">$${company.price.toFixed(2)}</div>
            <div class="company-trend ${company.trend}">
                ${company.trend === 'up' ? '↑' : company.trend === 'down' ? '↓' : '→'}
            </div>
            <div style="font-size: 0.8rem; color: #a0a0a0; margin-top: 5px;">
                Disponibles: ${company.available_shares}
            </div>
        </div>
    `).join('');
    
    // Actualizar select
    const currentValue = select.value;
    select.innerHTML = '<option value="">Seleccionar empresa...</option>' + 
        companies.map(c => `<option value="${c.id}">${c.name} - $${c.price.toFixed(2)}</option>`).join('');
    
    if (currentValue && companies.find(c => c.id === currentValue)) {
        select.value = currentValue;
    }
}

// Seleccionar empresa para trading
function selectCompany(companyId) {
    selectedCompany = companyId;
    document.getElementById('trade-company-select').value = companyId;
    updateCompanies(gameState.companies);
}

// Actualizar portfolio
function updatePortfolio(state) {
    const currentPlayer = state.players[0]; // Asumimos que el primer jugador es el humano
    const container = document.getElementById('my-portfolio');
    
    if (!currentPlayer || Object.keys(currentPlayer.portfolio).length === 0) {
        container.innerHTML = '<p style="color: #a0a0a0;">No tienes acciones</p>';
        return;
    }
    
    const portfolioItems = Object.entries(currentPlayer.portfolio).map(([companyId, quantity]) => {
        const company = state.companies.find(c => c.id === companyId);
        const value = company ? company.price * quantity : 0;
        return `
            <div class="portfolio-item">
                <span>${company ? company.name : 'Desconocida'} x${quantity}</span>
                <span>$${value.toFixed(2)}</span>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <div style="margin-bottom: 10px; font-weight: bold;">
            Capital: $${currentPlayer.capital.toFixed(2)}
        </div>
        ${portfolioItems}
    `;
}

// Actualizar eventos
function updateEvents(events) {
    const container = document.getElementById('events-list');
    container.innerHTML = events.slice().reverse().map(event => {
        let icon = 'ℹ️';
        if (event.type === 'event') icon = '⚡';
        if (event.type === 'action') icon = '💼';
        if (event.type === 'bot') icon = '🤖';
        
        return `<div class="event-item ${event.type}">${icon} ${event.message}</div>`;
    }).join('');
}

// Acciones de trading
function buyShares() {
    if (!selectedCompany || !currentRoom) {
        alert('Selecciona una empresa primero');
        return;
    }
    
    const quantity = parseInt(document.getElementById('trade-quantity').value);
    if (quantity < 1) {
        alert('Cantidad inválida');
        return;
    }
    
    socket.emit('buy_shares', {
        room_id: currentRoom,
        company_id: selectedCompany,
        quantity: quantity
    });
}

function sellShares() {
    if (!selectedCompany || !currentRoom) {
        alert('Selecciona una empresa primero');
        return;
    }
    
    const quantity = parseInt(document.getElementById('trade-quantity').value);
    if (quantity < 1) {
        alert('Cantidad inválida');
        return;
    }
    
    socket.emit('sell_shares', {
        room_id: currentRoom,
        company_id: selectedCompany,
        quantity: quantity
    });
}

function nextTurn() {
    if (!currentRoom) return;
    
    socket.emit('next_turn', { room_id: currentRoom });
}

// Mostrar fin del juego
function showGameOver(state) {
    if (localTimer) clearInterval(localTimer);
    
    const winner = state.winner;
    document.getElementById('winner-display').innerHTML = `
        🏆 Ganador: ${winner.name}<br>
        <span style="font-size: 1.2rem; color: #a0a0a0;">Valor: $${Math.round(winner.market_value).toLocaleString()}</span>
    `;
    
    updateRanking(state.players);
    document.getElementById('final-ranking').innerHTML = document.getElementById('players-ranking').innerHTML;
    
    showScreen('gameOver');
}

// Función global para seleccionar empresa desde HTML
window.selectCompany = selectCompany;
