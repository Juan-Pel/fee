"""
Sector - Representa un sector económico del mercado
"""
from typing import List, Dict, Optional
from enum import Enum


class SectorType(Enum):
    """Tipos de sectores económicos disponibles"""
    TECHNOLOGY = "Tecnología"
    ENERGY = "Energía"
    TOURISM = "Turismo"
    FINANCE = "Finanzas"
    HEALTHCARE = "Salud"
    REAL_ESTATE = "Inmobiliario"
    CONSUMER = "Consumo"
    INDUSTRIAL = "Industrial"


class Sector:
    """
    Representa un sector económico que contiene múltiples empresas.
    El valor del sector cambia dinámicamente según eventos y tendencias.
    """
    
    def __init__(self, sector_type: SectorType, base_value: float = 100.0):
        self.sector_type = sector_type
        self.base_value = base_value
        self.current_value = base_value
        self.companies: List[str] = []  # IDs de empresas en este sector
        self.modifier = 1.0  # Multiplicador de valor actual
        self.trend = 0.0  # Tendencia positiva o negativa (-1 a 1)
        self.volatility = 0.1  # Volatilidad del sector (0 a 1)
        
    @property
    def name(self) -> str:
        return self.sector_type.value
    
    @property
    def value_change(self) -> float:
        """Cambio porcentual respecto al valor base"""
        return ((self.current_value - self.base_value) / self.base_value) * 100
    
    def update_value(self, change_percent: float):
        """Actualiza el valor del sector basado en un cambio porcentual"""
        self.current_value *= (1 + change_percent / 100)
        self.current_value = max(self.current_value, 1)  # Mínimo valor 1
        
    def apply_modifier(self, modifier: float):
        """Aplica un multiplicador al valor del sector"""
        self.modifier *= modifier
        self.current_value = self.base_value * self.modifier
        
    def add_company(self, company_id: str):
        """Añade una empresa al sector"""
        if company_id not in self.companies:
            self.companies.append(company_id)
            
    def remove_company(self, company_id: str):
        """Elimina una empresa del sector"""
        if company_id in self.companies:
            self.companies.remove(company_id)
            
    def get_info(self) -> Dict:
        """Retorna información completa del sector"""
        return {
            'name': self.name,
            'base_value': self.base_value,
            'current_value': round(self.current_value, 2),
            'change': round(self.value_change, 2),
            'companies_count': len(self.companies),
            'trend': self.trend,
            'volatility': self.volatility
        }
    
    def __str__(self) -> str:
        change_symbol = "↑" if self.value_change >= 0 else "↓"
        return f"{self.name}: ${self.current_value:.2f} {change_symbol} {abs(self.value_change):.1f}%"
