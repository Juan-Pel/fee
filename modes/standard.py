"""
Standard Mode - Partida estándar de 30-45 minutos
"""
from game.game import StockMarketGame


class StandardMode(StockMarketGame):
    """
    Modo estándar: 30-45 minutos, 3-6 jugadores.
    Objetivo: Alcanzar 50 puntos de influencia.
    Mecánicas equilibradas.
    """
    
    def __init__(self):
        super().__init__('standard')
    
    def get_mode_info(self) -> dict:
        return {
            'name': 'Partida Estándar',
            'duration': '30-45 minutos',
            'players': '3-6',
            'objective': 'Alcanzar 50 puntos de influencia',
            'event_frequency': 'Cada 4 rondas',
            'special_rules': [
                'Equilibrio entre estrategia y azar',
                'Cartas obtenidas cada 5 rondas',
                'Fusiones y absorciones estándar'
            ]
        }
