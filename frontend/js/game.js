// Variables Globales
let socket = null;
let playerId = null;
let currentRoom = null;
let gameState = null;
let boardScene = null;
let boardCamera = null;
let boardRenderer = null;
let companyMeshes = [];
let currentBoardRotation = 0;
let timerInterval = null;

// Colores por sector
const SECTOR_COLORS = {
    'Tecnología': 0x00d9ff,
    'Energía': 0xffaa00,
    'Turismo': 0x28a745,
    'Finanzas': 0x6f42c1,
    'Salud': 0xdc3545,
    'Inmobiliario': 0xfd7e14,
    'Consumo': 0xe83e8c,
    'Industrial': 0x6c757d
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
});

function initSocket() {
    socket = io.connect(window.location.origin);
    
    socket.on('connect', () => {
        console.log('Conectado al servidor');
        playerId = socket.id;
    });
    
    socket.on('room_created', (data) => {
        currentRoom = data.room_code;
        playerId = data.player_id;
        showLobby(data.room_code, data.players, true);
    });
    
    socket.on('room_joined', (data) => {
        currentRoom = data.room_code;
        playerId = data.player_id;
        showLobby(data.room_code, data.players, false);
    });
    
    socket.on('game_started', (data) => {
        hideAllScreens();
        document.getElementById('game-screen').classList.add('active');
        gameState = data.state;
        initBoard3D();
        updateGameUI(data.state);
        startTimer(data.time_left);
        logMessage('¡La partida ha comenzado!', true);
    });
    
    socket.on('game_update', (data) => {
        if (data.state) {
            gameState = data.state;
            updateGameUI(data.state);
        }
        if (data.last_action) {
            logMessage(data.last_action);
        }
        if (data.notification) {
            showModal('Notificación', data.notification);
        }
    });
    
    socket.on('turn_change', (data) => {
        updateTurnIndicator(data.active_player, data.round);
        startTimer(data.time_left);
    });
    
    socket.on('action_result', (data) => {
        if (!data.success) {
            showModal('Error', data.message);
        } else {
            logMessage(data.message);
        }
    });
    
    socket.on('game_over', (data) => {
        stopTimer();
        showEndScreen(data.scores);
    });
    
    socket.on('board_rotated', (data) => {
        // Solo para vista individual
        if (boardCamera) {
            const angle = data.rotation * Math.PI / 180;
            boardCamera.position.x = Math.sin(angle) * 50;
            boardCamera.position.z = Math.cos(angle) * 50;
            boardCamera.lookAt(0, 0, 0);
        }
    });
    
    socket.on('error', (data) => {
        showModal('Error', data.message);
    });
}

// Navegación entre pantallas
function hideAllScreens() {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
}

function goHome() {
    hideAllScreens();
    document.getElementById('start-screen').classList.add('active');
}

function showModeSelection() {
    hideAllScreens();
    document.getElementById('mode-screen').classList.add('active');
}

function showLocalSetup() {
    hideAllScreens();
    document.getElementById('local-setup-screen').classList.add('active');
}

function showMultiplayerOptions() {
    hideAllScreens();
    document.getElementById('multiplayer-screen').classList.add('active');
}

function showCreateRoom() {
    hideAllScreens();
    document.getElementById('create-room-screen').classList.add('active');
}

function showJoinRoom() {
    hideAllScreens();
    document.getElementById('join-room-screen').classList.add('active');
}

// Crear/Unirse a partida
function startLocalGame() {
    const name = document.getElementById('local-player-name').value || 'Jugador 1';
    const bots = parseInt(document.getElementById('local-bot-count').value);
    const rounds = parseInt(document.getElementById('local-rounds').value);
    const turnTime = parseInt(document.getElementById('local-turn-time').value);
    
    socket.emit('create_game', {
        mode: 'local',
        name: name,
        bots: bots,
        config: {
            max_rounds: rounds,
            turn_time: turnTime,
            events_enabled: true,
            trade_enabled: true
        }
    });
}

function createRoom() {
    const name = document.getElementById('create-player-name').value || 'Jugador 1';
    const rounds = parseInt(document.getElementById('create-rounds').value);
    const turnTime = parseInt(document.getElementById('create-turn-time').value);
    const events = document.getElementById('create-events').checked;
    const trading = document.getElementById('create-trading').checked;
    
    socket.emit('create_game', {
        mode: 'online',
        name: name,
        config: {
            max_rounds: rounds,
            turn_time: turnTime,
            events_enabled: events,
            trade_enabled: trading
        }
    });
}

function joinRoom() {
    const name = document.getElementById('join-player-name').value || 'Jugador 1';
    const roomCode = document.getElementById('join-room-code').value.trim().toUpperCase();
    
    if (!roomCode) {
        showModal('Error', 'Ingresa un código de sala válido');
        return;
    }
    
    socket.emit('join_game', {
        room_code: roomCode,
        name: name
    });
}

// Lobby
function showLobby(roomCode, players, isHost) {
    hideAllScreens();
    document.getElementById('lobby-screen').classList.add('active');
    document.getElementById('lobby-room-code').textContent = roomCode;
    
    const playersList = document.getElementById('lobby-players-list');
    playersList.innerHTML = '';
    players.forEach(p => {
        const li = document.createElement('li');
        li.textContent = p.name + (p.is_bot ? ' 🤖' : '');
        playersList.appendChild(li);
    });
    
    if (isHost) {
        document.getElementById('host-controls').style.display = 'block';
        document.getElementById('waiting-message').style.display = 'none';
    } else {
        document.getElementById('host-controls').style.display = 'none';
        document.getElementById('waiting-message').style.display = 'block';
    }
}

function startGame() {
    if (currentRoom) {
        socket.emit('start_game', { room_code: currentRoom });
    }
}

// Tablero 3D con Three.js
function initBoard3D() {
    const container = document.getElementById('board-container');
    container.innerHTML = '';
    
    // Escena
    boardScene = new THREE.Scene();
    boardScene.background = new THREE.Color(0x0f0f1a);
    
    // Cámara
    boardCamera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    boardCamera.position.set(0, 40, 50);
    boardCamera.lookAt(0, 0, 0);
    
    // Renderer
    boardRenderer = new THREE.WebGLRenderer({ antialias: true });
    boardRenderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(boardRenderer.domElement);
    
    // Luces
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    boardScene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    boardScene.add(directionalLight);
    
    // Base del tablero
    const baseGeometry = new THREE.CylinderGeometry(25, 25, 2, 32);
    const baseMaterial = new THREE.MeshPhongMaterial({ color: 0x1a1a2e, transparent: true, opacity: 0.8 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    boardScene.add(base);
    
    // Crear empresas como torres en el tablero
    companyMeshes = [];
    if (gameState && gameState.companies) {
        Object.values(gameState.companies).forEach((company, index) => {
            const angle = (index / Object.keys(gameState.companies).length) * Math.PI * 2;
            const radius = 15;
            const x = Math.cos(angle) * radius;
            const z = Math.sin(angle) * radius;
            
            // Altura basada en el precio
            const height = Math.max(2, company.price / 20);
            
            const geometry = new THREE.BoxGeometry(2, height, 2);
            const color = SECTOR_COLORS[company.sector] || 0xffffff;
            const material = new THREE.MeshPhongMaterial({ color: color });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(x, height / 2, z);
            mesh.userData = { companyId: company.id, name: company.name };
            
            boardScene.add(mesh);
            companyMeshes.push(mesh);
        });
    }
    
    // Animación
    animateBoard();
}

function animateBoard() {
    requestAnimationFrame(animateBoard);
    if (boardRenderer && boardScene && boardCamera) {
        boardRenderer.render(boardScene, boardCamera);
    }
}

function rotateBoard(delta) {
    currentBoardRotation += delta;
    if (boardCamera) {
        const angle = currentBoardRotation * Math.PI / 180;
        boardCamera.position.x = Math.sin(angle) * 50;
        boardCamera.position.z = Math.cos(angle) * 50;
        boardCamera.lookAt(0, 0, 0);
    }
    if (currentRoom) {
        socket.emit('update_board_rotation', {
            room_code: currentRoom,
            rotation: currentBoardRotation
        });
    }
}

function resetRotation() {
    currentBoardRotation = 0;
    rotateBoard(0);
}

// UI del Juego
function updateGameUI(state) {
    if (!state) return;
    
    // Actualizar ronda
    document.getElementById('game-round').textContent = `Ronda: ${state.round}`;
    
    // Actualizar ranking
    updateRanking(state.players);
    
    // Actualizar stats del jugador
    const myPlayer = state.players.find(p => p.id === playerId);
    if (myPlayer) {
        document.getElementById('player-cash').textContent = `$${myPlayer.cash.toLocaleString()}`;
        document.getElementById('player-total').textContent = `$${myPlayer.total_value.toLocaleString()}`;
        
        // Actualizar contenido de pestañas
        if (document.querySelector('.tab-btn.active')) {
            const activeTab = document.querySelector('.tab-btn.active').textContent.toLowerCase();
            switchTab(activeTab === 'comprar' ? 'buy' : 
                     activeTab === 'vender' ? 'sell' : 
                     activeTab === 'cartas' ? 'cards' : 'trade');
        }
    }
    
    // Actualizar indicador de turno
    updateTurnIndicator(state.active_player, state.round);
}

function updateTurnIndicator(activePlayerId, round) {
    if (!gameState) return;
    const player = gameState.players.find(p => p.id === activePlayerId);
    const name = player ? player.name : 'Desconocido';
    const isMyTurn = activePlayerId === playerId;
    
    const indicator = document.getElementById('current-player-name');
    indicator.textContent = name;
    indicator.style.color = isMyTurn ? '#28a745' : '#00d9ff';
    
    if (isMyTurn) {
        logMessage('¡Es tu turno!', true);
    }
}

function updateRanking(players) {
    const sorted = [...players].sort((a, b) => b.total_value - a.total_value);
    const container = document.getElementById('ranking-list');
    container.innerHTML = '';
    
    sorted.forEach((player, index) => {
        const div = document.createElement('div');
        div.className = 'rank-item';
        div.innerHTML = `
            <span class="rank-position">${index + 1}</span>
            <span class="rank-name">${player.name}${player.is_bot ? ' 🤖' : ''}</span>
            <span class="rank-value">$${player.total_value.toLocaleString()}</span>
        `;
        container.appendChild(div);
    });
}

// Pestañas de acción
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    const content = document.getElementById('action-content');
    content.innerHTML = '';
    
    if (!gameState || !gameState.companies) return;
    
    if (tab === 'buy') {
        renderBuySellTab(content, 'buy');
    } else if (tab === 'sell') {
        renderBuySellTab(content, 'sell');
    } else if (tab === 'cards') {
        renderCardsTab(content);
    } else if (tab === 'trade') {
        renderTradeTab(content);
    }
}

function renderBuySellTab(container, actionType) {
    const companies = Object.values(gameState.companies);
    const myPlayer = gameState.players.find(p => p.id === playerId);
    
    const list = document.createElement('div');
    list.className = 'company-list';
    
    companies.forEach(company => {
        const canAfford = myPlayer.cash >= company.price;
        const ownsShares = myPlayer.portfolio && myPlayer.portfolio[company.id] > 0;
        
        if ((actionType === 'buy' && !canAfford) || (actionType === 'sell' && !ownsShares)) {
            return;
        }
        
        const item = document.createElement('div');
        item.className = 'company-item' + (company.disaster ? ' disaster' : '');
        item.innerHTML = `
            <div class="company-info">
                <h4>${company.name}</h4>
                <div class="company-sector">${company.sector}</div>
            </div>
            <div class="company-price">
                <div class="price-value">$${Math.round(company.price)}</div>
                ${actionType === 'buy' ? `<div>Disponibles: ${company.available}</div>` : 
                  `<div>Tus acciones: ${myPlayer.portfolio[company.id] || 0}</div>`}
            </div>
            <div class="action-controls">
                <input type="number" min="1" max="${actionType === 'buy' ? company.available : (myPlayer.portfolio[company.id] || 1)}" value="1" id="qty-${company.id}">
                <button class="btn btn-small btn-primary" onclick="executeAction('${actionType}', ${company.id})">
                    ${actionType === 'buy' ? 'Comprar' : 'Vender'}
                </button>
            </div>
        `;
        list.appendChild(item);
    });
    
    container.appendChild(list);
}

function executeAction(actionType, companyId) {
    const qtyInput = document.getElementById(`qty-${companyId}`);
    const quantity = parseInt(qtyInput.value) || 1;
    
    socket.emit('player_action', {
        room_code: currentRoom,
        action_type: actionType,
        action_data: {
            company_id: companyId,
            quantity: quantity
        }
    });
}

function renderCardsTab(container) {
    const myPlayer = gameState.players.find(p => p.id === playerId);
    
    if (!myPlayer.hand || myPlayer.hand.length === 0) {
        container.innerHTML = '<p style="color: #aaa; text-align: center;">No tienes cartas</p>';
        return;
    }
    
    const list = document.createElement('div');
    list.className = 'company-list';
    
    myPlayer.hand.forEach((card, index) => {
        const item = document.createElement('div');
        item.className = 'company-item';
        item.innerHTML = `
            <div class="company-info">
                <h4>${card.name}</h4>
                <div class="company-sector">Tipo: ${card.type}</div>
            </div>
            <button class="btn btn-small btn-primary" onclick="executeAction('play_card', ${index})">
                Usar
            </button>
        `;
        list.appendChild(item);
    });
    
    container.appendChild(list);
}

function renderTradeTab(container) {
    const otherPlayers = gameState.players.filter(p => p.id !== playerId && !p.is_bot);
    
    if (otherPlayers.length === 0) {
        container.innerHTML = '<p style="color: #aaa; text-align: center;">No hay otros jugadores humanos para intercambiar</p>';
        return;
    }
    
    const list = document.createElement('div');
    list.className = 'company-list';
    
    otherPlayers.forEach(player => {
        const item = document.createElement('div');
        item.className = 'company-item';
        item.innerHTML = `
            <div class="company-info">
                <h4>${player.name}</h4>
                <div class="company-sector">Valor: $${player.total_value.toLocaleString()}</div>
            </div>
            <button class="btn btn-small btn-secondary" onclick="openTradeModal('${player.id}')">
                Ofrecer Intercambio
            </button>
        `;
        list.appendChild(item);
    });
    
    container.appendChild(list);
    
    // Mostrar ofertas pendientes
    if (gameState.trade_offers && gameState.trade_offers.length > 0) {
        const offersDiv = document.createElement('div');
        offersDiv.style.marginTop = '20px';
        offersDiv.innerHTML = '<h4 style="color: #00d9ff; margin-bottom: 10px;">Ofertas Recibidas:</h4>';
        
        gameState.trade_offers.forEach(offer => {
            const offerDiv = document.createElement('div');
            offerDiv.className = 'company-item';
            offerDiv.innerHTML = `
                <div class="company-info">
                    <h4>De: ${gameState.players.find(p => p.id === offer.from)?.name}</h4>
                </div>
                <div>
                    <button class="btn btn-small btn-success" onclick="resolveTrade('${offer.id}', true)">Aceptar</button>
                    <button class="btn btn-small btn-danger" onclick="resolveTrade('${offer.id}', false)">Rechazar</button>
                </div>
            `;
            offersDiv.appendChild(offerDiv);
        });
        
        container.appendChild(offersDiv);
    }
}

function openTradeModal(playerId) {
    // Simplificado para demo
    showModal('Intercambio', 'Funcionalidad de intercambio detallado en desarrollo. Selecciona acciones y dinero para ofrecer.');
}

function resolveTrade(tradeId, accept) {
    socket.emit('resolve_trade', {
        room_code: currentRoom,
        trade_id: tradeId,
        accept: accept
    });
}

// Temporizador
function startTimer(seconds) {
    stopTimer();
    const timerEl = document.getElementById('game-timer');
    
    let remaining = seconds;
    updateTimerDisplay(remaining);
    
    timerInterval = setInterval(() => {
        remaining--;
        updateTimerDisplay(remaining);
        
        if (remaining <= 0) {
            stopTimer();
        }
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimerDisplay(seconds) {
    const timerEl = document.getElementById('game-timer');
    timerEl.textContent = `${seconds}s`;
    
    if (seconds <= 10) {
        timerEl.style.color = '#ff6b6b';
    } else if (seconds <= 30) {
        timerEl.style.color = '#ffaa00';
    } else {
        timerEl.style.color = '#28a745';
    }
}

// Utilidades
function logMessage(message, important = false) {
    const log = document.getElementById('game-log');
    const entry = document.createElement('div');
    entry.className = 'log-entry' + (important ? ' important' : '');
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    log.insertBefore(entry, log.firstChild);
    
    // Limitar historial
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

function showModal(title, message) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = `<p>${message}</p>`;
    document.getElementById('notification-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('notification-modal').classList.remove('active');
}

function closeTradeModal() {
    document.getElementById('trade-modal').classList.remove('active');
}

function acceptTrade() {
    // Implementar aceptación
    closeTradeModal();
}

function rejectTrade() {
    // Implementar rechazo
    closeTradeModal();
}

// Pantalla final
function showEndScreen(scores) {
    hideAllScreens();
    document.getElementById('end-screen').classList.add('active');
    
    const container = document.getElementById('final-ranking');
    container.innerHTML = '<h3 style="margin-bottom: 20px; color: #00d9ff;">Clasificación Final</h3>';
    
    scores.forEach((score, index) => {
        const div = document.createElement('div');
        div.className = 'rank-item';
        div.style.padding = '15px';
        div.style.marginBottom = '10px';
        div.innerHTML = `
            <span class="rank-position" style="font-size: 1.5rem;">${index + 1}</span>
            <span class="rank-name" style="font-size: 1.2rem;">${score.name}</span>
            <span class="rank-value" style="font-size: 1.2rem; color: #00d9ff;">$${score.value.toLocaleString()}</span>
        `;
        container.appendChild(div);
    });
}

// Manejo de redimensionamiento
window.addEventListener('resize', () => {
    if (boardCamera && boardRenderer) {
        const container = document.getElementById('board-container');
        boardCamera.aspect = container.clientWidth / container.clientHeight;
        boardCamera.updateProjectionMatrix();
        boardRenderer.setSize(container.clientWidth, container.clientHeight);
    }
});
