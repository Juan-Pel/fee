# 📈 Stock Market Tycoon

Simulador de mercado bursátil competitivo multijugador en tiempo real.

## 🚀 Características

- **Partida Local**: Juega contra bots con IA
- **Multijugador Online**: Crea salas con código único para jugar con amigos
- **Mercado Dinámico**: 8 empresas en 4 sectores con precios que fluctúan
- **Eventos Aleatorios**: Crisis económicas, booms sectoriales, regulaciones
- **Temporizador por Turno**: 30-90 segundos configurables
- **Sistema de Ranking**: Clasificación en tiempo real por valor de mercado

## 📁 Estructura del Proyecto

```
stock_market_pro/
├── server.py              # Servidor Flask + Socket.IO
├── game_logic/
│   └── core.py           # Lógica del juego (empresas, jugadores, turnos)
├── public/
│   ├── index.html        # Interfaz web
│   ├── css/
│   │   └── styles.css    # Estilos visuales
│   └── js/
│       └── game.js       # Cliente JavaScript
└── requirements.txt      # Dependencias Python
```

## 🔧 Instalación

### Requisitos
- Python 3.8+
- Node.js (opcional, solo para desarrollo)

### Pasos

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Ejecutar el servidor:**
```bash
python server.py
```

3. **Abrir en el navegador:**
```
http://127.0.0.1:5000
```

## 🎮 Cómo Jugar

### Partida Local
1. Haz clic en "Partida Local (vs IA)"
2. Configura tu nombre, duración y tiempo por turno
3. Inicia la partida y compite contra 3 bots

### Multijugador Online
1. Haz clic en "Multijugador Online"
2. **Crear Sala**: Genera un código de 6 caracteres
3. Comparte el código con tus amigos
4. **Unirse a Sala**: Ingresa el código recibido
5. El creador inicia la partida cuando todos estén listos

### Mecánicas Básicas
- **Comprar Acciones**: Selecciona una empresa, indica cantidad y haz clic en "Comprar"
- **Vender Acciones**: Selecciona una empresa de tu portfolio y haz clic en "Vender"
- **Saltar Turno**: Pasa al siguiente jugador sin hacer nada
- **Objetivo**: Tener el mayor valor de mercado (capital + acciones) al finalizar

## ⚙️ Configuración de Partida

- **Rondas**: 10 (rápida), 20 (estándar), 40 (extendida)
- **Tiempo por Turno**: 30, 60 o 90 segundos
- **Eventos Aleatorios**: Activar/desactivar eventos de mercado
- **Jugadores**: 2-6 humanos + bots para completar

## 🌐 Multijugador

El sistema usa Socket.IO para comunicación en tiempo real:
- Cada sala tiene un código único de 6 caracteres
- Los jugadores se sincronizan automáticamente
- El temporizador es independiente en cada cliente pero sincronizado con el servidor
- Soporta hasta 6 jugadores humanos por sala

## 🏆 Condiciones de Victoria

Gana el jugador con mayor **valor de mercado** al finalizar todas las rondas:
```
Valor de Mercado = Capital en Efectivo + (Acciones × Precio Actual)
```

## 🛠️ Desarrollo

### Agregar más empresas
Edita `game_logic/core.py` en el método `_init_companies()`:

```python
company_names = [
    ('TechCorp', 'Tecnología'),
    ('NuevaEmpresa', 'NuevoSector'),
    # ...
]
```

### Modificar eventos
Edita `_process_round_events()` en `game_logic/core.py` para cambiar probabilidades o efectos.

### Personalizar interfaz
- Colores: `public/css/styles.css`
- Estructura HTML: `public/index.html`
- Comportamiento: `public/js/game.js`

## 📝 Notas

- El servidor usa Flask en modo desarrollo. Para producción, configura un WSGI server como Gunicorn.
- Los bots tienen IA básica: compran aleatoriamente cuando tienen capital.
- Los precios de las acciones cambian según oferta/demanda y eventos aleatorios.

## 🐛 Solución de Problemas

**Error: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Error: "Address already in use"**
```bash
# Mata el proceso en el puerto 5000
kill $(lsof -t -i:5000)
```

**Los botones no responden**
- Verifica que el servidor esté corriendo
- Abre la consola del navegador (F12) para ver errores
- Recarga la página (Ctrl+R)

## 📄 Licencia

Proyecto educativo de código abierto.
