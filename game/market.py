"""
Market - Sistema de mercado que gestiona sectores, empresas y precios
"""
from typing import Dict, List, Optional, Tuple
from .sector import Sector, SectorType
from .company import Company, CompanyStatus


class Market:
    """
    Gestiona el mercado bursátil completo: sectores, empresas, precios dinámicos.
    Implementa la lógica de oferta/demanda y actualizaciones de precios.
    """
    
    def __init__(self):
        self.sectors: Dict[str, Sector] = {}
        self.companies: Dict[str, Company] = {}
        self.market_trend = 0.0  # Tendencia general del mercado (-1 a 1)
        self.volatility_modifier = 1.0  # Multiplicador de volatilidad
        self.round_number = 0
        
        # Inicializar sectores por defecto
        self._initialize_default_sectors()
        
    def _initialize_default_sectors(self):
        """Crea los sectores económicos base"""
        default_sectors = [
            (SectorType.TECHNOLOGY, 150.0, 0.15),  # Mayor volatilidad
            (SectorType.ENERGY, 120.0, 0.12),
            (SectorType.TOURISM, 100.0, 0.18),
            (SectorType.FINANCE, 130.0, 0.10),
            (SectorType.HEALTHCARE, 140.0, 0.08),  # Menor volatilidad
            (SectorType.REAL_ESTATE, 110.0, 0.14),
            (SectorType.CONSUMER, 100.0, 0.10),
            (SectorType.INDUSTRIAL, 105.0, 0.11)
        ]
        
        for sector_type, base_value, volatility in default_sectors:
            sector = Sector(sector_type, base_value)
            sector.volatility = volatility
            self.sectors[sector_type.value] = sector
    
    def create_company(self, company_id: str, name: str, sector_name: str,
                       initial_price: float = 10.0, total_shares: int = 1000) -> Company:
        """Crea una nueva empresa en un sector"""
        if sector_name not in self.sectors:
            raise ValueError(f"Sector '{sector_name}' no existe")
            
        sector = self.sectors[sector_name]
        company = Company(company_id, name, sector, initial_price, total_shares)
        self.companies[company_id] = company
        return company
    
    def get_company(self, company_id: str) -> Optional[Company]:
        """Obtiene una empresa por su ID"""
        return self.companies.get(company_id)
    
    def get_sector(self, sector_name: str) -> Optional[Sector]:
        """Obtiene un sector por su nombre"""
        return self.sectors.get(sector_name)
    
    def buy_shares(self, player_id: str, company_id: str, quantity: int) -> Tuple[bool, float, str]:
        """
        Un jugador compra acciones de una empresa.
        Retorna: (éxito, costo_total, mensaje)
        """
        company = self.get_company(company_id)
        if not company:
            return False, 0, "Empresa no encontrada"
            
        if quantity <= 0:
            return False, 0, "Cantidad inválida"
            
        if quantity > company.available_shares:
            return False, 0, f"Solo hay {company.available_shares} acciones disponibles"
        
        # Calcular precio con impacto de mercado
        base_cost = quantity * company.current_price
        impact_factor = 1 + (quantity / company.total_shares) * 0.1  # 10% max impact
        total_cost = base_cost * impact_factor
        
        # Ejecutar compra
        if company.buy_shares(player_id, quantity, company.current_price * impact_factor):
            # Actualizar precio del sector ligeramente al alza
            company.sector.update_value(0.1)  # +0.1% por demanda
            return True, total_cost, f"Compraste {quantity} acciones de {company.name}"
        
        return False, 0, "Error en la compra"
    
    def sell_shares(self, player_id: str, company_id: str, quantity: int) -> Tuple[bool, float, str]:
        """
        Un jugador vende acciones de una empresa.
        Retorna: (éxito, ganancia_total, mensaje)
        """
        company = self.get_company(company_id)
        if not company:
            return False, 0, "Empresa no encontrada"
            
        if quantity <= 0:
            return False, 0, "Cantidad inválida"
        
        # Verificar que el jugador tiene las acciones
        current_holdings = company.shareholders.get(player_id, 0)
        if quantity > current_holdings:
            return False, 0, f"Solo tienes {current_holdings} acciones"
        
        # Calcular precio con impacto de mercado
        base_value = quantity * company.current_price
        impact_factor = 1 - (quantity / company.total_shares) * 0.1  # Precio baja por venta masiva
        total_value = base_value * impact_factor
        
        # Ejecutar venta
        if company.sell_shares(player_id, quantity, company.current_price * impact_factor):
            # Actualizar precio del sector ligeramente a la baja
            company.sector.update_value(-0.1)  # -0.1% por oferta
            return True, total_value, f"Vendiste {quantity} acciones de {company.name}"
        
        return False, 0, "Error en la venta"
    
    def update_prices(self):
        """Actualiza todos los precios basándose en oferta/demanda y tendencias"""
        self.round_number += 1
        
        for company in self.companies.values():
            if company.status != CompanyStatus.ACTIVE:
                continue
                
            # Factores que afectan el precio
            demand_factor = 0
            supply_factor = 0
            
            # Demanda: porcentaje de acciones compradas
            bought_ratio = (company.total_shares - company.available_shares) / company.total_shares
            demand_factor = bought_ratio * 2  # Hasta +2%
            
            # Oferta: presión vendedora
            if company.available_shares > company.total_shares * 0.8:
                supply_factor = -1  # -1% si hay mucha oferta
            
            # Tendencia del sector
            sector_trend = company.sector.trend * 3  # Amplificar tendencia
            
            # Volatilidad aleatoria
            import random
            noise = random.gauss(0, company.sector.volatility * self.volatility_modifier)
            
            # Calcular cambio total
            total_change = demand_factor + supply_factor + sector_trend + noise
            
            # Aplicar cambio
            company.apply_price_change(total_change)
        
        # Actualizar valores de sectores
        for sector in self.sectors.values():
            sector.update_value(self.market_trend * 0.5)
    
    def apply_sector_event(self, sector_name: str, percent_change: float):
        """Aplica un evento que afecta a todo un sector"""
        if sector_name in self.sectors:
            sector = self.sectors[sector_name]
            sector.update_value(percent_change)
            
            # Afectar a todas las empresas del sector
            for company in self.companies.values():
                if company.sector == sector and company.status == CompanyStatus.ACTIVE:
                    company.apply_price_change(percent_change * 0.8)  # Empresas se mueven un 80% del sector
    
    def get_market_summary(self) -> Dict:
        """Retorna un resumen completo del mercado"""
        sectors_info = {name: s.get_info() for name, s in self.sectors.items()}
        companies_info = {cid: c.get_info() for cid, c in self.companies.items() 
                         if c.status == CompanyStatus.ACTIVE}
        
        total_market_cap = sum(c.market_cap for c in self.companies.values() 
                               if c.status == CompanyStatus.ACTIVE)
        
        return {
            'round': self.round_number,
            'sectors': sectors_info,
            'companies': companies_info,
            'total_market_cap': round(total_market_cap, 2),
            'market_trend': self.market_trend,
            'volatility': self.volatility_modifier,
            'active_companies': len([c for c in self.companies.values() 
                                    if c.status == CompanyStatus.ACTIVE])
        }
    
    def get_companies_by_sector(self, sector_name: str) -> List[Company]:
        """Retorna todas las empresas activas de un sector"""
        return [c for c in self.companies.values() 
                if c.sector.name == sector_name and c.status == CompanyStatus.ACTIVE]
    
    def check_majority_owners(self) -> Dict[str, List[str]]:
        """Verifica qué jugadores tienen mayoría en cada empresa"""
        owners = {}
        for company in self.companies.values():
            if company.status == CompanyStatus.ACTIVE and company.owner:
                if company.owner not in owners:
                    owners[company.owner] = []
                owners[company.owner].append(company.company_id)
        return owners
    
    def __str__(self) -> str:
        lines = ["=== MERCADO BURSÁTIL ===", f"Ronda: {self.round_number}"]
        for sector in self.sectors.values():
            lines.append(f"  {sector}")
        return "\n".join(lines)
