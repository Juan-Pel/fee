"""
Game - Lógica principal del juego Stock Market Tycoon
"""
from typing import Dict, List, Optional, Tuple
import random

from .player import Player
from .market import Market
from .events import EventManager, Event
from .cards import CardDeck, Card
from .company import CompanyStatus


class GameMode:
    """Configuración de modos de juego"""
    QUICK = {
        'name': 'Rápida',
        'duration_minutes': 15,
        'max_players': 4,
        'min_players': 2,
        'objective': 'market_value',
        'target_influence': None,
        'event_frequency': 2,
        'initial_cash': 10000,
        'sectors_to_control': None
    }
    
    STANDARD = {
        'name': 'Estándar',
        'duration_minutes': 40,
        'max_players': 6,
        'min_players': 3,
        'objective': 'influence',
        'target_influence': 50,
        'event_frequency': 4,
        'initial_cash': 15000,
        'sectors_to_control': None
    }
    
    EXTENDED = {
        'name': 'Extendida',
        'duration_minutes': 90,
        'max_players': 8,
        'min_players': 4,
        'objective': 'sectors_and_capital',
        'target_influence': None,
        'event_frequency': 5,
        'initial_cash': 20000,
        'sectors_to_control': 3,
        'capital_threshold': 100000
    }


class StockMarketGame:
    """
    Clase principal que gestiona toda la lógica del juego.
    Controla turnos, jugadores, mercado, eventos y condiciones de victoria.
    """
    
    def __init__(self, mode: str = 'standard'):
        self.mode_config = GameMode.STANDARD
        if mode.lower() == 'quick':
            self.mode_config = GameMode.QUICK
        elif mode.lower() == 'extended':
            self.mode_config = GameMode.EXTENDED
        
        # Estado del juego
        self.players: Dict[str, Player] = {}
        self.market = Market()
        self.event_manager = EventManager()
        self.card_deck = CardDeck()
        
        self.current_player_idx = 0
        self.round_number = 0
        self.max_rounds = self.mode_config['duration_minutes'] // 2  # Aproximado
        self.game_over = False
        self.winner: Optional[str] = None
        
        # Configuración inicial
        self.event_manager.set_frequency(self.mode_config['event_frequency'])
        
        # Inicializar empresas
        self._initialize_companies()
    
    def _initialize_companies(self):
        """Crea las empresas iniciales en cada sector"""
        companies_data = [
            # Tecnología
            ('tech1', 'TechCorp', 'Tecnología', 15.0),
            ('tech2', 'InnovateX', 'Tecnología', 12.0),
            ('tech3', 'CyberDyne', 'Tecnología', 18.0),
            
            # Energía
            ('energy1', 'GreenPower', 'Energía', 20.0),
            ('energy2', 'OilMax', 'Energía', 16.0),
            
            # Turismo
            ('tourism1', 'TravelWorld', 'Turismo', 10.0),
            ('tourism2', 'HotelChain', 'Turismo', 14.0),
            
            # Finanzas
            ('finance1', 'BankCorp', 'Finanzas', 25.0),
            ('finance2', 'InvestPro', 'Finanzas', 22.0),
            
            # Salud
            ('health1', 'PharmaCo', 'Salud', 30.0),
            ('health2', 'BioTech', 'Salud', 28.0),
            
            # Inmobiliario
            ('real1', 'EstateDev', 'Inmobiliario', 18.0),
            ('real2', 'PropertyMax', 'Inmobiliario', 15.0),
            
            # Consumo
            ('consumer1', 'RetailGiant', 'Consumo', 12.0),
            ('consumer2', 'FoodCorp', 'Consumo', 10.0),
            
            # Industrial
            ('industrial1', 'ManufactureCo', 'Industrial', 20.0),
            ('industrial2', 'SteelWorks', 'Industrial', 17.0)
        ]
        
        for comp_id, name, sector, price in companies_data:
            self.market.create_company(comp_id, name, sector, price, 1000)
    
    def add_player(self, player_id: str, name: str, is_ai: bool = False) -> Player:
        """Añade un jugador al juego"""
        if len(self.players) >= self.mode_config['max_players']:
            raise ValueError(f"Máximo de jugadores alcanzado ({self.mode_config['max_players']})")
        
        player = Player(
            player_id=player_id,
            name=name,
            is_ai=is_ai,
            cash=self.mode_config['initial_cash'],
            initial_cash=self.mode_config['initial_cash']
        )
        
        self.players[player_id] = player
        
        # Dar 2 cartas iniciales
        cards = self.card_deck.draw(2)
        for card in cards:
            player.add_card(card.card_id)
        
        return player
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Obtiene un jugador por su ID"""
        return self.players.get(player_id)
    
    def get_current_player(self) -> Player:
        """Retorna el jugador actual"""
        player_ids = list(self.players.keys())
        return self.players[player_ids[self.current_player_idx]]
    
    def next_turn(self):
        """Pasa al siguiente turno"""
        player_ids = list(self.players.keys())
        self.current_player_idx = (self.current_player_idx + 1) % len(player_ids)
        
        # Si volvemos al primer jugador, es una nueva ronda
        if self.current_player_idx == 0:
            self.round_number += 1
            self._start_new_round()
    
    def _start_new_round(self):
        """Lógica al inicio de cada ronda"""
        # Actualizar precios del mercado
        self.market.update_prices()
        
        # Verificar eventos
        event = self.event_manager.generate_event(self.round_number)
        if event:
            message = self.event_manager.apply_event(event, self.market)
            print(f"\n{message}")
        
        # Actualizar eventos activos
        expired_messages = self.event_manager.update_active_events(self.market)
        for msg in expired_messages:
            print(f"\n{msg}")
        
        # Dar carta cada 5 rondas
        if self.round_number % 5 == 0:
            for player in self.players.values():
                if not player.is_bankrupt:
                    cards = self.card_deck.draw(1)
                    for card in cards:
                        player.add_card(card.card_id)
        
        # Verificar condiciones de victoria
        self._check_victory_conditions()
    
    def buy_shares(self, player_id: str, company_id: str, quantity: int) -> Tuple[bool, float, str]:
        """Un jugador compra acciones"""
        player = self.get_player(player_id)
        if not player or player.is_bankrupt:
            return False, 0, "Jugador no válido"
        
        success, cost, message = self.market.buy_shares(player_id, company_id, quantity)
        
        if success:
            if player.spend_cash(cost):
                player.add_shares(company_id, quantity)
                player.total_trades += 1
                
                # Verificar si obtuvo mayoría
                company = self.market.get_company(company_id)
                if company and player.check_majority(company_id, company.total_shares):
                    player.companies_owned.add(company_id)
                    player.add_influence(5)
                    message += f" ¡Mayoria obtenida! +5 influencia"
                
                return True, cost, message
            else:
                # Revertir compra si no hay fondos
                self.market.sell_shares(player_id, company_id, quantity)
                return False, 0, "Fondos insuficientes"
        
        return False, 0, message
    
    def sell_shares(self, player_id: str, company_id: str, quantity: int) -> Tuple[bool, float, str]:
        """Un jugador vende acciones"""
        player = self.get_player(player_id)
        if not player or player.is_bankrupt:
            return False, 0, "Jugador no válido"
        
        success, value, message = self.market.sell_shares(player_id, company_id, quantity)
        
        if success:
            player.remove_shares(company_id, quantity)
            player.receive_cash(value)
            player.total_trades += 1
            
            # Verificar si perdió mayoría
            company = self.market.get_company(company_id)
            if company and not player.check_majority(company_id, company.total_shares):
                if company_id in player.companies_owned:
                    player.companies_owned.remove(company_id)
            
            return True, value, message
        
        return False, 0, message
    
    def play_card(self, player_id: str, card_id: str, target: Optional[str] = None) -> Dict:
        """Un jugador usa una carta"""
        player = self.get_player(player_id)
        if not player:
            return {'success': False, 'message': 'Jugador no encontrado'}
        
        if card_id not in player.cards:
            return {'success': False, 'message': 'Carta no encontrada en mano'}
        
        card = self.card_deck.get_card(card_id)
        if not card:
            return {'success': False, 'message': 'Carta no válida'}
        
        result = card.play(self, player_id, target)
        
        if result['success']:
            player.use_card(card_id)
        
        return result
    
    def attempt_merge(self, player_id: str, company1_id: str, company2_id: str) -> Tuple[bool, str]:
        """Intenta fusionar dos empresas"""
        player = self.get_player(player_id)
        if not player:
            return False, "Jugador no válido"
        
        company1 = self.market.get_company(company1_id)
        company2 = self.market.get_company(company2_id)
        
        if not company1 or not company2:
            return False, "Empresa(s) no encontrada(s)"
        
        if company1.sector != company2.sector:
            return False, "Las empresas deben ser del mismo sector"
        
        # Verificar que el jugador tiene mayoría en ambas
        if not player.check_majority(company1_id, company1.total_shares):
            return False, f"No tienes mayoría en {company1.name}"
        
        if not player.check_majority(company2_id, company2.total_shares):
            return False, f"No tienes mayoría en {company2.name}"
        
        # Realizar fusión
        merged_company = company1.merge_with(company2)
        self.market.companies[merged_company.company_id] = merged_company
        
        player.successful_mergers += 1
        player.add_influence(15)  # Bonus por fusión
        
        return True, f"Fusión exitosa: {merged_company.name}. +15 influencia"
    
    def _update_all_portfolio_values(self):
        """Actualiza el valor de mercado de todos los jugadores"""
        company_prices = {cid: c.current_price for cid, c in self.market.companies.items()}
        
        for player in self.players.values():
            player.update_market_value(company_prices)
    
    def _check_victory_conditions(self):
        """Verifica si se han cumplido las condiciones de victoria"""
        self._update_all_portfolio_values()
        
        objective = self.mode_config['objective']
        
        # Verificar bancarrota
        for player in self.players.values():
            if player.net_worth < 1000 and not player.is_bankrupt:
                player.declare_bankruptcy()
        
        active_players = [p for p in self.players.values() if not p.is_bankrupt]
        
        if len(active_players) <= 1 and len(self.players) > 1:
            # Solo queda un jugador
            self.game_over = True
            self.winner = active_players[0].player_id if active_players else None
            return
        
        # Condiciones específicas por modo
        if objective == 'market_value':
            # Modo rápido: verificar si se acabó el tiempo
            if self.round_number >= self.max_rounds:
                self.game_over = True
                best_player = max(active_players, key=lambda p: p.net_worth)
                self.winner = best_player.player_id
        
        elif objective == 'influence':
            # Modo estándar: alcanzar puntos de influencia
            for player in active_players:
                if self.mode_config['target_influence'] and player.influence_points >= self.mode_config['target_influence']:
                    self.game_over = True
                    self.winner = player.player_id
                    return
        
        elif objective == 'sectors_and_capital':
            # Modo extendido: controlar sectores + capital
            self._update_sector_control()
            
            for player in active_players:
                sectors_controlled = len(player.sectors_controlled)
                if (sectors_controlled >= self.mode_config['sectors_to_control'] and 
                    player.net_worth >= self.mode_config.get('capital_threshold', 100000)):
                    self.game_over = True
                    self.winner = player.player_id
                    return
            
            # También verificar por tiempo
            if self.round_number >= self.max_rounds:
                self.game_over = True
                best_player = max(active_players, key=lambda p: (len(p.sectors_controlled), p.net_worth))
                self.winner = best_player.player_id
    
    def _update_sector_control(self):
        """Actualiza qué jugadores controlan cada sector"""
        # Resetear control
        for player in self.players.values():
            player.sectors_controlled.clear()
        
        # Contar empresas por jugador en cada sector
        sector_companies = {}
        for company in self.market.companies.values():
            if company.status != CompanyStatus.ACTIVE:
                continue
            
            sector = company.sector.name
            if sector not in sector_companies:
                sector_companies[sector] = {}
            
            owner = company.owner
            if owner:
                if owner not in sector_companies[sector]:
                    sector_companies[sector][owner] = 0
                sector_companies[sector][owner] += 1
        
        # Determinar control de sector (mayoría de empresas)
        for sector, owners in sector_companies.items():
            if owners:
                total_companies = sum(owners.values())
                for owner, count in owners.items():
                    if count > total_companies / 2:
                        player = self.get_player(owner)
                        if player:
                            player.sectors_controlled.add(sector)
    
    def get_game_state(self) -> Dict:
        """Retorna el estado completo del juego"""
        self._update_all_portfolio_values()
        
        return {
            'round': self.round_number,
            'max_rounds': self.max_rounds,
            'mode': self.mode_config['name'],
            'game_over': self.game_over,
            'winner': self.winner,
            'players': {pid: p.get_portfolio_summary({
                cid: c.get_info() for cid, c in self.market.companies.items()
            }) for pid, p in self.players.items()},
            'market_summary': self.market.get_market_summary(),
            'current_player': list(self.players.keys())[self.current_player_idx] if self.players else None
        }
    
    def get_leaderboard(self) -> List[Dict]:
        """Retorna la clasificación actual de jugadores"""
        self._update_all_portfolio_values()
        
        leaderboard = []
        for player in self.players.values():
            leaderboard.append({
                'rank': 0,  # Se calculará después
                'name': player.name,
                'net_worth': round(player.net_worth, 2),
                'cash': round(player.cash, 2),
                'market_value': round(player.market_value, 2),
                'influence': player.influence_points,
                'companies_owned': len(player.companies_owned),
                'sectors_controlled': len(player.sectors_controlled),
                'is_bankrupt': player.is_bankrupt
            })
        
        # Ordenar por valor neto
        leaderboard.sort(key=lambda x: (-x['net_worth'], -x['influence']))
        
        # Asignar rangos
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1
        
        return leaderboard
    
    def __str__(self) -> str:
        lines = [
            f"=== STOCK MARKET TYCOON ===",
            f"Modo: {self.mode_config['name']}",
            f"Ronda: {self.round_number}/{self.max_rounds}",
            "",
            str(self.market),
            "",
            "=== JUGADORES ==="
        ]
        
        for player in self.players.values():
            lines.append(f"  {player}")
        
        return "\n".join(lines)
