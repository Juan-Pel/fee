// Stock Market Tycoon - JavaScript para la interfaz web

// Estado global del juego
let gameState = {
    playerId: null,
    playerName: 'Jugador 1',
    gameMode: 'standard',
    botCount: 2,
    companies: {},
    sectors: {},
    portfolio: {},
    players: {},
    currentRound: 0,
    currentPlayer: null,
    isMyTurn: false
};

// Conexión WebSocket
let socket = io();

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    setupSocketListeners();
    loadInitialData();
});

// Configurar listeners de Socket.IO
function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('Conectado al servidor');
        showNotification('¡Conectado al servidor!', 'success');
    });

    socket.on('player_added', (data) => {
        console.log('Jugador añadido:', data);
        updateLeaderboard();
    });

    socket.on('shares_bought', (data) => {
        console.log('Acciones compradas:', data);
        refreshGameData();
        if (data.player_id === gameState.playerId) {
            showNotification(`Compraste ${data.quantity} acciones de ${data.company_id} por $${data.cost.toFixed(2)}`, 'success');
        }
    });

    socket.on('shares_sold', (data) => {
        console.log('Acciones vendidas:', data);
        refreshGameData();
        if (data.player_id === gameState.playerId) {
            showNotification(`Vendiste ${data.quantity} acciones de ${data.company_id} por $${data.value.toFixed(2)}`, 'success');
        }
    });

    socket.on('companies_merged', (data) => {
        console.log('Empresas fusionadas:', data);
        refreshGameData();
        showNotification('¡Fusión completada!', 'success');
    });

    socket.on('card_played', (data) => {
        console.log('Carta jugada:', data);
        refreshGameData();
    });

    socket.on('turn_changed', (data) => {
        console.log('Cambio de turno:', data);
        gameState.currentRound = data.round;
        gameState.currentPlayer = data.current_player;
        gameState.isMyTurn = (data.current_player === gameState.playerId);
        
        updateTurnDisplay();
        refreshGameData();
        
        if (gameState.isMyTurn) {
            showNotification('¡Es tu turno!', 'info');
            document.getElementById('btn-next-turn').disabled = false;
        } else {
            document.getElementById('btn-next-turn').disabled = true;
        }
    });

    socket.on('ai_turn', (data) => {
        console.log('Turno de IA:', data);
        showNotification(`Turno de ${data.player_id} (IA)`, 'info');
    });

    socket.on('ai_action', (data) => {
        console.log('Acción de IA:', data);
        if (data.action === 'buy') {
            showNotification(`${data.player_id} compró ${data.quantity} acciones de ${data.company_id}`, 'info');
        }
    });
}

// Cargar datos iniciales
async function loadInitialData() {
    try {
        // Los datos se cargarán cuando se inicie el juego
    } catch (error) {
        console.error('Error cargando datos:', error);
    }
}

// Ajustar número de bots
function adjustBots(delta) {
    const botCountEl = document.getElementById('bot-count');
    let count = parseInt(botCountEl.textContent);
    count = Math.max(1, Math.min(7, count + delta));
    botCountEl.textContent = count;
    gameState.botCount = count;
}

// Iniciar nueva partida
async function startGame() {
    const playerName = document.getElementById('player-name').value.trim();
    const gameMode = document.getElementById('game-mode').value;
    
    if (!playerName) {
        showNotification('Por favor, introduce tu nombre', 'error');
        return;
    }

    gameState.playerName = playerName;
    gameState.gameMode = gameMode;
    gameState.playerId = `player_${Date.now()}`;

    try {
        // Crear nueva partida
        const response = await fetch('/api/game/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: gameMode })
        });

        const result = await response.json();
        
        if (result.success) {
            // Añadir jugador humano
            await addPlayer(gameState.playerId, playerName, false);
            
            // Añadir bots
            for (let i = 0; i < gameState.botCount; i++) {
                await addPlayer(`bot_${i}`, `Bot ${i + 1}`, true);
            }

            // Cambiar a pantalla de juego
            document.getElementById('setup-screen').classList.remove('active');
            document.getElementById('game-screen').classList.add('active');

            // Cargar datos del juego
            await refreshGameData();
            
            showNotification('¡Partida iniciada!', 'success');
        } else {
            showNotification('Error al crear partida: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Añadir jugador
async function addPlayer(playerId, name, isAi) {
    try {
        const response = await fetch('/api/player/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: playerId, name, is_ai: isAi })
        });

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error añadiendo jugador:', error);
    }
}

// Refrescar todos los datos del juego
async function refreshGameData() {
    await loadCompanies();
    await loadSectors();
    await loadPlayerData();
    await loadLeaderboard();
    await loadEvents();
    updateTradeForm();
    updatePortfolio();
}

// Cargar empresas
async function loadCompanies() {
    try {
        const response = await fetch('/api/market/companies');
        gameState.companies = await response.json();
        renderSectors();
    } catch (error) {
        console.error('Error cargando empresas:', error);
    }
}

// Cargar sectores
async function loadSectors() {
    try {
        const response = await fetch('/api/market/sectors');
        gameState.sectors = await response.json();
    } catch (error) {
        console.error('Error cargando sectores:', error);
    }
}

// Cargar datos del jugador
async function loadPlayerData() {
    try {
        const response = await fetch(`/api/player/${gameState.playerId}`);
        if (response.ok) {
            const data = await response.json();
            gameState.portfolio = data.shares || {};
            updatePlayerStats(data);
        }
    } catch (error) {
        console.error('Error cargando datos del jugador:', error);
    }
}

// Cargar clasificación
async function loadLeaderboard() {
    try {
        const response = await fetch('/api/game/leaderboard');
        if (response.ok) {
            const leaderboard = await response.json();
            renderLeaderboard(leaderboard);
        }
    } catch (error) {
        console.error('Error cargando clasificación:', error);
    }
}

// Cargar eventos
async function loadEvents() {
    try {
        const response = await fetch('/api/events/current');
        if (response.ok) {
            const events = await response.json();
            renderEvents(events);
        }
    } catch (error) {
        console.error('Error cargando eventos:', error);
    }
}

// Renderizar sectores y empresas
function renderSectors() {
    const container = document.getElementById('sectors-container');
    container.innerHTML = '';

    // Agrupar empresas por sector
    const sectorCompanies = {};
    for (const [companyId, company] of Object.entries(gameState.companies)) {
        const sectorName = company.sector;
        if (!sectorCompanies[sectorName]) {
            sectorCompanies[sectorName] = [];
        }
        sectorCompanies[sectorName].push({ id: companyId, ...company });
    }

    // Renderizar cada sector
    for (const [sectorName, companies] of Object.entries(sectorCompanies)) {
        const sectorCard = document.createElement('div');
        sectorCard.className = 'sector-card';
        
        const trend = getSectorTrend(companies);
        
        sectorCard.innerHTML = `
            <div class="sector-header">
                <span class="sector-name">${getSectorIcon(sectorName)} ${sectorName}</span>
                <span class="sector-trend ${trend.class}">${trend.text}</span>
            </div>
            <div class="company-list">
                ${companies.map(company => renderCompanyItem(company)).join('')}
            </div>
        `;
        
        container.appendChild(sectorCard);
    }
}

// Obtener tendencia del sector
function getSectorTrend(companies) {
    const avgChange = companies.reduce((sum, c) => sum + (c.price_change || 0), 0) / companies.length;
    if (avgChange > 2) return { class: 'up', text: '▲ Alcista' };
    if (avgChange < -2) return { class: 'down', text: '▼ Bajista' };
    return { class: 'neutral', text: '● Estable' };
}

// Icono de sector
function getSectorIcon(sectorName) {
    const icons = {
        'Tecnología': '💻',
        'Energía': '⚡',
        'Turismo': '✈️',
        'Finanzas': '🏦',
        'Salud': '🏥',
        'Inmobiliario': '🏢',
        'Consumo': '🛒',
        'Industrial': '🏭'
    };
    return icons[sectorName] || '📊';
}

// Renderizar item de empresa
function renderCompanyItem(company) {
    const changeClass = company.price_change >= 0 ? 'positive' : 'negative';
    const changeSign = company.price_change >= 0 ? '+' : '';
    
    return `
        <div class="company-item" onclick="selectCompany('${company.company_id}')">
            <div class="company-info">
                <div class="company-name">${company.name}</div>
                <div class="company-price">${company.sector}</div>
            </div>
            <div class="company-stock-info">
                <div class="stock-price">$${company.current_price.toFixed(2)}</div>
                <div class="stock-change ${changeClass}">${changeSign}${company.price_change.toFixed(2)}%</div>
            </div>
        </div>
    `;
}

// Seleccionar empresa para operar
function selectCompany(companyId) {
    document.querySelectorAll('.company-item').forEach(el => el.classList.remove('selected'));
    event.target.closest('.company-item').classList.add('selected');
    
    document.getElementById('trade-company').value = companyId;
    updateTradeInfo();
}

// Actualizar formulario de operaciones
function updateTradeForm() {
    const select = document.getElementById('trade-company');
    select.innerHTML = '<option value="">Seleccionar...</option>';
    
    for (const [companyId, company] of Object.entries(gameState.companies)) {
        select.innerHTML += `<option value="${companyId}">${company.name} - $${company.current_price.toFixed(2)}</option>`;
    }

    // Actualizar selects de fusión
    const mergeSelect1 = document.getElementById('merge-company1');
    const mergeSelect2 = document.getElementById('merge-company2');
    mergeSelect1.innerHTML = '<option value="">Empresa 1...</option>';
    mergeSelect2.innerHTML = '<option value="">Empresa 2...</option>';
    
    for (const [companyId, company] of Object.entries(gameState.companies)) {
        mergeSelect1.innerHTML += `<option value="${companyId}">${company.name} (${company.sector})</option>`;
        mergeSelect2.innerHTML += `<option value="${companyId}">${company.name} (${company.sector})</option>`;
    }
}

// Actualizar información de operación
function updateTradeInfo() {
    const companyId = document.getElementById('trade-company').value;
    const quantity = parseInt(document.getElementById('trade-quantity').value) || 1;
    
    if (companyId && gameState.companies[companyId]) {
        const price = gameState.companies[companyId].current_price;
        const total = price * quantity;
        
        document.getElementById('trade-price').textContent = `$${price.toFixed(2)}`;
        document.getElementById('trade-total').textContent = `$${total.toFixed(2)}`;
    } else {
        document.getElementById('trade-price').textContent = '$0';
        document.getElementById('trade-total').textContent = '$0';
    }
}

// Comprar acciones
async function buyShares() {
    const companyId = document.getElementById('trade-company').value;
    const quantity = parseInt(document.getElementById('trade-quantity').value) || 1;
    
    if (!companyId) {
        showNotification('Selecciona una empresa', 'error');
        return;
    }

    try {
        const response = await fetch('/api/action/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: gameState.playerId,
                company_id: companyId,
                quantity: quantity
            })
        });

        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            await refreshGameData();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Error comprando acciones:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Vender acciones
async function sellShares() {
    const companyId = document.getElementById('trade-company').value;
    const quantity = parseInt(document.getElementById('trade-quantity').value) || 1;
    
    if (!companyId) {
        showNotification('Selecciona una empresa', 'error');
        return;
    }

    try {
        const response = await fetch('/api/action/sell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: gameState.playerId,
                company_id: companyId,
                quantity: quantity
            })
        });

        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            await refreshGameData();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Error vendiendo acciones:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Fusionar empresas
async function mergeCompanies() {
    const company1 = document.getElementById('merge-company1').value;
    const company2 = document.getElementById('merge-company2').value;
    
    if (!company1 || !company2) {
        showNotification('Selecciona dos empresas', 'error');
        return;
    }

    if (company1 === company2) {
        showNotification('Las empresas deben ser diferentes', 'error');
        return;
    }

    try {
        const response = await fetch('/api/action/merge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: gameState.playerId,
                company1_id: company1,
                company2_id: company2
            })
        });

        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            await refreshGameData();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Error fusionando empresas:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Pasar turno
async function nextTurn() {
    if (!gameState.isMyTurn) {
        showNotification('No es tu turno', 'error');
        return;
    }

    try {
        const response = await fetch('/api/turn/next', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: gameState.playerId })
        });

        const result = await response.json();
        
        if (result.success) {
            gameState.isMyTurn = false;
            document.getElementById('btn-next-turn').disabled = true;
        }
    } catch (error) {
        console.error('Error pasando turno:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Actualizar estadísticas del jugador
function updatePlayerStats(data) {
    document.getElementById('player-cash').textContent = `$${data.cash.toFixed(2)}`;
    document.getElementById('player-net-worth').textContent = `$${data.net_worth.toFixed(2)}`;
    document.getElementById('player-influence').textContent = data.influence_points || 0;
    document.getElementById('player-companies').textContent = (data.companies_owned || []).length;
    
    // Actualizar cartas
    const cardsContainer = document.getElementById('cards-container');
    cardsContainer.innerHTML = '';
    
    if (data.cards && data.cards.length > 0) {
        data.cards.forEach(cardId => {
            const cardEl = document.createElement('div');
            cardEl.className = 'card-item';
            cardEl.textContent = getCardName(cardId);
            cardEl.onclick = () => playCard(cardId);
            cardsContainer.appendChild(cardEl);
        });
    } else {
        cardsContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem;">Sin cartas</p>';
    }
}

// Obtener nombre de carta
function getCardName(cardId) {
    const names = {
        'discount': '🎫 Descuento',
        'premium': '💎 Prima',
        'raid': '⚔️ Adquisición',
        'bailout': '🆘 Rescate',
        'insider': '📊 Insider',
        'marketing': '📣 Marketing',
        'lawsuit': '⚖️ Demanda',
        'innovation': '💡 Innovación',
        'strike': '🚼 Huelga',
        'merger_boost': '🤝 Fusión+'
    };
    return names[cardId] || cardId;
}

// Jugar carta
async function playCard(cardId) {
    if (!confirm(`¿Jugar carta ${getCardName(cardId)}?`)) return;

    try {
        const response = await fetch('/api/action/card', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: gameState.playerId,
                card_id: cardId
            })
        });

        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            await refreshGameData();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Error jugando carta:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Actualizar cartera
function updatePortfolio() {
    const container = document.getElementById('portfolio-container');
    container.innerHTML = '';
    
    let hasShares = false;
    
    for (const [companyId, quantity] of Object.entries(gameState.portfolio)) {
        if (quantity > 0 && gameState.companies[companyId]) {
            hasShares = true;
            const company = gameState.companies[companyId];
            const value = company.current_price * quantity;
            
            const itemEl = document.createElement('div');
            itemEl.className = 'portfolio-item';
            itemEl.innerHTML = `
                <div class="portfolio-company">
                    <div style="font-weight: 600;">${company.name}</div>
                    <div class="portfolio-shares">${quantity} acciones</div>
                </div>
                <div class="portfolio-value">$${value.toFixed(2)}</div>
            `;
            
            container.appendChild(itemEl);
        }
    }
    
    if (!hasShares) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Sin acciones en cartera</p>';
    }
}

// Renderizar clasificación
function renderLeaderboard(leaderboard) {
    const container = document.getElementById('leaderboard-container');
    container.innerHTML = '';
    
    leaderboard.sort((a, b) => b.net_worth - a.net_worth);
    
    leaderboard.forEach((player, index) => {
        const itemEl = document.createElement('div');
        itemEl.className = 'leaderboard-item';
        itemEl.innerHTML = `
            <span class="leaderboard-rank">#${index + 1} ${player.name}</span>
            <span>$${player.net_worth.toLocaleString()}</span>
        `;
        container.appendChild(itemEl);
    });
}

// Renderizar eventos
function renderEvents(events) {
    const container = document.getElementById('active-events');
    container.innerHTML = '';
    
    if (events.length === 0) {
        container.innerHTML = '<p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">Sin eventos activos</p>';
        return;
    }
    
    events.forEach(event => {
        const badgeEl = document.createElement('div');
        badgeEl.className = `event-badge ${event.type}`;
        badgeEl.innerHTML = `
            <strong>${event.name}</strong><br>
            <small>${event.description}</small>
        `;
        container.appendChild(badgeEl);
    });
}

// Actualizar display de turno
function updateTurnDisplay() {
    document.getElementById('round-display').textContent = `Ronda: ${gameState.currentRound}`;
    document.getElementById('mode-display').textContent = `Modo: ${getModeName(gameState.gameMode)}`;
    document.getElementById('current-player-display').textContent = `Turno: ${gameState.currentPlayer}`;
    
    if (gameState.isMyTurn) {
        document.getElementById('current-player-display').classList.add('turn-indicator');
    } else {
        document.getElementById('current-player-display').classList.remove('turn-indicator');
    }
}

// Obtener nombre del modo
function getModeName(mode) {
    const names = {
        'quick': 'Rápida',
        'standard': 'Estándar',
        'extended': 'Extendida'
    };
    return names[mode] || mode;
}

// Mostrar notificación
function showNotification(message, type = 'info') {
    const modal = document.getElementById('notification-modal');
    const messageEl = document.getElementById('modal-message');
    
    const colors = {
        'success': '#27ae60',
        'error': '#e74c3c',
        'info': '#3498db'
    };
    
    messageEl.innerHTML = `<div style="color: ${colors[type]}; font-size: 1.2rem; font-weight: 600;">${message}</div>`;
    
    modal.classList.add('active');
    
    setTimeout(() => {
        modal.classList.remove('active');
    }, 2500);
}

// Cerrar modal
function closeModal() {
    document.getElementById('notification-modal').classList.remove('active');
}

// Cerrar modal con click fuera
window.onclick = function(event) {
    const modal = document.getElementById('notification-modal');
    if (event.target === modal) {
        modal.classList.remove('active');
    }
}
