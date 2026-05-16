#include "market.h"
#include <cstdlib>
#include <ctime>
#include <algorithm>
#include <cmath>

void Company::updatePrice(float change) {
    stockPrice = std::max(1.0f, stockPrice * (1.0f + change));
}

void Company::addPriceHistory() {
    for (int i = 9; i > 0; i--) {
        priceHistory[i] = priceHistory[i - 1];
    }
    priceHistory[0] = stockPrice;
}

Market::Market() : round(0) {
    srand(static_cast<unsigned int>(time(nullptr)));
    initializeCompanies();
}

void Market::initializeCompanies() {
    // Tecnología
    companies["TECH1"] = {"TECH1", "TechCorp", SectorType::TECHNOLOGY, 150.0f, {}, 1000, 800, {}, 0.15f, false, ""};
    companies["TECH2"] = {"TECH2", "InnovateX", SectorType::TECHNOLOGY, 120.0f, {}, 1000, 750, {}, 0.18f, false, ""};
    
    // Energía
    companies["ENRG1"] = {"ENRG1", "PowerCo", SectorType::ENERGY, 100.0f, {}, 1000, 900, {}, 0.10f, false, ""};
    companies["ENRG2"] = {"ENRG2", "GreenEnergy", SectorType::ENERGY, 85.0f, {}, 1000, 850, {}, 0.12f, false, ""};
    
    // Turismo
    companies["TOUR1"] = {"TOUR1", "TravelWorld", SectorType::TOURISM, 95.0f, {}, 1000, 800, {}, 0.20f, false, ""};
    companies["TOUR2"] = {"TOUR2", "HotelChain", SectorType::TOURISM, 110.0f, {}, 1000, 700, {}, 0.14f, false, ""};
    
    // Finanzas
    companies["FIN1"] = {"FIN1", "BankCorp", SectorType::FINANCE, 200.0f, {}, 1000, 600, {}, 0.08f, false, ""};
    companies["FIN2"] = {"FIN2", "InvestPlus", SectorType::FINANCE, 175.0f, {}, 1000, 650, {}, 0.11f, false, ""};
    
    // Salud
    companies["HLTH1"] = {"HLTH1", "PharmaInc", SectorType::HEALTH, 180.0f, {}, 1000, 700, {}, 0.13f, false, ""};
    companies["HLTH2"] = {"HLTH2", "BioTech", SectorType::HEALTH, 140.0f, {}, 1000, 750, {}, 0.16f, false, ""};
    
    // Inmobiliario
    companies["REAL1"] = {"REAL1", "EstatePro", SectorType::REAL_ESTATE, 130.0f, {}, 1000, 800, {}, 0.09f, false, ""};
    companies["REAL2"] = {"REAL2", "BuildCorp", SectorType::REAL_ESTATE, 115.0f, {}, 1000, 850, {}, 0.10f, false, ""};
    
    // Consumo
    companies["CONS1"] = {"CONS1", "RetailMax", SectorType::CONSUMER, 90.0f, {}, 1000, 900, {}, 0.07f, false, ""};
    companies["CONS2"] = {"CONS2", "FoodCo", SectorType::CONSUMER, 75.0f, {}, 1000, 950, {}, 0.06f, false, ""};
    
    // Industrial
    companies["IND1"] = {"IND1", "ManufactureX", SectorType::INDUSTRIAL, 160.0f, {}, 1000, 700, {}, 0.11f, false, ""};
    companies["IND2"] = {"IND2", "SteelWorks", SectorType::INDUSTRIAL, 125.0f, {}, 1000, 750, {}, 0.12f, false, ""};
    
    // Inicializar historial de precios
    for (auto& pair : companies) {
        for (int i = 0; i < 10; i++) {
            pair.second.priceHistory[i] = pair.second.stockPrice;
        }
    }
}

Company& Market::getCompany(const std::string& id) {
    return companies[id];
}

std::map<std::string, Company>& Market::getAllCompanies() {
    return companies;
}

bool Market::buyStock(int playerId, const std::string& companyId, int quantity) {
    auto it = companies.find(companyId);
    if (it == companies.end()) return false;
    
    Company& company = it->second;
    if (company.availableShares < quantity) return false;
    
    float totalCost = company.stockPrice * quantity;
    
    company.availableShares -= quantity;
    company.ownership[playerId] += quantity;
    
    return true;
}

bool Market::sellStock(int playerId, const std::string& companyId, int quantity) {
    auto it = companies.find(companyId);
    if (it == companies.end()) return false;
    
    Company& company = it->second;
    auto ownerIt = company.ownership.find(playerId);
    
    if (ownerIt == company.ownership.end() || ownerIt->second < quantity) {
        return false;
    }
    
    company.availableShares += quantity;
    ownerIt->second -= quantity;
    
    if (ownerIt->second == 0) {
        company.ownership.erase(ownerIt);
    }
    
    return true;
}

void Market::updatePrices() {
    // Actualizar precios basados en oferta/demanda y volatilidad
    for (auto& pair : companies) {
        Company& company = pair.second;
        
        // Calcular cambio basado en volatilidad
        float baseChange = (static_cast<float>(rand()) / RAND_MAX - 0.5f) * 2.0f * company.volatility;
        
        // Ajustar por demanda (si hay muchas compras, sube)
        int totalOwned = 0;
        for (const auto& owner : company.ownership) {
            totalOwned += owner.second;
        }
        float demandFactor = (static_cast<float>(totalOwned) / company.totalShares) - 0.5f;
        
        // Aplicar cambios
        float totalChange = baseChange + (demandFactor * 0.1f);
        company.updatePrice(totalChange);
        company.addPriceHistory();
    }
    
    // Aplicar efectos de eventos activos
    applyEventEffects();
}

void Market::triggerRandomEvent() {
    const char* titles[] = {
        "Innovación Tecnológica",
        "Crisis Energética",
        "Pandemia Global",
        "Boom Económico",
        "Nueva Regulación",
        "Desastre Natural",
        "Avance Médico",
        "Burbuja Inmobiliaria"
    };
    
    const char* descriptions[] = {
        "Las empresas tecnológicas ven aumentar su valor un 20%",
        "El sector energético sufre una caída del 15%",
        "El turismo se desploma un 30% por restricciones",
        "Todos los sectores crecen un 10%",
        "Nuevas regulaciones afectan al sector financiero",
        "Un tornado daña plantas industriales",
        "Nuevo medicamento revoluciona el sector salud",
        "El mercado inmobiliario entra en crisis"
    };
    
    MarketEvent event;
    int eventType = rand() % 8;
    
    event.type = static_cast<EventType>(eventType);
    event.title = titles[eventType];
    event.description = descriptions[eventType];
    event.duration = 3;
    event.currentDuration = 3;
    
    switch (eventType) {
        case 0: // Innovación tecnológica
            event.affectedSector = "TECHNOLOGY";
            event.impactPercent = 0.20f;
            break;
        case 1: // Crisis energética
            event.affectedSector = "ENERGY";
            event.impactPercent = -0.15f;
            break;
        case 2: // Pandemia
            event.affectedSector = "TOURISM";
            event.impactPercent = -0.30f;
            break;
        case 3: // Boom económico
            event.affectedSector = "ALL";
            event.impactPercent = 0.10f;
            break;
        case 4: // Regulación
            event.affectedSector = "FINANCE";
            event.impactPercent = -0.12f;
            break;
        case 5: // Desastre natural
            event.affectedSector = "INDUSTRIAL";
            event.impactPercent = -0.18f;
            break;
        case 6: // Avance médico
            event.affectedSector = "HEALTH";
            event.impactPercent = 0.25f;
            break;
        case 7: // Burbuja inmobiliaria
            event.affectedSector = "REAL_ESTATE";
            event.impactPercent = -0.20f;
            break;
    }
    
    activeEvents.push_back(event);
}

void Market::applyEventEffects() {
    for (auto it = activeEvents.begin(); it != activeEvents.end();) {
        MarketEvent& event = *it;
        
        for (auto& pair : companies) {
            Company& company = pair.second;
            
            bool affected = false;
            
            if (event.affectedSector == "ALL") {
                affected = true;
            } else {
                // Verificar si la empresa pertenece al sector afectado
                std::string companySector;
                switch (company.sector) {
                    case SectorType::TECHNOLOGY: companySector = "TECHNOLOGY"; break;
                    case SectorType::ENERGY: companySector = "ENERGY"; break;
                    case SectorType::TOURISM: companySector = "TOURISM"; break;
                    case SectorType::FINANCE: companySector = "FINANCE"; break;
                    case SectorType::HEALTH: companySector = "HEALTH"; break;
                    case SectorType::REAL_ESTATE: companySector = "REAL_ESTATE"; break;
                    case SectorType::CONSUMER: companySector = "CONSUMER"; break;
                    case SectorType::INDUSTRIAL: companySector = "INDUSTRIAL"; break;
                }
                
                if (companySector == event.affectedSector) {
                    affected = true;
                }
            }
            
            if (affected) {
                company.updatePrice(event.impactPercent / event.duration);
            }
        }
        
        event.currentDuration--;
        if (event.currentDuration <= 0) {
            it = activeEvents.erase(it);
        } else {
            ++it;
        }
    }
}

void Market::drawCard(int playerId) {
    // Implementación simplificada - en producción habría un mazo real
    Card card;
    card.id = "CARD_" + std::to_string(rand() % 10);
    card.name = "Oportunidad de Inversión";
    card.description = "Compra acciones con 10% de descuento";
    card.cardType = Card::CardType::ACTION;
    card.targetType = Card::TargetType::SELF;
    card.value = 0.10f;
    card.cost = 0;
    card.used = false;
    
    // En una implementación completa, esto se añadiría al inventario del jugador
}

void Market::playCard(const std::string& cardId, int targetPlayerId, const std::string& targetCompany) {
    // Implementación de uso de cartas
}

bool Market::canMerge(const std::string& company1, const std::string& company2, int playerId) {
    auto it1 = companies.find(company1);
    auto it2 = companies.find(company2);
    
    if (it1 == companies.end() || it2 == companies.end()) return false;
    
    // Verificar que sean del mismo sector
    if (it1->second.sector != it2->second.sector) return false;
    
    // Verificar que el jugador tenga mayoría en ambas
    int shares1 = it1->second.ownership.count(playerId) ? it1->second.ownership[playerId] : 0;
    int shares2 = it2->second.ownership.count(playerId) ? it2->second.ownership[playerId] : 0;
    
    return (shares1 > it1->second.totalShares * 0.5f) && 
           (shares2 > it2->second.totalShares * 0.5f);
}

void Market::mergeCompanies(const std::string& company1, const std::string& company2) {
    auto it1 = companies.find(company1);
    auto it2 = companies.find(company2);
    
    if (it1 == companies.end() || it2 == companies.end()) return;
    
    // Fusionar: la más grande absorbe a la más pequeña
    Company& bigger = (it1->second.totalShares > it2->second.totalShares) ? 
                      it1->second : it2->second;
    Company& smaller = (it1->second.totalShares > it2->second.totalShares) ? 
                       it2->second : it1->second;
    
    bigger.totalShares += smaller.totalShares;
    bigger.availableShares += smaller.availableShares;
    
    // Transferir propiedad
    for (const auto& owner : smaller.ownership) {
        bigger.ownership[owner.first] += owner.second;
    }
    
    smaller.isMerged = true;
    smaller.mergedWith = bigger.id;
    smaller.stockPrice = 0;
    smaller.availableShares = 0;
}

void Market::nextRound() {
    round++;
    updatePrices();
    
    // Trigger event cada 3-5 rondas
    if (round % (3 + rand() % 3) == 0) {
        triggerRandomEvent();
    }
}

std::vector<MarketEvent>& Market::getActiveEvents() {
    return activeEvents;
}
