"""
Events - Sistema de eventos aleatorios que afectan el mercado
"""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random


class EventType(Enum):
    """Tipos de eventos posibles"""
    POSITIVE = "positivo"
    NEGATIVE = "negativo"
    NEUTRAL = "neutral"
    CRISIS = "crisis"
    BOOM = "boom"


@dataclass
class Event:
    """Representa un evento de mercado"""
    event_id: str
    name: str
    description: str
    event_type: EventType
    sector_affected: Optional[str]  # None = afecta a todo el mercado
    sector_change: float  # Cambio porcentual en el sector
    market_change: float  # Cambio porcentual general
    duration: int = 1  # Rondas que dura el efecto
    probability: float = 1.0  # Probabilidad relativa de ocurrencia
    
    def apply(self, market) -> str:
        """Aplica el evento al mercado y retorna un mensaje descriptivo"""
        message = f"📰 {self.name}: {self.description}\n"
        
        # Aplicar cambio al sector específico
        if self.sector_affected and self.sector_affected in market.sectors:
            market.apply_sector_event(self.sector_affected, self.sector_change)
            message += f"   → Sector {self.sector_affected}: {self.sector_change:+.1f}%\n"
        
        # Aplicar cambio general al mercado
        if self.market_change != 0:
            market.market_trend += self.market_change / 100
            message += f"   → Mercado general: {self.market_change:+.1f}%\n"
        
        return message


class EventManager:
    """
    Gestiona la generación y aplicación de eventos aleatorios.
    Los eventos simulan noticias del mundo real que afectan el mercado.
    """
    
    def __init__(self):
        self.events: Dict[str, Event] = {}
        self.active_events: List[Event] = []
        self.rounds_since_last_event = 0
        self.event_frequency = 3  # Eventos cada 3-5 rondas
        
        # Registrar eventos por defecto
        self._register_default_events()
    
    def _register_default_events(self):
        """Registra los eventos base del juego"""
        
        # === EVENTOS POSITIVOS ===
        self.register_event(Event(
            event_id="tech_innovation",
            name="💡 Innovación Tecnológica",
            description="Una startup revoluciona el sector con IA cuántica",
            event_type=EventType.POSITIVE,
            sector_affected="Tecnología",
            sector_change=20.0,
            market_change=2.0,
            probability=1.2
        ))
        
        self.register_event(Event(
            event_id="energy_breakthrough",
            name="⚡ Avance Energético",
            description="Descubren nueva fuente de energía limpia y barata",
            event_type=EventType.POSITIVE,
            sector_affected="Energía",
            sector_change=15.0,
            market_change=1.0,
            probability=1.0
        ))
        
        self.register_event(Event(
            event_id="tourism_boom",
            name="✈️ Boom Turístico",
            description="Temporada récord impulsa el turismo global",
            event_type=EventType.POSITIVE,
            sector_affected="Turismo",
            sector_change=18.0,
            market_change=0.5,
            probability=1.1
        ))
        
        self.register_event(Event(
            event_id="medical_advance",
            name="💊 Avance Médico",
            description="Nueva vacuna promete erradicar enfermedad global",
            event_type=EventType.POSITIVE,
            sector_affected="Salud",
            sector_change=12.0,
            market_change=1.5,
            probability=1.0
        ))
        
        self.register_event(Event(
            event_id="market_rally",
            name="📈 Euforia de Mercado",
            description="Los inversores están optimistas, compras masivas",
            event_type=EventType.BOOM,
            sector_affected=None,
            sector_change=0,
            market_change=5.0,
            probability=0.8
        ))
        
        # === EVENTOS NEGATIVOS ===
        self.register_event(Event(
            event_id="tech_crash",
            name="💻 Crisis Tecnológica",
            description="Burbuja tech explota, ventas masivas",
            event_type=EventType.NEGATIVE,
            sector_affected="Tecnología",
            sector_change=-25.0,
            market_change=-3.0,
            probability=1.0
        ))
        
        self.register_event(Event(
            event_id="energy_crisis",
            name="🛢️ Crisis Energética",
            description="Conflicto geopolítico dispara precios de energía",
            event_type=EventType.NEGATIVE,
            sector_affected="Energía",
            sector_change=-15.0,
            market_change=-2.0,
            probability=1.1
        ))
        
        self.register_event(Event(
            event_id="pandemic",
            name="🦠 Pandemia Global",
            description="Nuevo virus obliga a cuarentenas mundiales",
            event_type=EventType.CRISIS,
            sector_affected="Turismo",
            sector_change=-40.0,
            market_change=-5.0,
            probability=0.5
        ))
        
        self.register_event(Event(
            event_id="real_estate_bubble",
            name="🏠 Burbuja Inmobiliaria",
            description="El mercado inmobiliario colapsa por sobrevaluación",
            event_type=EventType.NEGATIVE,
            sector_affected="Inmobiliario",
            sector_change=-30.0,
            market_change=-4.0,
            probability=0.7
        ))
        
        self.register_event(Event(
            event_id="regulation_crackdown",
            name="⚖️ Nueva Regulación",
            description="Gobierno impone restricciones severas al sector",
            event_type=EventType.NEGATIVE,
            sector_affected="Finanzas",
            sector_change=-20.0,
            market_change=-1.0,
            probability=1.0
        ))
        
        self.register_event(Event(
            event_id="market_crash",
            name="📉 Crash del Mercado",
            description="Pánico vendedor barre todos los sectores",
            event_type=EventType.CRISIS,
            sector_affected=None,
            sector_change=0,
            market_change=-8.0,
            probability=0.3
        ))
        
        # === EVENTOS NEUTRALES ===
        self.register_event(Event(
            event_id="merger_wave",
            name="🤝 Ola de Fusiones",
            description="Empresas buscan sinergias mediante fusiones",
            event_type=EventType.NEUTRAL,
            sector_affected=None,
            sector_change=0,
            market_change=0,
            probability=0.9
        ))
        
        self.register_event(Event(
            event_id="investor_caution",
            name="😐 Precaución Inversora",
            description="Los inversores esperan señales más claras",
            event_type=EventType.NEUTRAL,
            sector_affected=None,
            sector_change=0,
            market_change=0,
            probability=1.0
        ))
    
    def register_event(self, event: Event):
        """Registra un nuevo evento en el sistema"""
        self.events[event.event_id] = event
    
    def generate_event(self, round_number: int) -> Optional[Event]:
        """
        Genera un evento aleatorio basado en la ronda actual.
        Retorna None si no hay evento esta ronda.
        """
        self.rounds_since_last_event += 1
        
        # Determinar si debe haber evento (cada 3-5 rondas)
        if self.rounds_since_last_event < self.event_frequency:
            if random.random() > 0.3:  # 30% chance de evento anticipado
                return None
        else:
            if random.random() > 0.7:  # 70% chance cuando toca
                return None
        
        self.rounds_since_last_event = 0
        
        # Calcular probabilidades ponderadas
        total_prob = sum(e.probability for e in self.events.values())
        rand = random.uniform(0, total_prob)
        
        cumulative = 0
        selected_event = None
        
        for event in self.events.values():
            cumulative += event.probability
            if rand <= cumulative:
                selected_event = event
                break
        
        # Ajustar tipo de evento según contexto del mercado
        if selected_event and hasattr(self, '_market'):
            market = self._market
            if market.market_trend > 0.1 and selected_event.event_type == EventType.NEGATIVE:
                # Menos probabilidad de eventos negativos en mercado alcista
                if random.random() > 0.6:
                    return self.generate_event(round_number)
            elif market.market_trend < -0.1 and selected_event.event_type == EventType.POSITIVE:
                # Menos probabilidad de eventos positivos en mercado bajista
                if random.random() > 0.6:
                    return self.generate_event(round_number)
        
        return selected_event
    
    def apply_event(self, event: Event, market) -> str:
        """Aplica un evento al mercado y retorna el mensaje"""
        if not hasattr(self, '_market'):
            self._market = market
            
        message = event.apply(market)
        
        if event.duration > 1:
            self.active_events.append(event)
        
        return message
    
    def update_active_events(self, market) -> List[str]:
        """Actualiza eventos activos y retorna mensajes de expiración"""
        messages = []
        expired = []
        
        for event in self.active_events:
            event.duration -= 1
            if event.duration <= 0:
                expired.append(event)
                messages.append(f"⏰ El efecto de '{event.name}' ha terminado")
        
        # Remover eventos expirados
        for event in expired:
            self.active_events.remove(event)
            # Revertir efectos temporales si es necesario
            if event.market_change != 0:
                market.market_trend -= event.market_change / 100
        
        return messages
    
    def get_upcoming_events_preview(self) -> List[Dict]:
        """Retorna una vista previa de eventos posibles"""
        preview = []
        for event in list(self.events.values())[:5]:  # Mostrar 5 eventos
            preview.append({
                'name': event.name,
                'type': event.event_type.value,
                'sector': event.sector_affected or "Todos",
                'impact': f"{event.sector_change:+.0f}%" if event.sector_affected else f"{event.market_change:+.0f}%"
            })
        return preview
    
    def set_frequency(self, frequency: int):
        """Configura la frecuencia de eventos (rondas entre eventos)"""
        self.event_frequency = max(2, min(frequency, 10))
