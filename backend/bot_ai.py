import random
import time

class BotAI:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty  # easy, medium, hard
        self.risk_tolerance = 0.5
        if difficulty == 'easy':
            self.risk_tolerance = 0.3
        elif difficulty == 'hard':
            self.risk_tolerance = 0.8
            
    def decide_action(self, player, companies, game_state):
        """
        Decide qué acción tomar basado en el estado actual.
        Retorna (action_type, action_data)
        """
        # Analizar mercado
        opportunities = []
        for cid, comp in companies.items():
            # Calcular tendencia simple
            if len(comp.price_history) >= 2:
                trend = (comp.current_price - comp.price_history[-2]) / comp.price_history[-2]
                
                # Si precio bajo y tendencia positiva o estable -> Comprar
                if comp.current_price < comp.base_price * 0.9 and trend > -0.02:
                    opportunities.append(('buy', cid, 'undervalued'))
                # Si precio alto y tendencia negativa -> Vender
                elif comp.current_price > comp.base_price * 1.2 and trend < 0:
                    opportunities.append(('sell', cid, 'overvalued'))
                    
        # Decidir acción
        if not opportunities:
            # Acción por defecto: comprar algo aleatorio si tiene dinero
            if player.cash > 2000:
                affordable = [c for c in companies.values() if c.current_price < player.cash * 0.3]
                if affordable:
                    target = random.choice(affordable)
                    return ('buy', {'company_id': target.id, 'quantity': 1})
            return ('pass', {})
            
        # Seleccionar mejor oportunidad basada en tolerancia al riesgo
        action_type, comp_id, reason = random.choice(opportunities)
        
        if action_type == 'buy':
            company = companies[comp_id]
            max_affordable = int(player.cash / company.current_price)
            qty = min(max_affordable, random.randint(1, 3))
            if qty > 0:
                return ('buy', {'company_id': comp_id, 'quantity': qty})
        elif action_type == 'sell':
            owned = player.portfolio.get(comp_id, 0)
            if owned > 0:
                qty = min(owned, random.randint(1, 2))
                return ('sell', {'company_id': comp_id, 'quantity': qty})
                
        # Usar carta si tiene y es buena oportunidad
        if player.hand_cards and random.random() < self.risk_tolerance:
            # Priorizar cartas de desastre sobre oponentes fuertes (no implementado completamente aquí)
            return ('play_card', {'card_index': 0})
            
        return ('pass', {})
