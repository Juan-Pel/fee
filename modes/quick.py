"""
Quick Mode - Partida rápida de 15 minutos
"""
from game.game import StockMarketGame, GameMode


class QuickMode(StockMarketGame):
    """
    Modo rápido: 15 minutos, 2-4 jugadores.
    Objetivo: Mayor valor de mercado al finalizar.
    Eventos cada 2 rondas.
    """
    
    def __init__(self):
        super().__init__('quick')
    
    def get_mode_info(self) -> dict:
        return {
            'name': 'Partida Rápida',
            'duration': '15 minutos',
            'players': '2-4',
            'objective': 'Mayor valor de mercado',
            'event_frequency': 'Cada 2 rondas',
            'special_rules': [
                'Fusiones más frecuentes',
                'Cartas obtenidas cada 3 rondas',
                'Volatilidad aumentada un 20%'
            ]
        }
