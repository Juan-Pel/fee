#ifndef PLAYER_H
#define PLAYER_H

#include <string>
#include <vector>
#include <map>

enum class PlayerType {
    HUMAN,
    AI_AGGRESSIVE,
    AI_CONSERVATIVE,
    AI_BALANCED
};

enum class VictoryCondition {
    MAGNATE,        // Mayor capital
    OLIGOPOLY,      // Controlar >50% de un sector
    INFLUENCE       // Puntos por diversidad
};

struct Stock {
    std::string companyId;
    int quantity;
    float averagePrice;
};

struct Player {
    int id;
    std::string name;
    PlayerType type;
    float capital;
    float marketValue;
    int influencePoints;
    std::vector<Stock> portfolio;
    std::map<std::string, int> sectorControl; // porcentaje por sector
    bool isBankrupt;
    
    Player() : id(0), capital(10000), marketValue(10000), 
               influencePoints(0), isBankrupt(false) {}
    
    void calculateMarketValue(const std::map<std::string, float>& stockPrices);
    void addStock(const std::string& companyId, int quantity, float price);
    void removeStock(const std::string& companyId, int quantity);
    bool canBuy(float price, int quantity) const;
    bool canSell(const std::string& companyId, int quantity) const;
};

class PlayerManager {
private:
    std::vector<Player> players;
    int currentPlayerIndex;
    VictoryCondition victoryCondition;
    
public:
    PlayerManager();
    
    void addPlayer(const std::string& name, PlayerType type);
    Player& getCurrentPlayer();
    Player& getPlayer(int index);
    int getCurrentPlayerIndex() const;
    void nextTurn();
    bool checkVictory(Player& winner);
    std::vector<Player>& getAllPlayers();
    void setVictoryCondition(VictoryCondition condition);
    VictoryCondition getVictoryCondition() const;
};

#endif // PLAYER_H
