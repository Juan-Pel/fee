#ifndef MARKET_H
#define MARKET_H

#include <string>
#include <vector>
#include <map>

enum class SectorType {
    TECHNOLOGY,
    ENERGY,
    TOURISM,
    FINANCE,
    HEALTH,
    REAL_ESTATE,
    CONSUMER,
    INDUSTRIAL
};

struct Company {
    std::string id;
    std::string name;
    SectorType sector;
    float stockPrice;
    float priceHistory[10]; // Últimos 10 precios
    int totalShares;
    int availableShares;
    std::map<int, int> ownership; // playerId -> shares
    float volatility;
    bool isMerged;
    std::string mergedWith;
    
    Company() : stockPrice(100), totalShares(1000), availableShares(1000),
                volatility(0.1f), isMerged(false) {}
    
    void updatePrice(float change);
    void addPriceHistory();
};

enum class EventType {
    POSITIVE_NEWS,
    NEGATIVE_NEWS,
    NATURAL_DISASTER,
    MARKET_CRASH,
    INNOVATION,
    REGULATION,
    PANDEMIC,
    ECONOMIC_BOOM
};

struct MarketEvent {
    EventType type;
    std::string title;
    std::string description;
    std::string affectedSector;
    float impactPercent;
    int duration; // rondas que dura el efecto
    int currentDuration;
    
    MarketEvent() : impactPercent(0), duration(0), currentDuration(0) {}
};

struct Card {
    std::string id;
    std::string name;
    std::string description;
    enum class CardType {
        ACTION,
        EVENT,
        NEGOTIATION
    } cardType;
    
    enum class TargetType {
        SELF,
        OTHER_PLAYER,
        COMPANY,
        SECTOR,
        ALL
    } targetType;
    
    float value;
    int cost;
    bool used;
};

class Market {
private:
    std::map<std::string, Company> companies;
    std::vector<MarketEvent> activeEvents;
    std::vector<Card> deck;
    std::vector<Card> discardedCards;
    int round;
    
public:
    Market();
    
    void initializeCompanies();
    Company& getCompany(const std::string& id);
    std::map<std::string, Company>& getAllCompanies();
    
    bool buyStock(int playerId, const std::string& companyId, int quantity);
    bool sellStock(int playerId, const std::string& companyId, int quantity);
    
    void updatePrices();
    void triggerRandomEvent();
    void applyEventEffects();
    
    void drawCard(int playerId);
    void playCard(const std::string& cardId, int targetPlayerId = -1, 
                  const std::string& targetCompany = "");
    
    bool canMerge(const std::string& company1, const std::string& company2, int playerId);
    void mergeCompanies(const std::string& company1, const std::string& company2);
    
    int getRound() const { return round; }
    void nextRound();
    
    std::vector<MarketEvent>& getActiveEvents();
};

#endif // MARKET_H
