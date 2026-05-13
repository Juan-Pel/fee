"""
Company - Representa una empresa que puede ser comprada/vendida en el mercado
"""
from typing import Dict, List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .sector import Sector


class CompanyStatus(Enum):
    """Estados posibles de una empresa"""
    ACTIVE = "Activa"
    MERGED = "Fusionada"
    ABSORBED = "Absorbida"
    BANKRUPT = "En bancarrota"


class Company:
    """
    Representa una empresa cuyas acciones pueden ser compradas y vendidas.
    El precio de las acciones cambia dinámicamente según la demanda y eventos.
    """
    
    def __init__(self, company_id: str, name: str, sector: 'Sector', 
                 initial_price: float = 10.0, total_shares: int = 1000):
        self.company_id = company_id
        self.name = name
        self.sector = sector
        self.status = CompanyStatus.ACTIVE
        
        # Configuración de acciones
        self.initial_price = initial_price
        self.current_price = initial_price
        self.total_shares = total_shares
        self.available_shares = total_shares  # Acciones en el mercado
        
        # Propiedad
        self.shareholders: Dict[str, int] = {}  # player_id -> número de acciones
        
        # Historial de precios
        self.price_history: List[float] = [initial_price]
        
        # Añadir empresa al sector
        sector.add_company(company_id)
        
    @property
    def market_cap(self) -> float:
        """Capitalización de mercado (precio * total de acciones)"""
        return self.current_price * self.total_shares
    
    @property
    def price_change(self) -> float:
        """Cambio porcentual respecto al precio inicial"""
        return ((self.current_price - self.initial_price) / self.initial_price) * 100
    
    @property
    def owner(self) -> Optional[str]:
        """Retorna el ID del jugador mayoritario si existe (>50%)"""
        for player_id, shares in self.shareholders.items():
            if shares > self.total_shares * 0.5:
                return player_id
        return None
    
    @property
    def majority_owner(self) -> Optional[str]:
        """Retorna el ID del jugador con más acciones"""
        if not self.shareholders:
            return None
        return max(self.shareholders, key=self.shareholders.get)
    
    def buy_shares(self, player_id: str, quantity: int, price: float) -> bool:
        """
        Un jugador compra acciones de la empresa.
        Retorna True si la compra fue exitosa.
        """
        if quantity > self.available_shares:
            return False
            
        self.available_shares -= quantity
        self.shareholders[player_id] = self.shareholders.get(player_id, 0) + quantity
        self.update_price(price)
        return True
    
    def sell_shares(self, player_id: str, quantity: int, price: float) -> bool:
        """
        Un jugador vende acciones de la empresa.
        Retorna True si la venta fue exitosa.
        """
        current_holdings = self.shareholders.get(player_id, 0)
        if quantity > current_holdings:
            return False
            
        self.shareholders[player_id] = current_holdings - quantity
        self.available_shares += quantity
        
        # Eliminar del diccionario si no tiene acciones
        if self.shareholders[player_id] == 0:
            del self.shareholders[player_id]
            
        self.update_price(price)
        return True
    
    def update_price(self, new_price: float):
        """Actualiza el precio de la acción"""
        self.current_price = max(new_price, 0.01)  # Mínimo $0.01
        self.price_history.append(self.current_price)
        
        # Limitar historial a últimas 50 rondas
        if len(self.price_history) > 50:
            self.price_history.pop(0)
    
    def apply_price_change(self, percent_change: float):
        """Aplica un cambio porcentual al precio"""
        new_price = self.current_price * (1 + percent_change / 100)
        self.update_price(new_price)
    
    def get_shareholder_info(self, player_id: str) -> Dict:
        """Retorna información sobre las acciones de un jugador"""
        shares = self.shareholders.get(player_id, 0)
        percentage = (shares / self.total_shares) * 100 if self.total_shares > 0 else 0
        value = shares * self.current_price
        
        return {
            'shares': shares,
            'percentage': round(percentage, 2),
            'value': round(value, 2),
            'is_majority': shares > self.total_shares * 0.5
        }
    
    def can_merge(self) -> bool:
        """Verifica si la empresa puede ser fusionada (tiene dueño mayoritario)"""
        return self.owner is not None and self.status == CompanyStatus.ACTIVE
    
    def merge_with(self, other: 'Company') -> 'Company':
        """
        Fusiona esta empresa con otra.
        Retorna una nueva empresa fusionada.
        """
        if self.sector != other.sector:
            raise ValueError("Solo se pueden fusionar empresas del mismo sector")
        
        # Crear empresa fusionada
        merged_name = f"{self.name}-{other.name}"
        merged_id = f"{self.company_id}_{other.company_id}"
        
        merged = Company(
            company_id=merged_id,
            name=merged_name,
            sector=self.sector,
            initial_price=(self.current_price + other.current_price) / 2,
            total_shares=self.total_shares + other.total_shares
        )
        
        # Transferir accionistas
        for pid, shares in {**self.shareholders, **other.shareholders}.items():
            merged.shareholders[pid] = shares
            
        # Cambiar estado de empresas originales
        self.status = CompanyStatus.MERGED
        other.status = CompanyStatus.MERGED
        
        return merged
    
    def get_info(self) -> Dict:
        """Retorna información completa de la empresa"""
        return {
            'id': self.company_id,
            'name': self.name,
            'sector': self.sector.name,
            'price': round(self.current_price, 2),
            'change': round(self.price_change, 2),
            'market_cap': round(self.market_cap, 2),
            'available_shares': self.available_shares,
            'total_shares': self.total_shares,
            'status': self.status.value,
            'owner': self.owner,
            'shareholders_count': len(self.shareholders)
        }
    
    def __str__(self) -> str:
        change_symbol = "↑" if self.price_change >= 0 else "↓"
        return f"{self.name} ({self.sector.name}): ${self.current_price:.2f} {change_symbol} {abs(self.price_change):.1f}%"
