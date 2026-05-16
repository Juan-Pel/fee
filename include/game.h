#ifndef GAME_H
#define GAME_H

#include "player.h"
#include "market.h"
#include "board.h"
#include "ui.h"
#include <string>
#include <vector>

enum class GameMode {
    QUICK,      // 15 min
    STANDARD,   // 30-45 min
    EXTENDED    // 90 min
};

enum class GameState {
    WAITING_PLAYERS,
    SETUP,
    PLAYING,
    PAUSED,
    ENDED
};

struct GameSettings {
    GameMode mode;
    int maxPlayers;
    int humanPlayers;
    int aiPlayers;
    float turnTime; // segundos por turno
    int maxRounds;
    bool eventsEnabled;
    bool tradingEnabled;
    VictoryCondition victoryCondition;
    std::string lobbyCode;
    bool isOnline;
};

struct TurnInfo {
    int currentPlayer;
    float timeRemaining;
    int actionsRemaining;
    bool canTrade;
    bool canPlayCard;
};

class Game {
private:
    GameState state;
    GameSettings settings;
    
    PlayerManager playerManager;
    Market market;
    Board board;
    UI ui;
    
    TurnInfo currentTurn;
    int currentRound;
    float globalTimer; // para modos de tiempo limitado
    
    // Cola de acciones para multijugador
    struct Action {
        int playerId;
        std::string type;
        std::string target;
        int value;
        double timestamp;
    };
    std::vector<Action> actionQueue;
    
    // IA
    void processAITurn(int playerId);
    void aiBuyDecision(int playerId);
    void aiSellDecision(int playerId);
    void aiMergeDecision(int playerId);
    void aiCardDecision(int playerId);
    
public:
    Game();
    ~Game();
    
    bool initialize();
    void run();
    void update();
    void draw();
    void unload();
    
    // Gestión del juego
    void startGame();
    void endGame();
    void pauseGame();
    void resumeGame();
    
    // Configuración
    void setGameMode(GameMode mode);
    void setVictoryCondition(VictoryCondition condition);
    void setTurnTime(float time);
    void setMaxRounds(int rounds);
    GameSettings& getSettings();
    
    // Jugadores
    void addHumanPlayer(const std::string& name);
    void addAIPlayer(PlayerType type);
    PlayerManager& getPlayerManager();
    
    // Mercado
    Market& getMarket();
    
    // Tablero
    Board& getBoard();
    
    // UI
    UI& getUI();
    
    // Turnos
    void nextTurn();
    TurnInfo& getCurrentTurn();
    bool isPlayerTurn(int playerId);
    void skipTurn();
    
    // Acciones de juego
    bool buyStock(const std::string& companyId, int quantity);
    bool sellStock(const std::string& companyId, int quantity);
    bool mergeCompanies(const std::string& company1, const std::string& company2);
    bool playCard(const std::string& cardId, int target = -1);
    bool proposeTrade(int fromPlayer, int toPlayer);
    
    // Multijugador
    std::string createLobby();
    bool joinLobby(const std::string& code);
    void sendAction(const Action& action);
    void receiveAction(const Action& action);
    
    // Estado
    GameState getState() const;
    int getCurrentRound() const;
    bool checkGameOver();
    void determineWinner();
    
    // Utilidades
    float getGlobalTimer() const;
    int getActivePlayerCount() const;
};

#endif // GAME_H
