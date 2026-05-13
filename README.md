# Stock Market Tycoon - Simulador de Mercado Bursátil

Un simulador competitivo de mercado bursátil donde los jugadores representan corporaciones que buscan expandirse mediante compra de acciones, fusiones y absorciones.

## 🎮 Características Principales

### Mecánicas
- **Acciones y Fusiones**: Compra acciones de empresas, provoca fusiones o absorbe rivales
- **Eventos de Mercado**: Noticias que afectan el valor de las acciones (crisis, innovaciones, regulaciones)
- **Gestión de Liquidez**: Mantén flujo de caja para sobrevivir
- **Tablero Dinámico**: Mapa de sectores económicos que cambian de valor según las rondas
- **Sistema Riesgo/Recompensa**: Invertir en sectores emergentes puede dar grandes beneficios o pérdidas catastróficas

### Modos de Juego

| Modo | Duración | Jugadores | Objetivo |
|------|----------|-----------|----------|
| **Rápida** | 15 min | 2-4 | Mayor valor de mercado |
| **Estándar** | 30-45 min | 4-6 | Alcanzar 50 puntos de influencia |
| **Extendida** | 90 min | 6-8 | Controlar 3 sectores + capital |

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## ▶️ Cómo Jugar

```bash
python main.py
```

### Controles Básicos
- `c` - Comprar acciones
- `v` - Vender acciones
- `f` - Ver opciones de fusión
- `e` - Ver estado del mercado
- `m` - Mi portafolio
- `s` - Saltar turno
- `q` - Salir del juego

## 📋 Estructura del Proyecto

```
stock_market_tycoon/
├── main.py              # Punto de entrada principal
├── game/
│   ├── __init__.py
│   ├── game.py          # Lógica principal del juego
│   ├── player.py        # Clase Player
│   ├── company.py       # Clase Company
│   ├── sector.py        # Clase Sector
│   ├── market.py        # Sistema de mercado
│   ├── events.py        # Eventos aleatorios
│   └── cards.py         # Cartas de acción
├── modes/
│   ├── __init__.py
│   ├── quick.py         # Modo rápido (15 min)
│   ├── standard.py      # Modo estándar (30-45 min)
│   └── extended.py      # Modo extendido (90 min)
└── utils/
    ├── __init__.py
    └── helpers.py       # Funciones utilitarias
```

## 🏆 Condiciones de Victoria

- **Rápida**: Mayor valor de mercado al finalizar el tiempo
- **Estándar**: Alcanzar 50 puntos de influencia primero
- **Extendida**: Control mayoritario de 3 sectores + superar umbral de capital

## 🌐 Características Online (Planificadas)

- Ranking global con puntuación ELO
- Eventos semanales con reglas especiales
- Skins y personalización de corporaciones
- IA con diferentes estilos (agresiva, conservadora, especuladora)

## 📄 Licencia

MIT License
