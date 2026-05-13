"""
Extended Mode - Partida extendida de 90 minutos
"""
from game.game import StockMarketGame


class ExtendedMode(StockMarketGame):
    """
    Modo extendido: 90 minutos, 4-8 jugadores.
    Objetivo: Controlar 3 sectores + superar umbral de capital.
    Incluye rondas de negociación y eventos macroeconómicos complejos.
    """
    
    def __init__(self):
        super().__init__('extended')
    
    def get_mode_info(self) -> dict:
        return {
            'name': 'Partida Extendida',
            'duration': '90 minutos',
            'players': '4-8',
            'objective': 'Controlar 3 sectores + $100,000 de capital',
            'event_frequency': 'Cada 5 rondas',
            'special_rules': [
                'Rondas de negociación obligatoria cada 10 turnos',
                'Eventos macroeconómicos complejos',
                'Alianzas temporales permitidas',
                'Mayor profundidad estratégica'
            ]
        }
