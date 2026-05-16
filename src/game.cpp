#include "game.h"
#include <iostream>

Game::Game() : state(GameState::WAITING_PLAYERS), currentRound(1), globalTimer(0) {
    settings.mode = GameMode::STANDARD;
    settings.maxPlayers = 4;
    settings.humanPlayers = 1;
    settings.aiPlayers = 3;
    settings.turnTime = 60;
    settings.maxRounds = 20;
    settings.eventsEnabled = true;
    settings.tradingEnabled = true;
    settings.victoryCondition = VictoryCondition::MAGNATE;
    settings.isOnline = false;
    
    currentTurn.currentPlayer = 0;
    currentTurn.timeRemaining = settings.turnTime;
    currentTurn.actionsRemaining = 3;
    currentTurn.canTrade = true;
    currentTurn.canPlayCard = true;
}

Game::~Game() {
    unload();
}

bool Game::initialize() {
    // Inicializar UI
    ui.initialize();
    ui.setMaxTurnTime(settings.turnTime);
    ui.setTurnTimer(settings.turnTime);
    
    // Inicializar mercado
    market.initializeCompanies();
    
    // Inicializar tablero
    board.initialize();
    
    // Agregar jugador humano por defecto
    addHumanPlayer("Jugador 1");
    
    std::cout << "Juego inicializado correctamente" << std::endl;
    return true;
}

void Game::run() {
    while (!WindowShouldClose()) {
        update();
        draw();
    }
}

void Game::update() {
    float dt = GetFrameTime();
    
    // Actualizar UI
    ui.update();
    
    // Manejar estados del juego
    switch (state) {
        case GameState::WAITING_PLAYERS:
            // Manejar menú principal
            handleMenuInput();
            break;
            
        case GameState::SETUP:
            // Manejar configuración
            handleSetupInput();
            break;
            
        case GameState::PLAYING:
            // Actualizar temporizador del turno
            if (currentTurn.timeRemaining > 0) {
                currentTurn.timeRemaining -= dt;
                ui.setTurnTimer(currentTurn.timeRemaining);
                
                // Verificar si el tiempo se agotó
                if (currentTurn.timeRemaining <= 0) {
                    nextTurn();
                }
            }
            
            // Actualizar tablero
            board.update();
            
            // Procesar IA si es turno de un bot
            Player& currentPlayer = playerManager.getCurrentPlayer();
            if (currentPlayer.type != PlayerType::HUMAN && currentTurn.timeRemaining > 0) {
                processAITurn(currentPlayer.id);
            }
            
            // Manejar input del jugador
            handleGameInput();
            break;
            
        case GameState::PAUSED:
            if (IsKeyPressed(KEY_ESCAPE)) {
                resumeGame();
            }
            break;
            
        case GameState::ENDED:
            if (IsKeyPressed(KEY_ENTER)) {
                // Volver al menú
                state = GameState::WAITING_PLAYERS;
                ui.setState(UIState::MENU_MAIN);
            }
            break;
    }
}

void Game::draw() {
    BeginDrawing();
    
    // El UI maneja la mayoría del dibujado
    ui.draw();
    
    // Si estamos jugando, dibujar el tablero 3D
    if (state == GameState::PLAYING) {
        // El UI ya dibuja el HUD, el tablero se dibuja en drawGameHUD
        // a través de board.draw() que es llamado desde allí
    }
    
    EndDrawing();
}

void Game::unload() {
    board.unload();
}

void Game::startGame() {
    // Configurar condición de victoria
    playerManager.setVictoryCondition(settings.victoryCondition);
    
    // Agregar bots si es necesario
    for (int i = 0; i < settings.aiPlayers; i++) {
        PlayerType aiType = PlayerType::AI_BALANCED;
        if (i % 3 == 0) aiType = PlayerType::AI_AGGRESSIVE;
        else if (i % 3 == 1) aiType = PlayerType::AI_CONSERVATIVE;
        
        addAIPlayer(aiType);
    }
    
    state = GameState::PLAYING;
    ui.setState(UIState::PLAYING);
    
    // Inicializar cámaras para cada jugador
    for (size_t i = 0; i < playerManager.getAllPlayers().size(); i++) {
        board.setPlayerCamera(i);
    }
    
    std::cout << "Partida iniciada con " << playerManager.getAllPlayers().size() 
              << " jugadores" << std::endl;
}

void Game::endGame() {
    state = GameState::ENDED;
    determineWinner();
}

void Game::pauseGame() {
    if (state == GameState::PLAYING) {
        state = GameState::PAUSED;
        ui.setState(UIState::PAUSED);
    }
}

void Game::resumeGame() {
    if (state == GameState::PAUSED) {
        state = GameState::PLAYING;
        ui.setState(UIState::PLAYING);
    }
}

void Game::setGameMode(GameMode mode) {
    settings.mode = mode;
    
    switch (mode) {
        case GameMode::QUICK:
            settings.maxRounds = 10;
            settings.turnTime = 30;
            break;
        case GameMode::STANDARD:
            settings.maxRounds = 20;
            settings.turnTime = 60;
            break;
        case GameMode::EXTENDED:
            settings.maxRounds = 40;
            settings.turnTime = 90;
            break;
    }
    
    ui.setMaxTurnTime(settings.turnTime);
}

void Game::setVictoryCondition(VictoryCondition condition) {
    settings.victoryCondition = condition;
}

void Game::setTurnTime(float time) {
    settings.turnTime = time;
    ui.setMaxTurnTime(time);
}

void Game::setMaxRounds(int rounds) {
    settings.maxRounds = rounds;
}

GameSettings& Game::getSettings() {
    return settings;
}

void Game::addHumanPlayer(const std::string& name) {
    playerManager.addPlayer(name, PlayerType::HUMAN);
}

void Game::addAIPlayer(PlayerType type) {
    std::string name = "Bot ";
    name += std::to_string(playerManager.getAllPlayers().size());
    playerManager.addPlayer(name, type);
}

PlayerManager& Game::getPlayerManager() {
    return playerManager;
}

Market& Game::getMarket() {
    return market;
}

Board& Game::getBoard() {
    return board;
}

UI& Game::getUI() {
    return ui;
}

void Game::nextTurn() {
    // Pasar al siguiente jugador
    playerManager.nextTurn();
    
    // Resetear temporizador
    currentTurn.currentPlayer = playerManager.getCurrentPlayerIndex();
    currentTurn.timeRemaining = settings.turnTime;
    currentTurn.actionsRemaining = 3;
    currentTurn.canTrade = true;
    currentTurn.canPlayCard = true;
    
    ui.setTurnTimer(currentTurn.timeRemaining);
    
    // Actualizar cámara para el nuevo jugador
    board.setPlayerCamera(currentTurn.currentPlayer);
    
    // Verificar si terminó la ronda
    if (currentTurn.currentPlayer == 0) {
        currentRound++;
        market.nextRound();
        
        // Verificar si se alcanzó el máximo de rondas
        if (currentRound > settings.maxRounds) {
            endGame();
            return;
        }
    }
    
    // Mostrar información del nuevo turno
    Player& player = playerManager.getCurrentPlayer();
    std::cout << "Turno de " << player.name << std::endl;
}

TurnInfo& Game::getCurrentTurn() {
    return currentTurn;
}

bool Game::isPlayerTurn(int playerId) {
    return currentTurn.currentPlayer == playerId;
}

void Game::skipTurn() {
    nextTurn();
}

bool Game::buyStock(const std::string& companyId, int quantity) {
    int playerId = playerManager.getCurrentPlayerIndex();
    Player& player = playerManager.getCurrentPlayer();
    Company& company = market.getCompany(companyId);
    
    float totalCost = company.stockPrice * quantity;
    
    if (player.canBuy(company.stockPrice, quantity)) {
        if (market.buyStock(playerId, companyId, quantity)) {
            player.capital -= totalCost;
            player.addStock(companyId, quantity, company.stockPrice);
            player.calculateMarketValue(market.getAllCompanies().transform(
                [](const auto& pair) { return std::make_pair(pair.first, pair.second.stockPrice); }
            ));
            return true;
        }
    }
    
    return false;
}

bool Game::sellStock(const std::string& companyId, int quantity) {
    int playerId = playerManager.getCurrentPlayerIndex();
    Player& player = playerManager.getCurrentPlayer();
    Company& company = market.getCompany(companyId);
    
    if (player.canSell(companyId, quantity)) {
        if (market.sellStock(playerId, companyId, quantity)) {
            float totalValue = company.stockPrice * quantity;
            player.capital += totalValue;
            player.removeStock(companyId, quantity);
            player.calculateMarketValue(market.getAllCompanies().transform(
                [](const auto& pair) { return std::make_pair(pair.first, pair.second.stockPrice); }
            ));
            return true;
        }
    }
    
    return false;
}

bool Game::mergeCompanies(const std::string& company1, const std::string& company2) {
    int playerId = playerManager.getCurrentPlayerIndex();
    
    if (market.canMerge(company1, company2, playerId)) {
        market.mergeCompanies(company1, company2);
        return true;
    }
    
    return false;
}

bool Game::playCard(const std::string& cardId, int target) {
    if (currentTurn.canPlayCard) {
        market.playCard(cardId, target);
        currentTurn.canPlayCard = false;
        return true;
    }
    return false;
}

bool Game::proposeTrade(int fromPlayer, int toPlayer) {
    if (settings.tradingEnabled && currentTurn.canTrade) {
        ui.startTrade(fromPlayer, toPlayer);
        ui.setState(UIState::TRADE_SCREEN);
        return true;
    }
    return false;
}

std::string Game::createLobby() {
    // Generar código único
    const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    std::string code = "";
    
    for (int i = 0; i < 6; i++) {
        code += chars[rand() % 36];
    }
    
    settings.lobbyCode = code;
    settings.isOnline = true;
    
    return code;
}

bool Game::joinLobby(const std::string& code) {
    // En una implementación real, esto se conectaría a un servidor
    settings.lobbyCode = code;
    settings.isOnline = true;
    return true;
}

void Game::sendAction(const Action& action) {
    actionQueue.push_back(action);
}

void Game::receiveAction(const Action& action) {
    // Procesar acción recibida
}

GameState Game::getState() const {
    return state;
}

int Game::getCurrentRound() const {
    return currentRound;
}

bool Game::checkGameOver() {
    Player winner;
    if (playerManager.checkVictory(winner)) {
        endGame();
        return true;
    }
    
    // Verificar bancarrota
    for (auto& player : playerManager.getAllPlayers()) {
        if (player.capital <= 0 && player.marketValue <= 0) {
            player.isBankrupt = true;
        }
    }
    
    // Verificar si queda un solo jugador
    int activePlayers = 0;
    for (const auto& player : playerManager.getAllPlayers()) {
        if (!player.isBankrupt) activePlayers++;
    }
    
    if (activePlayers <= 1) {
        endGame();
        return true;
    }
    
    return false;
}

void Game::determineWinner() {
    Player winner;
    playerManager.checkVictory(winner);
    
    ui.setState(UIState::VICTORY);
    
    std::cout << "¡" << winner.name << " gana la partida!" << std::endl;
}

float Game::getGlobalTimer() const {
    return globalTimer;
}

int Game::getActivePlayerCount() const {
    int count = 0;
    for (const auto& player : playerManager.getAllPlayers()) {
        if (!player.isBankrupt) count++;
    }
    return count;
}

// Métodos privados - IA
void Game::processAITurn(int playerId) {
    // Simular pensamiento de la IA
    static float aiThinkTime = 0;
    aiThinkTime += GetFrameTime();
    
    if (aiThinkTime > 2.0f) { // Pensar durante 2 segundos
        aiThinkTime = 0;
        
        Player& player = playerManager.getPlayer(playerId);
        
        // Decidir compra
        aiBuyDecision(playerId);
        
        // Decidir venta
        aiSellDecision(playerId);
        
        // Decidir fusión
        aiMergeDecision(playerId);
        
        // Pasar turno
        nextTurn();
    }
}

void Game::aiBuyDecision(int playerId) {
    Player& player = playerManager.getPlayer(playerId);
    auto& companies = market.getAllCompanies();
    
    // IA simple: comprar acciones aleatorias si tiene capital
    if (player.capital > 500) {
        int companyIndex = rand() % companies.size();
        auto it = companies.begin();
        std::advance(it, companyIndex);
        
        if (it->second.availableShares > 0 && player.capital >= it->second.stockPrice * 5) {
            market.buyStock(playerId, it->first, 5);
            player.capital -= it->second.stockPrice * 5;
            player.addStock(it->first, 5, it->second.stockPrice);
        }
    }
}

void Game::aiSellDecision(int playerId) {
    // IA simple: no vender a menos que necesite dinero urgentemente
    Player& player = playerManager.getPlayer(playerId);
    
    if (player.capital < 100 && !player.portfolio.empty()) {
        // Vender algunas acciones
        Stock& stock = player.portfolio[0];
        if (stock.quantity > 2) {
            market.sellStock(playerId, stock.companyId, 2);
            Company& company = market.getCompany(stock.companyId);
            player.capital += company.stockPrice * 2;
            player.removeStock(stock.companyId, 2);
        }
    }
}

void Game::aiMergeDecision(int playerId) {
    // IA simple: intentar fusionar si es posible
    auto& companies = market.getAllCompanies();
    
    for (auto it1 = companies.begin(); it1 != companies.end(); ++it1) {
        for (auto it2 = std::next(it1); it2 != companies.end(); ++it2) {
            if (market.canMerge(it1->first, it2->first, playerId)) {
                market.mergeCompanies(it1->first, it2->first);
                return;
            }
        }
    }
}

void Game::aiCardDecision(int playerId) {
    // IA simple: usar carta aleatoria si tiene
    market.drawCard(playerId);
}

// Manejo de input
void Game::handleMenuInput() {
    Vector2 mousePos = GetMousePosition();
    
    if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
        auto& buttons = ui.getUI().buttons; // Necesitaríamos un getter
        
        // Detectar clicks en botones del menú
        // Esto es simplificado - en producción usaríamos el sistema de botones de UI
        if (CheckCollisionPointRec(mousePos, {(float)(GetScreenWidth()/2 - 150), 
                                               (float)(GetScreenHeight()/2 - 80), 300, 50})) {
            // Partida Local
            state = GameState::SETUP;
            ui.setState(UIState::GAME_SETUP);
        }
    }
}

void Game::handleSetupInput() {
    Vector2 mousePos = GetMousePosition();
    
    if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
        // Detectar botón de iniciar
        Rectangle startBtn = {(float)(GetScreenWidth()/2 - 100), 
                              (float)(GetScreenHeight() - 120), 200, 50};
        
        if (CheckCollisionPointRec(mousePos, startBtn)) {
            startGame();
        }
        
        // Detectar botón volver
        Rectangle backBtn = {(float)(GetScreenWidth()/2 - 100), 
                             (float)(GetScreenHeight() - 60), 200, 40};
        
        if (CheckCollisionPointRec(mousePos, backBtn)) {
            state = GameState::WAITING_PLAYERS;
            ui.setState(UIState::MENU_MAIN);
        }
    }
}

void Game::handleGameInput() {
    // Pausa
    if (IsKeyPressed(KEY_ESCAPE)) {
        pauseGame();
        return;
    }
    
    // Saltar turno con ESPACIO
    if (IsKeyPressed(KEY_SPACE)) {
        nextTurn();
        return;
    }
    
    // Interacción con el tablero
    Ray ray = GetCameraRay(board.getActiveCamera(), GetMousePosition());
    
    if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
        // Click en empresa
        CompanyMarker* marker = board.raycastCompany(ray);
        if (marker != nullptr) {
            board.highlightCompany(marker->companyId, true);
            // Mostrar panel de detalles de la empresa
        }
        
        // Click en sector
        Sector3D* sector = board.raycastSector(ray);
        if (sector != nullptr) {
            board.highlightSector(sector->id, true);
        }
    }
}
