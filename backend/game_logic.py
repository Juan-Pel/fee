import random
import time
from datetime import datetime

class Company:
    def __init__(self, id, name, sector, base_price):
        self.id = id
        self.name = name
        self.sector = sector
        self.base_price = base_price
        self.current_price = base_price
        self.owner = None
        self.shares_available = 100
        self.price_history = [base_price]
        self.disaster_effect = None  # Para fenómenos naturales
        
    def update_price(self, market_modifier=1.0):
        change = random.uniform(-0.05, 0.05) * market_modifier
        if self.disaster_effect:
            change *= self.disaster_effect['multiplier']
        self.current_price = max(1, self.current_price * (1 + change))
        self.price_history.append(self.current_price)
        if len(self.price_history) > 20:
            self.price_history.pop(0)

class Player:
    def __init__(self, id, name, is_bot=False):
        self.id = id
        self.name = name
        self.is_bot = is_bot
        self.cash = 10000
        self.portfolio = {}  # {company_id: quantity}
        self.hand_cards = []
        self.influence_points = 0
        
    def get_portfolio_value(self, companies):
        value = self.cash
        for comp_id, qty in self.portfolio.items():
            company = next((c for c in companies if c.id == comp_id), None)
            if company:
                value += company.current_price * qty
        return value

class Card:
    def __init__(self, id, name, card_type, effect_data):
        self.id = id
        self.name = name
        self.card_type = card_type  # 'event', 'action', 'disaster'
        self.effect_data = effect_data
        self.description = ""
        
    def apply_effect(self, game_state):
        if self.card_type == 'disaster':
            target_company = game_state['companies'].get(self.effect_data['target'])
            if target_company:
                target_company.disaster_effect = {
                    'multiplier': self.effect_data['multiplier'],
                    'duration': self.effect_data.get('duration', 999)
                }
                return f"{target_company.name} ha sufrido un desastre! Sus acciones se reducen."
        elif self.card_type == 'event':
            sector = self.effect_data.get('sector')
            modifier = self.effect_data.get('modifier', 1.0)
            for comp in game_state['companies'].values():
                if not sector or comp.sector == sector:
                    comp.update_price(modifier)
            return f"Evento de mercado: El sector {sector or 'general'} ha sido afectado."
        return "Carta aplicada con éxito."

class StockMarketGame:
    def __init__(self, game_id, host_id, config=None):
        self.game_id = game_id
        self.host_id = host_id
        self.config = config or {
            'turn_time': 60,
            'max_rounds': 10,
            'events_enabled': True,
            'trade_enabled': True
        }
        self.players = {}
        self.companies = {}
        self.deck = []
        self.discard_pile = []
        self.current_turn_index = 0
        self.player_order = []
        self.current_round = 1
        self.turn_start_time = None
        self.game_status = 'waiting'  # waiting, playing, finished
        self.market_events = []
        self.trade_offers = {}
        self.board_rotation = {}  # Rotación individual por jugador
        
        self._initialize_companies()
        self._initialize_deck()
        
    def _initialize_companies(self):
        sectors = ['Tecnología', 'Energía', 'Turismo', 'Finanzas', 'Salud', 'Inmobiliario', 'Consumo', 'Industrial']
        company_names = [
            ("TechCorp", "Tecnología", 150), ("SoftSys", "Tecnología", 120),
            ("OilMax", "Energía", 200), ("GreenPower", "Energía", 180),
            ("TravelJoy", "Turismo", 90), ("HotelLux", "Turismo", 110),
            ("BankSafe", "Finanzas", 250), ("InvestPro", "Finanzas", 220),
            ("MediCare", "Salud", 170), ("PharmaLife", "Salud", 190),
            ("BuildIt", "Inmobiliario", 140), ("EstateGroup", "Inmobiliario", 160),
            ("FoodCo", "Consumo", 80), ("RetailKing", "Consumo", 100),
            ("AutoMake", "Industrial", 130), ("SteelWorks", "Industrial", 150)
        ]
        
        for i, (name, sector, price) in enumerate(company_names):
            self.companies[i] = Company(i, name, sector, price)
            
    def _initialize_deck(self):
        disasters = [
            {"name": "Tornado en Planta Eléctrica", "type": "disaster", "target_sector": "Energía", "mult": 0.7, "dur": 3},
            {"name": "Meteorito en Resort", "type": "disaster", "target_sector": "Turismo", "mult": 0.1, "dur": 999},
            {"name": "Demanda Judicial Masiva", "type": "disaster", "target_sector": "Salud", "mult": 0.6, "dur": 4},
            {"name": "Crisis Hipotecaria", "type": "disaster", "target_sector": "Inmobiliario", "mult": 0.5, "dur": 5}
        ]
        
        events = [
            {"name": "Boom Tecnológico", "type": "event", "sector": "Tecnología", "mod": 1.3},
            {"name": "Subida de Tipos de Interés", "type": "event", "sector": "Finanzas", "mod": 1.15},
            {"name": "Nueva Pandemia", "type": "event", "sector": "Salud", "mod": 1.4},
            {"name": "Acuerdo Comercial Global", "type": "event", "sector": "Industrial", "mod": 1.25}
        ]
        
        actions = [
            {"name": "Adquisición Hostil", "type": "action", "effect": "steal_shares"},
            {"name": "Soborno Directivo", "type": "action", "effect": "cash_gift"},
            {"name": "Fusión Amistosa", "type": "action", "effect": "merge_bonus"}
        ]
        
        card_id = 0
        for data in disasters:
            self.deck.append(Card(card_id, data['name'], 'disaster', {
                'target_sector': data['target_sector'], 
                'multiplier': data['mult'], 
                'duration': data['dur']
            }))
            card_id += 1
            
        for data in events:
            self.deck.append(Card(card_id, data['name'], 'event', {
                'sector': data['sector'], 
                'modifier': data['mod']
            }))
            card_id += 1
            
        random.shuffle(self.deck)
        
    def add_player(self, player_id, name, is_bot=False):
        if len(self.players) >= 8:
            return False
        self.players[player_id] = Player(player_id, name, is_bot)
        self.player_order.append(player_id)
        if len(self.players) == 1:
            self.host_id = player_id
        return True
        
    def start_game(self):
        if len(self.players) < 2:
            return False
        self.game_status = 'playing'
        self.current_round = 1
        self._next_turn()
        return True
        
    def _next_turn(self):
        if not self.player_order:
            return
            
        self.current_turn_index = (self.current_turn_index) % len(self.player_order)
        current_player_id = self.player_order[self.current_turn_index]
        self.turn_start_time = time.time()
        
        # Repartir carta aleatoria al jugador si es su turno y tiene menos de 3
        player = self.players[current_player_id]
        if len(player.hand_cards) < 3 and self.deck:
            card = self.deck.pop()
            player.hand_cards.append(card)
            
        return current_player_id
        
    def process_turn(self, player_id, action_type, action_data):
        if self.game_status != 'playing':
            return {'success': False, 'message': 'El juego no ha comenzado'}
            
        current_player_id = self.player_order[self.current_turn_index]
        if player_id != current_player_id:
            return {'success': False, 'message': 'No es tu turno'}
            
        # Verificar tiempo
        if self.turn_start_time and (time.time() - self.turn_start_time) > self.config['turn_time']:
            return {'success': False, 'message': 'Se agotó el tiempo de tu turno'}
            
        player = self.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Jugador no encontrado'}
            
        success = False
        message = ""
        
        if action_type == 'buy':
            comp_id = action_data.get('company_id')
            qty = action_data.get('quantity', 1)
            company = self.companies.get(comp_id)
            
            if company and company.shares_available >= qty:
                cost = company.current_price * qty
                if player.cash >= cost:
                    player.cash -= cost
                    company.shares_available -= qty
                    player.portfolio[comp_id] = player.portfolio.get(comp_id, 0) + qty
                    success = True
                    message = f"Compraste {qty} acciones de {company.name}"
                else:
                    message = "Fondo insuficiente"
            else:
                message = "Acciones no disponibles"
                
        elif action_type == 'sell':
            comp_id = action_data.get('company_id')
            qty = action_data.get('quantity', 1)
            company = self.companies.get(comp_id)
            
            if company and player.portfolio.get(comp_id, 0) >= qty:
                gain = company.current_price * qty
                player.cash += gain
                player.portfolio[comp_id] -= qty
                if player.portfolio[comp_id] == 0:
                    del player.portfolio[comp_id]
                company.shares_available += qty
                success = True
                message = f"Vendiste {qty} acciones de {company.name}"
            else:
                message = "No tienes suficientes acciones"
                
        elif action_type == 'play_card':
            card_idx = action_data.get('card_index')
            if 0 <= card_idx < len(player.hand_cards):
                card = player.hand_cards.pop(card_idx)
                game_state = {'companies': self.companies}
                msg = card.apply_effect(game_state)
                self.discard_pile.append(card)
                success = True
                message = msg
            else:
                message = "Carta inválida"
                
        elif action_type == 'trade_offer':
            target_id = action_data.get('target_id')
            offer = action_data.get('offer') # {give: {cash, shares}, receive: {cash, shares}}
            if target_id in self.players:
                trade_id = f"{player_id}_{target_id}_{time.time()}"
                self.trade_offers[trade_id] = {
                    'from': player_id,
                    'to': target_id,
                    'offer': offer,
                    'status': 'pending'
                }
                success = True
                message = "Oferta de intercambio enviada"
            else:
                message = "Jugador objetivo no encontrado"
                
        if success:
            # Actualizar precios de mercado tras acción
            for comp in self.companies.values():
                comp.update_price()
                
        return {'success': success, 'message': message}
        
    def resolve_trade(self, trade_id, accept):
        if trade_id not in self.trade_offers:
            return False
            
        trade = self.trade_offers[trade_id]
        if not accept:
            trade['status'] = 'rejected'
            return False
            
        p1 = self.players[trade['from']]
        p2 = self.players[trade['to']]
        offer = trade['offer']
        
        # Validar nuevamente antes de ejecutar
        if p1.cash < offer['give'].get('cash', 0):
            return False
            
        # Ejecutar intercambio
        p1.cash -= offer['give'].get('cash', 0)
        p1.cash += offer['receive'].get('cash', 0)
        p2.cash += offer['give'].get('cash', 0)
        p2.cash -= offer['receive'].get('cash', 0)
        
        # Intercambio de acciones (simplificado)
        for comp_id, qty in offer['give'].get('shares', {}).items():
            if p1.portfolio.get(comp_id, 0) >= qty:
                p1.portfolio[comp_id] -= qty
                p2.portfolio[comp_id] = p2.portfolio.get(comp_id, 0) + qty
                
        trade['status'] = 'completed'
        return True
        
    def advance_turn(self):
        if self.game_status != 'playing':
            return
            
        # Mover al siguiente jugador
        self.current_turn_index = (self.current_turn_index + 1) % len(self.player_order)
        
        # Si volvemos al inicio, nueva ronda
        if self.current_turn_index == 0:
            self.current_round += 1
            if self.current_round > self.config['max_rounds']:
                self.end_game()
                return None
                
        # Verificar eventos aleatorios (10% probabilidad por turno)
        event_msg = None
        if self.config['events_enabled'] and random.random() < 0.1 and self.deck:
            # Sacar carta de evento del mazo si es de tipo evento
            # En una implementación real, esto sería más robusto
            pass
            
        return self._next_turn()
        
    def end_game(self):
        self.game_status = 'finished'
        # Calcular ganadores
        scores = []
        for pid, player in self.players.items():
            total_val = player.get_portfolio_value(list(self.companies.values()))
            scores.append({'id': pid, 'name': player.name, 'value': total_val})
            
        scores.sort(key=lambda x: x['value'], reverse=True)
        return scores
        
    def get_game_state(self, viewer_id):
        # Preparar estado visible para el jugador
        # Ocultar cartas y decisiones privadas de otros jugadores/bots
        visible_companies = {}
        for cid, comp in self.companies.items():
            visible_companies[cid] = {
                'id': comp.id,
                'name': comp.name,
                'sector': comp.sector,
                'price': comp.current_price,
                'history': comp.price_history[-10:],
                'available': comp.shares_available,
                'disaster': comp.disaster_effect is not None
            }
            
        visible_players = []
        for pid, p in self.players.items():
            p_data = {
                'id': p.id,
                'name': p.name,
                'cash': p.cash,
                'influence': p.influence_points,
                'total_value': p.get_portfolio_value(list(self.companies.values())),
                'is_bot': p.is_bot
            }
            # Solo mostrar portafolio detallado si es el propio jugador
            if pid == viewer_id:
                p_data['portfolio'] = p.portfolio
                p_data['hand'] = [{'name': c.name, 'type': c.card_type} for c in p.hand_cards]
            else:
                # Mostrar resumen genérico para otros
                p_data['portfolio_count'] = sum(p.portfolio.values())
                
            visible_players.append(p_data)
            
        active_player_id = self.player_order[self.current_turn_index] if self.player_order else None
        time_elapsed = 0
        if self.turn_start_time and self.game_status == 'playing':
            time_elapsed = time.time() - self.turn_start_time
            
        return {
            'game_id': self.game_id,
            'status': self.game_status,
            'round': self.current_round,
            'active_player': active_player_id,
            'turn_time_left': max(0, self.config['turn_time'] - time_elapsed),
            'companies': visible_companies,
            'players': visible_players,
            'market_events': self.market_events[-5:], # Últimos 5 eventos
            'trade_offers': [t for t in self.trade_offers.values() if t['to'] == viewer_id and t['status'] == 'pending'],
            'board_rotation': self.board_rotation.get(viewer_id, 0)
        }

    def update_board_rotation(self, player_id, rotation):
        self.board_rotation[player_id] = rotation
