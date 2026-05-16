#include "player.h"
#include <algorithm>
#include <cmath>

void Player::calculateMarketValue(const std::map<std::string, float>& stockPrices) {
    marketValue = capital;
    for (const auto& stock : portfolio) {
        auto it = stockPrices.find(stock.companyId);
        if (it != stockPrices.end()) {
            marketValue += stock.quantity * it->second;
        }
    }
}

void Player::addStock(const std::string& companyId, int quantity, float price) {
    // Buscar si ya tenemos acciones de esta empresa
    for (auto& stock : portfolio) {
        if (stock.companyId == companyId) {
            // Calcular nuevo precio promedio
            float totalValue = stock.quantity * stock.averagePrice + quantity * price;
            stock.quantity += quantity;
            stock.averagePrice = totalValue / stock.quantity;
            return;
        }
    }
    
    // Nueva acción en el portafolio
    Stock newStock;
    newStock.companyId = companyId;
    newStock.quantity = quantity;
    newStock.averagePrice = price;
    portfolio.push_back(newStock);
}

void Player::removeStock(const std::string& companyId, int quantity) {
    for (auto it = portfolio.begin(); it != portfolio.end(); ++it) {
        if (it->companyId == companyId) {
            it->quantity -= quantity;
            if (it->quantity <= 0) {
                portfolio.erase(it);
            }
            return;
        }
    }
}

bool Player::canBuy(float price, int quantity) const {
    return capital >= (price * quantity);
}

bool Player::canSell(const std::string& companyId, int quantity) const {
    for (const auto& stock : portfolio) {
        if (stock.companyId == companyId && stock.quantity >= quantity) {
            return true;
        }
    }
    return false;
}

// Implementación de PlayerManager
PlayerManager::PlayerManager() : currentPlayerIndex(0), victoryCondition(VictoryCondition::MAGNATE) {}

void PlayerManager::addPlayer(const std::string& name, PlayerType type) {
    Player player;
    player.id = players.size();
    player.name = name;
    player.type = type;
    players.push_back(player);
}

Player& PlayerManager::getCurrentPlayer() {
    return players[currentPlayerIndex];
}

Player& PlayerManager::getPlayer(int index) {
    return players[index];
}

int PlayerManager::getCurrentPlayerIndex() const {
    return currentPlayerIndex;
}

void PlayerManager::nextTurn() {
    currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
}

bool PlayerManager::checkVictory(Player& winner) {
    if (players.size() == 1) {
        winner = players[0];
        return true;
    }
    
    switch (victoryCondition) {
        case VictoryCondition::MAGNATE: {
            // El que tenga mayor valor de mercado gana
            Player* maxPlayer = &players[0];
            for (auto& player : players) {
                if (player.marketValue > maxPlayer->marketValue) {
                    maxPlayer = &player;
                }
            }
            winner = *maxPlayer;
            return true;
        }
        
        case VictoryCondition::OLIGOPOLY: {
            // El que controle >50% de algún sector gana
            for (auto& player : players) {
                for (const auto& sector : player.sectorControl) {
                    if (sector.second > 50) {
                        winner = player;
                        return true;
                    }
                }
            }
            return false;
        }
        
        case VictoryCondition::INFLUENCE: {
            // El que tenga más puntos de influencia gana
            Player* maxPlayer = &players[0];
            for (auto& player : players) {
                if (player.influencePoints > maxPlayer->influencePoints) {
                    maxPlayer = &player;
                }
            }
            winner = *maxPlayer;
            return true;
        }
    }
    
    return false;
}

std::vector<Player>& PlayerManager::getAllPlayers() {
    return players;
}

void PlayerManager::setVictoryCondition(VictoryCondition condition) {
    victoryCondition = condition;
}

VictoryCondition PlayerManager::getVictoryCondition() const {
    return victoryCondition;
}
