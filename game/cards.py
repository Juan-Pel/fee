"""
Cards - Sistema de cartas de acción que permiten jugadas especiales
"""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class CardType(Enum):
    """Tipos de cartas disponibles"""
    ACTION = "acción"  # Cartas de opciones especiales
    FORTUNE = "fortuna"  # Eventos aleatorios personales
    NEGOTIATION = "negociación"  # Permiten pactar con otros jugadores


@dataclass
class Card:
    """Representa una carta de acción"""
    card_id: str
    name: str
    description: str
    card_type: CardType
    effect: str  # Descripción del efecto
    target: str = "self"  # self, player, company, sector, market
    value: float = 0.0  # Valor numérico del efecto
    duration: int = 1  # Rondas que dura (si aplica)
    
    def can_play(self, game_state: Dict) -> bool:
        """Verifica si la carta puede ser jugada en el estado actual"""
        # Implementación básica, puede ser extendida
        return True
    
    def play(self, game, player_id: str, target: Optional[str] = None) -> Dict:
        """
        Juega la carta y aplica sus efectos.
        Retorna un dict con el resultado de la acción.
        """
        result = {
            'success': False,
            'message': '',
            'effects': []
        }
        
        if not self.can_play(game.get_game_state()):
            result['message'] = "No se puede jugar esta carta ahora"
            return result
        
        # Efectos específicos por tipo de carta
        if self.card_id == "buy_discount":
            result = self._effect_buy_discount(game, player_id, target)
        elif self.card_id == "sell_premium":
            result = self._effect_sell_premium(game, player_id, target)
        elif self.card_id == "market_insight":
            result = self._effect_market_insight(game, player_id)
        elif self.card_id == "hostile_takeover":
            result = self._effect_hostile_takeover(game, player_id, target)
        elif self.card_id == "insider_trading":
            result = self._effect_insider_trading(game, player_id, target)
        elif self.card_id == "bailout":
            result = self._effect_bailout(game, player_id)
        elif self.card_id == "trade_proposal":
            result = self._effect_trade_proposal(game, player_id, target)
        else:
            result['message'] = f"Efecto de carta '{self.name}' no implementado"
        
        return result
    
    def _effect_buy_discount(self, game, player_id: str, target: Optional[str]) -> Dict:
        """Compra acciones con 20% de descuento"""
        if not target:
            return {'success': False, 'message': "Especifica una empresa"}
        
        company = game.market.get_company(target)
        if not company:
            return {'success': False, 'message': "Empresa no encontrada"}
        
        player = game.get_player(player_id)
        discount = 0.2
        discounted_price = company.current_price * (1 - discount)
        
        # Comprar al precio con descuento
        max_affordable = int(player.cash / discounted_price)
        available = min(max_affordable, company.available_shares, 100)
        
        if available <= 0:
            return {'success': False, 'message': "No puedes comprar acciones"}
        
        success, cost, msg = game.market.buy_shares(player_id, target, available)
        if success:
            # Reembolsar la diferencia (el descuento)
            refund = cost * discount
            player.receive_cash(refund)
            return {
                'success': True,
                'message': f"¡Oferta especial! Compraste {available} acciones de {company.name} con {discount*100:.0f}% de descuento",
                'effects': [f"Acciones compradas: {available}", f"Descuento aplicado: ${refund:.2f}"]
            }
        return {'success': False, 'message': "Error en la compra"}
    
    def _effect_sell_premium(self, game, player_id: str, target: Optional[str]) -> Dict:
        """Vende acciones con 25% de prima"""
        if not target:
            return {'success': False, 'message': "Especifica una empresa"}
        
        company = game.market.get_company(target)
        if not company:
            return {'success': False, 'message': "Empresa no encontrada"}
        
        player = game.get_player(player_id)
        holdings = company.shareholders.get(player_id, 0)
        
        if holdings <= 0:
            return {'success': False, 'message': "No tienes acciones de esta empresa"}
        
        premium = 0.25
        sell_quantity = min(holdings, 50)  # Vender hasta 50 acciones
        
        success, value, msg = game.market.sell_shares(player_id, target, sell_quantity)
        if success:
            # Añadir la prima
            bonus = value * premium
            player.receive_cash(bonus)
            return {
                'success': True,
                'message': f"¡Venta privilegiada! Vendiste {sell_quantity} acciones de {company.name} con {premium*100:.0f}% de prima",
                'effects': [f"Acciones vendidas: {sell_quantity}", f"Prima recibida: ${bonus:.2f}"]
            }
        return {'success': False, 'message': "Error en la venta"}
    
    def _effect_market_insight(self, game, player_id: str) -> Dict:
        """Revela información privilegiada del mercado"""
        insights = []
        
        # Mostrar empresas infravaloradas
        for company in game.market.companies.values():
            if company.price_change < -10:
                insights.append(f"📊 {company.name} está {abs(company.price_change):.1f}% por debajo de su valor inicial")
        
        # Mostrar sectores en tendencia
        for sector in game.market.sectors.values():
            if abs(sector.value_change) > 10:
                symbol = "📈" if sector.value_change > 0 else "📉"
                insights.append(f"{symbol} {sector.name}: {sector.value_change:+.1f}%")
        
        return {
            'success': True,
            'message': "Información privilegiada revelada:",
            'effects': insights if insights else ["Mercado estable, sin oportunidades obvias"]
        }
    
    def _effect_hostile_takeover(self, game, player_id: str, target: Optional[str]) -> Dict:
        """Intento de adquisición hostil de una empresa"""
        if not target:
            return {'success': False, 'message': "Especifica una empresa"}
        
        company = game.market.get_company(target)
        if not company:
            return {'success': False, 'message': "Empresa no encontrada"}
        
        player = game.get_player(player_id)
        
        # Costo de adquisición hostil: 150% del valor de mercado de las acciones restantes
        remaining_value = company.available_shares * company.current_price
        cost = remaining_value * 1.5
        
        if not player.can_afford(cost):
            return {
                'success': False,
                'message': f"Fondos insuficientes. Necesitas ${cost:.2f} para la adquisición"
            }
        
        # Ejecutar adquisición
        player.spend_cash(cost)
        
        # Transferir todas las acciones disponibles al jugador
        player.add_shares(target, company.available_shares)
        company.available_shares = 0
        
        # Verificar mayoría
        if player.check_majority(target, company.total_shares):
            player.companies_owned.add(target)
            player.add_influence(10)  # Puntos de influencia por adquisición
            
            return {
                'success': True,
                'message': f"¡Adquisición hostil exitosa! Ahora controlas {company.name}",
                'effects': [f"Acciones adquiridas: {company.total_shares - sum(company.shareholders.values())}", 
                           f"Costo: ${cost:.2f}", "+10 Influencia"]
            }
        
        return {'success': False, 'message': "No lograste el control mayoritario"}
    
    def _effect_insider_trading(self, game, player_id: str, target: Optional[str]) -> Dict:
        """Obtén información sobre el próximo evento del mercado"""
        # En una implementación real, esto revelaría el próximo evento
        return {
            'success': True,
            'message': "Información privilegiada: Se rumorea un movimiento importante en el mercado...",
            'effects': ["Próximo evento revelado en la siguiente ronda (implementación pendiente)"]
        }
    
    def _effect_bailout(self, game, player_id: str) -> Dict:
        """Rescate financiero: obtén efectivo de emergencia"""
        player = game.get_player(player_id)
        
        bailout_amount = 5000
        penalty = 5  # 5 puntos de influencia como penalización
        
        player.receive_cash(bailout_amount)
        player.influence_points = max(0, player.influence_points - penalty)
        
        return {
            'success': True,
            'message': f"¡Rescate aprobado! Recibes ${bailout_amount} pero pierdes {penalty} puntos de influencia",
            'effects': [f"+${bailout_amount}", f"-{penalty} Influencia"]
        }
    
    def _effect_trade_proposal(self, game, player_id: str, target: Optional[str]) -> Dict:
        """Propone un intercambio de acciones con otro jugador"""
        if not target or target == player_id:
            return {'success': False, 'message': "Especifica otro jugador como objetivo"}
        
        target_player = game.get_player(target)
        if not target_player:
            return {'success': False, 'message': "Jugador no encontrado"}
        
        # Crear propuesta de negociación (se resolvería en fase de negociación)
        return {
            'success': True,
            'message': f"Has propuesto una negociación a {target_player.name}. Espera su respuesta.",
            'effects': ["Fase de negociación iniciada"]
        }


class CardDeck:
    """
    Gestiona el mazo de cartas disponible en el juego.
    Las cartas se obtienen cumpliendo condiciones o aleatoriamente.
    """
    
    def __init__(self):
        self.cards: Dict[str, Card] = {}
        self.draw_pile: List[str] = []
        self.discard_pile: List[str] = []
        
        # Registrar cartas por defecto
        self._register_default_cards()
    
    def _register_default_cards(self):
        """Registra las cartas base del juego"""
        
        # Cartas de ACCIÓN
        self.register_card(Card(
            card_id="buy_discount",
            name="🏷️ Descuento de Compra",
            description="Compra acciones con 20% de descuento",
            card_type=CardType.ACTION,
            effect="20% discount on share purchase",
            target="company"
        ))
        
        self.register_card(Card(
            card_id="sell_premium",
            name="💰 Prima de Venta",
            description="Vende acciones con 25% de prima",
            card_type=CardType.ACTION,
            effect="25% premium on share sale",
            target="company"
        ))
        
        self.register_card(Card(
            card_id="hostile_takeover",
            name="🦈 Adquisición Hostil",
            description="Toma el control de una empresa pagando 150% de su valor",
            card_type=CardType.ACTION,
            effect="Acquire majority control of any company",
            target="company",
            value=1.5
        ))
        
        self.register_card(Card(
            card_id="insider_trading",
            name="🕵️ Información Privilegiada",
            description="Revela el próximo evento del mercado",
            card_type=CardType.ACTION,
            effect="Reveal next market event",
            target="self"
        ))
        
        # Cartas de FORTUNA
        self.register_card(Card(
            card_id="market_insight",
            name="📊 Perspicacia de Mercado",
            description="Muestra empresas infravaloradas y sectores en tendencia",
            card_type=CardType.FORTUNE,
            effect="Show undervalued companies and trending sectors",
            target="self"
        ))
        
        self.register_card(Card(
            card_id="lucky_strike",
            name="🍀 Golpe de Suerte",
            description="Gana $2000 inesperadamente",
            card_type=CardType.FORTUNE,
            effect="Gain $2000",
            target="self",
            value=2000
        ))
        
        self.register_card(Card(
            card_id="market_crash_warning",
            name="⚠️ Advertencia de Crash",
            description="Protege tus acciones de la próxima caída del mercado",
            card_type=CardType.FORTUNE,
            effect="Protect shares from next market crash",
            target="self",
            duration=3
        ))
        
        # Cartas de NEGOCIACIÓN
        self.register_card(Card(
            card_id="trade_proposal",
            name="🤝 Propuesta de Intercambio",
            description="Inicia una negociación con otro jugador",
            card_type=CardType.NEGOTIATION,
            effect="Initiate trade negotiation with another player",
            target="player"
        ))
        
        self.register_card(Card(
            card_id="alliance",
            name="🤝 Alianza Temporal",
            description="Forma una alianza de 3 rondas con otro jugador",
            card_type=CardType.NEGOTIATION,
            effect="Form 3-round alliance",
            target="player",
            duration=3
        ))
        
        self.register_card(Card(
            card_id="bailout",
            name="🆘 Rescate Financiero",
            description="Recibe $5000 pero pierdes 5 puntos de influencia",
            card_type=CardType.NEGOTIATION,
            effect="Gain $5000, lose 5 influence",
            target="self",
            value=5000
        ))
        
        # Inicializar mazo con múltiples copias
        self._initialize_deck()
    
    def register_card(self, card: Card):
        """Registra una carta en el sistema"""
        self.cards[card.card_id] = card
    
    def _initialize_deck(self):
        """Inicializa el mazo con copias de cada carta"""
        self.draw_pile = []
        
        # Añadir múltiples copias de cada carta
        for card_id, card in self.cards.items():
            copies = 3 if card.card_type == CardType.ACTION else 2
            self.draw_pile.extend([card_id] * copies)
        
        # Barajar
        self.shuffle()
    
    def shuffle(self):
        """Baraja el mazo"""
        import random
        random.shuffle(self.draw_pile)
    
    def draw(self, count: int = 1) -> List[Card]:
        """Roba cartas del mazo"""
        drawn = []
        
        for _ in range(count):
            if not self.draw_pile:
                if self.discard_pile:
                    # Reciclar descarte
                    self.draw_pile = self.discard_pile.copy()
                    self.discard_pile = []
                    self.shuffle()
                else:
                    break
            
            card_id = self.draw_pile.pop()
            if card_id in self.cards:
                drawn.append(self.cards[card_id])
        
        return drawn
    
    def discard(self, card_id: str):
        """Descarta una carta"""
        if card_id in self.cards:
            self.discard_pile.append(card_id)
    
    def get_card(self, card_id: str) -> Optional[Card]:
        """Obtiene una carta por su ID"""
        return self.cards.get(card_id)
    
    def cards_remaining(self) -> int:
        """Retorna el número de cartas restantes en el mazo"""
        return len(self.draw_pile)
