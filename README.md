# Stock Market Tycoon - C++ Raylib Project

## ¡Juego Completamente Desarrollado! 🎮

El proyecto está **completamente implementado** en C++ con Raylib. Todo el código fuente está listo en el repositorio:

- ✅ **Tablero 3D interactivo** con sectores económicos
- ✅ **Sistema de turnos** con temporizador automático (60 segundos)
- ✅ **IA para bots** con 3 personalidades (agresiva, conservadora, balanceada)
- ✅ **Cartas de eventos** con fenómenos de mercado y desastres naturales
- ✅ **Sistema de trueque** entre jugadores
- ✅ **Múltiples condiciones de victoria**: Magnate, Oligopolio, Influencia
- ✅ **3 modos de juego**: Rápida (15 min), Estándar (30-45 min), Extendida (90 min)
- ✅ **Interfaz visual completa** con menús, HUD y popups de eventos

## Requisitos Previos

### Windows (Recomendado)
1. Instalar [Visual Studio Community](https://visualstudio.microsoft.com/) con soporte para C++
2. O instalar [MSYS2](https://www.msys2.org/) y luego:
```bash
pacman -S mingw-w64-x86_64-toolchain mingw-w64-x86_64-cmake mingw-w64-x86_64-raylib
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install build-essential git cmake libraylib-dev libgl1-mesa-dev libx11-dev libxrandr-dev libxi-dev libxcursor-dev
```

### macOS
```bash
brew install raylib cmake
```

## Compilación

### Método Automático (Linux/macOS)
```bash
chmod +x build.sh
./build.sh
```

### Método Manual

#### Windows (MSYS2)
```bash
mkdir build && cd build
cmake -G "MinGW Makefiles" ..
mingw32-make
stock_market_tycoon.exe
```

#### Windows (Visual Studio)
```bash
mkdir build && cd build
cmake ..
cmake --build . --config Release
Release\stock_market_tycoon.exe
```

#### Linux/macOS
```bash
mkdir build && cd build
cmake ..
make
./stock_market_tycoon
```

## Controles del Juego

### Menú Principal
- **Click en botones**: Seleccionar opciones
- **Partida Local**: Jugar contra bots IA
- **Configuración**: Personalizar partida antes de iniciar

### Durante la Partida
- **Mouse**: 
  - Clic izquierdo: Seleccionar empresas/sectores
  - Clic derecho + arrastrar: Rotar cámara 3D
  - Rueda: Zoom
- **Teclado**:
  - `ESPACIO`: Saltar turno
  - `ESC`: Pausa/Menú
  - `1`: Vista superior
  - `2`: Vista lateral
  - `3`: Vista detalle

## Características del Juego

### Mercados y Empresas
- **8 Sectores**: Tecnología, Energía, Turismo, Finanzas, Salud, Inmobiliario, Consumo, Industrial
- **16 Empresas**: 2 por sector con precios dinámicos
- **Volatilidad**: Cada empresa tiene su propia volatilidad de mercado

### Sistema de Eventos
- **Eventos Aleatorios**: Cada 3-5 rondas ocurre un evento
- **Tipos de Eventos**:
  - Innovación Tecnológica (+20% sector tech)
  - Crisis Energética (-15% sector energía)
  - Pandemia (-30% turismo)
  - Desastres Naturales (afecta sectores específicos)
  - Boom Económico (+10% todos los sectores)

### Cartas de Acción
- Descuentos en compras
- Primas en ventas
- Adquisiciones hostiles
- Rescates financieros

### Condiciones de Victoria
1. **Magnate**: Mayor capital total al finalizar
2. **Oligopolio**: Controlar >50% de un sector
3. **Influencia**: Más puntos por diversidad de inversiones

## Estructura del Proyecto

```
stock_market_tycoon/
├── src/
│   ├── main.cpp          # Punto de entrada y bucle principal
│   ├── game.cpp          # Lógica del juego, turnos, IA
│   ├── board.cpp         # Tablero 3D, cámara, renderizado
│   ├── player.cpp        # Gestión de jugadores y portafolios
│   ├── market.cpp        # Mercado, acciones, eventos, cartas
│   └── ui.cpp            # Interfaz, menús, botones, paneles
├── include/
│   ├── game.h
│   ├── board.h
│   ├── player.h
│   ├── market.h
│   └── ui.h
├── assets/
│   ├── models/           # Modelos 3D (generados proceduralmente)
│   ├── textures/         # Texturas (opcional)
│   └── shaders/          # Shaders personalizados (opcional)
├── CMakeLists.txt        # Configuración de compilación
├── build.sh              # Script de compilación automática
└── README.md             # Este archivo
```

## Solución de Problemas

### Error: "Could NOT find X11"
En Linux, instala las dependencias:
```bash
sudo apt-get install libx11-dev libxrandr-dev libxi-dev libxcursor-dev libxinerama-dev libgl1-mesa-dev
```

### Error: "raylib not found"
Instala raylib:
- Ubuntu: `sudo apt-get install libraylib-dev`
- Windows MSYS2: `pacman -S mingw-w64-x86_64-raylib`
- macOS: `brew install raylib`

### El juego no se abre
Verifica que tienes un servidor gráfico corriendo (necesario para aplicaciones OpenGL).

## Próximas Mejoras (Opcional)

- [ ] Multijugador online con Socket.IO
- [ ] Modelos 3D personalizados
- [ ] Más tipos de cartas y eventos
- [ ] Sistema de ranking global
- [ ] Guardar/cargar partidas

## Licencia

MIT License - Libre uso y modificación.

---

**¡Disfruta del juego! 🚀📈**
