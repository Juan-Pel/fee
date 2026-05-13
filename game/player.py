"""
Player - Representa un jugador (corporación) en el juego
"""
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Player:
    """
    Representa una corporación jugadora que compite en el mercado bursátil.
    Gestiona capital, acciones, cartas y puntos de influencia.
    """
    
    player_id: str
    name: str
    is_ai: bool = False
    
    # Recursos económicos
    cash: float = 10000.0  # Capital inicial
    initial_cash: float = 10000.0
    
    # Acciones poseídas: company_id -> cantidad
    shares: Dict[str, int] = field(default_factory=dict)
    
    # Cartas en mano
    cards: List[str] = field(default_factory=list)  # IDs de cartas
    
    # Puntuación
    influence_points: int = 0  # Para modo estándar
    market_value: float = 0.0  # Valor total de mercado (acciones + efectivo)
    
    # Estadísticas
    companies_owned: Set[str] = field(default_factory=set)  # Empresas con mayoría
    sectors_controlled: Set[str] = field(default_factory=set)  # Sectores controlados
    turns_played: int = 0
    total_trades: int = 0
    successful_mergers: int = 0
    
    # Estado del jugador
    is_bankrupt: bool = False
    has_negotiated_this_turn: bool = False
    
    @property
    def portfolio_value(self) -> float:
        """Calcula el valor total del portafolio (se actualiza externamente)"""
        return self.market_value
    
    @property
    def net_worth(self) -> float:
        """Valor neto total (efectivo + valor de mercado)"""
        return self.cash + self.market_value
    
    @property
    def liquidity_ratio(self) -> float:
        """Ratio de liquidez (efectivo / valor neto)"""
        if self.net_worth == 0:
            return 0
        return self.cash / self.net_worth
    
    def add_shares(self, company_id: str, quantity: int):
        """Añade acciones de una empresa al portafolio"""
        self.shares[company_id] = self.shares.get(company_id, 0) + quantity
        
    def remove_shares(self, company_id: str, quantity: int) -> bool:
        """
        Elimina acciones de una empresa del portafolio.
        Retorna True si fue exitoso.
        """
        current = self.shares.get(company_id, 0)
        if quantity > current:
            return False
            
        self.shares[company_id] = current - quantity
        if self.shares[company_id] == 0:
            del self.shares[company_id]
        return True
    
    def add_card(self, card_id: str):
        """Añade una carta a la mano"""
        if len(self.cards) < 10:  # Máximo 10 cartas
            self.cards.append(card_id)
            return True
        return False
    
    def use_card(self, card_id: str) -> Optional[str]:
        """
        Usa una carta y la elimina de la mano.
        Retorna el ID de la carta si fue usada.
        """
        if card_id in self.cards:
            self.cards.remove(card_id)
            return card_id
        return None
    
    def update_market_value(self, company_prices: Dict[str, float]):
        """Actualiza el valor de mercado basado en los precios actuales"""
        total = 0
        for company_id, quantity in self.shares.items():
            price = company_prices.get(company_id, 0)
            total += price * quantity
        self.market_value = total
    
    def check_majority(self, company_id: str, total_shares: int) -> bool:
        """Verifica si tiene mayoría en una empresa (>50%)"""
        my_shares = self.shares.get(company_id, 0)
        return my_shares > total_shares * 0.5
    
    def add_influence(self, points: int):
        """Añade puntos de influencia"""
        self.influence_points += points
        
    def spend_cash(self, amount: float) -> bool:
        """
        Gasta efectivo. Retorna True si hay suficiente.
        """
        if self.cash >= amount:
            self.cash -= amount
            return True
        return False
    
    def receive_cash(self, amount: float):
        """Recibe efectivo"""
        self.cash += amount
        
    def can_afford(self, amount: float) -> bool:
        """Verifica si puede pagar una cantidad"""
        return self.cash >= amount
    
    def declare_bankruptcy(self):
        """Declara bancarrota"""
        self.is_bankrupt = True
        
    def get_portfolio_summary(self, companies_data: Dict[str, dict]) -> Dict:
        """Retorna un resumen completo del portafolio"""
        holdings = []
        total_value = 0
        
        for company_id, quantity in self.shares.items():
            if company_id in companies_data:
                comp = companies_data[company_id]
                value = quantity * comp.get('price', 0)
                percentage = (quantity / comp.get('total_shares', 1)) * 100
                holdings.append({
                    'company': comp.get('name', company_id),
                    'shares': quantity,
                    'price': comp.get('price', 0),
                    'value': round(value, 2),
                    'percentage': round(percentage, 2)
                })
                total_value += value
                
        return {
            'cash': round(self.cash, 2),
            'market_value': round(total_value, 2),
            'net_worth': round(self.cash + total_value, 2),
            'influence': self.influence_points,
            'holdings': holdings,
            'companies_owned': list(self.companies_owned),
            'sectors_controlled': list(self.sectors_controlled),
            'cards_count': len(self.cards)
        }
    
    def __str__(self) -> str:
        status = "💀" if self.is_bankrupt else ("🤖" if self.is_ai else "👤")
        return f"{status} {self.name}: ${self.cash:.0f} | Influencia: {self.influence_points}"
