"""
Lógica central del juego Stock Market Tycoon
Gestiona empresas, jugadores, turnos y eventos
"""
import random
from datetime import datetime

class Company:
    def __init__(self, id, name, sector, initial_price=100):
        self.id = id
        self.name = name
        self.sector = sector
        self.price = initial_price
        self.total_shares = 1000
        self.available_shares = 1000
        self.price_history = [initial_price]
    
    def get_trend(self):
        if len(self.price_history) < 2:
            return 'stable'
        if self.price > self.price_history[-2]:
            return 'up'
        elif self.price < self.price_history[-2]:
            return 'down'
        return 'stable'
    
    def update_price(self, change_percent):
        """Actualiza el precio con un porcentaje de cambio"""
        change = self.price * (change_percent / 100)
        self.price = max(1, self.price + change)
        self.price_history.append(self.price)
    
    def get_available_shares(self):
        return self.available_shares

class Player:
    def __init__(self, id, name, is_bot=False):
        self.id = id
        self.name = name
        self.capital = 10000  # Capital inicial
        self.portfolio = {}  # {company_id: quantity}
        self.is_bot = is_bot
        self.influence_points = 0
    
    def get_market_value(self, companies):
        """Calcula el valor total de mercado del jugador"""
        value = self.capital
        for company_id, quantity in self.portfolio.items():
            if company_id in companies:
                value += companies[company_id].price * quantity
        return value
    
    def can_buy(self, company, quantity):
        cost = company.price * quantity
        return self.capital >= cost and company.available_shares >= quantity
    
    def buy(self, company, quantity):
        cost = company.price * quantity
        if not self.can_buy(company, quantity):
            return False
        
        self.capital -= cost
        company.available_shares -= quantity
        
        if company.id not in self.portfolio:
            self.portfolio[company.id] = 0
        self.portfolio[company.id] += quantity
        
        # Impacto en el precio (demanda)
        price_increase = (quantity / company.total_shares) * 5
        company.update_price(price_increase)
        
        return True
    
    def sell(self, company, quantity):
        if company.id not in self.portfolio or self.portfolio[company.id] < quantity:
            return False
        
        revenue = company.price * quantity
        self.capital += revenue
        company.available_shares += quantity
        self.portfolio[company.id] -= quantity
        
        if self.portfolio[company.id] == 0:
            del self.portfolio[company.id]
        
        # Impacto en el precio (oferta)
        price_decrease = (quantity / company.total_shares) * 5
        company.update_price(-price_decrease)
        
        return True

class StockMarketGame:
    def __init__(self, max_turns=20, turn_duration=60, enable_events=True):
        self.max_turns = max_turns
        self.turn_duration = turn_duration
        self.enable_events = enable_events
        self.phase = 'LOBBY'  # LOBBY, PLAYING, GAME_OVER
        self.current_turn = 0
        self.current_round = 1
        self.turn_timer = turn_duration
        self.game_over = False
        self.players = {}
        self.companies = {}
        self.event_log = []
        self.current_player_id = None
        
        # Inicializar empresas por sectores
        self._init_companies()
    
    def _init_companies(self):
        sectors = ['Tecnología', 'Energía', 'Finanzas', 'Salud']
        company_names = [
            ('TechCorp', 'Tecnología'), ('DataSys', 'Tecnología'),
            ('OilMax', 'Energía'), ('GreenPower', 'Energía'),
            ('BankPro', 'Finanzas'), ('InvestCo', 'Finanzas'),
            ('PharmaLife', 'Salud'), ('MediCare', 'Salud')
        ]
        
        for i, (name, sector) in enumerate(company_names):
            self.companies[str(i)] = Company(str(i), name, sector, initial_price=random.randint(80, 120))
    
    def add_player(self, player_id, name, is_bot=False):
        self.players[player_id] = Player(player_id, name, is_bot)
    
    def start(self):
        if len(self.players) < 2:
            return False
        
        self.phase = 'PLAYING'
        self.current_turn = 0
        self.current_round = 1
        self.turn_timer = self.turn_duration
        player_ids = list(self.players.keys())
        self.current_player_id = player_ids[0]
        self.game_over = False
        
        self._log_event("Juego iniciado", "info")
        return True
    
    def next_turn(self):
        if self.phase != 'PLAYING':
            return
        
        player_ids = list(self.players.keys())
        current_index = player_ids.index(self.current_player_id) if self.current_player_id in player_ids else 0
        next_index = (current_index + 1) % len(player_ids)
        
        self.current_player_id = player_ids[next_index]
        self.current_turn += 1
        
        # Nueva ronda
        if next_index == 0:
            self.current_round += 1
            self._process_round_events()
        
        # Verificar fin del juego
        if self.current_turn >= self.max_turns * len(self.players):
            self.end_game()
            return
        
        self.turn_timer = self.turn_duration
        
        # Si el siguiente es bot, ejecutar su turno
        next_player = self.players[self.current_player_id]
        if next_player.is_bot:
            self._execute_bot_turn(next_player)
    
    def _execute_bot_turn(self, bot):
        """IA básica para bots"""
        import time
        time.sleep(1)  # Pequeña pausa para realismo
        
        # Decisión simple: comprar si tiene capital y hay acciones disponibles
        available_companies = [c for c in self.companies.values() if c.available_shares > 0]
        
        if available_companies and bot.capital > 200:
            company = random.choice(available_companies)
            max_affordable = int(bot.capital / company.price)
            quantity = min(random.randint(1, 5), max_affordable, company.available_shares)
            
            if quantity > 0:
                bot.buy(company, quantity)
                self._log_event(f"{bot.name} compró {quantity} acciones de {company.name}", "bot")
        
        self.next_turn()
    
    def _process_round_events(self):
        """Procesa eventos al inicio de cada ronda"""
        if not self.enable_events:
            return
        
        # 30% de probabilidad de evento
        if random.random() < 0.3:
            event_type = random.choice(['boom', 'crisis', 'regulation'])
            
            if event_type == 'boom':
                sector = random.choice(list(set(c.sector for c in self.companies.values())))
                for company in self.companies.values():
                    if company.sector == sector:
                        company.update_price(random.randint(10, 25))
                self._log_event(f"¡Boom económico en {sector}! +10-25%", "event")
            
            elif event_type == 'crisis':
                sector = random.choice(list(set(c.sector for c in self.companies.values())))
                for company in self.companies.values():
                    if company.sector == sector:
                        company.update_price(random.randint(-25, -10))
                self._log_event(f"Crisis en {sector}! -10-25%", "event")
            
            elif event_type == 'regulation':
                for company in self.companies.values():
                    company.update_price(random.randint(-5, 5))
                self._log_event("Nuevas regulaciones de mercado", "event")
    
    def buy_shares(self, player_id, company_id, quantity):
        if player_id not in self.players or company_id not in self.companies:
            return False, "Datos inválidos"
        
        if self.current_player_id != player_id:
            return False, "No es tu turno"
        
        player = self.players[player_id]
        company = self.companies[company_id]
        
        if player.buy(company, quantity):
            self._log_event(f"{player.name} compró {quantity} acciones de {company.name}", "action")
            return True, "Compra exitosa"
        
        return False, "Fondo insuficiente o acciones no disponibles"
    
    def sell_shares(self, player_id, company_id, quantity):
        if player_id not in self.players or company_id not in self.companies:
            return False, "Datos inválidos"
        
        if self.current_player_id != player_id:
            return False, "No es tu turno"
        
        player = self.players[player_id]
        company = self.companies[company_id]
        
        if player.sell(company, quantity):
            self._log_event(f"{player.name} vendió {quantity} acciones de {company.name}", "action")
            return True, "Venta exitosa"
        
        return False, "No tienes suficientes acciones"
    
    def _log_event(self, message, event_type="info"):
        self.event_log.append({
            'message': message,
            'type': event_type,
            'timestamp': datetime.now().isoformat()
        })
    
    def end_game(self):
        self.phase = 'GAME_OVER'
        self.game_over = True
        self._log_event("Juego terminado", "end")
    
    def get_winner(self):
        if not self.game_over:
            return None
        
        best_player = max(self.players.values(), key=lambda p: p.get_market_value(self.companies))
        return {
            'id': best_player.id,
            'name': best_player.name,
            'market_value': best_player.get_market_value(self.companies)
        }
