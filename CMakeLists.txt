cmake_minimum_required(VERSION 3.10)
project(StockMarketTycoon VERSION 1.0 LANGUAGES CXX)

# Establecer estándar C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Buscar Raylib
find_package(raylib 4.0 QUIET)

if(NOT raylib_FOUND)
    # Si no se encuentra, descargar y compilar Raylib
    include(FetchContent)
    FetchContent_Declare(
        raylib
        GIT_REPOSITORY https://github.com/raysan5/raylib.git
        GIT_TAG 4.5.0
    )
    FetchContent_MakeAvailable(raylib)
    
    # Configurar Raylib para compilación mínima (sin X11)
    set(PLATFORM "Desktop")
    set(USE_GLFW TRUE)
endif()

# Archivos fuente
set(SOURCES
    src/main.cpp
    src/game.cpp
    src/board.cpp
    src/player.cpp
    src/market.cpp
    src/ui.cpp
)

# Archivos de cabecera
set(HEADERS
    include/game.h
    include/board.h
    include/player.h
    include/market.h
    include/ui.h
)

# Crear ejecutable
add_executable(stock_market_tycoon ${SOURCES} ${HEADERS})

# Incluir directorios
target_include_directories(stock_market_tycoon PRIVATE ${CMAKE_SOURCE_DIR}/include)

# Enlazar con Raylib
target_link_libraries(stock_market_tycoon raylib)

# Configurar opciones de plataforma
if(UNIX AND NOT APPLE)
    # Intentar encontrar dependencias opcionales
    find_package(X11 QUIET)
    if(X11_FOUND)
        target_link_libraries(stock_market_tycoon ${X11_LIBRARIES})
        target_include_directories(stock_market_tycoon PRIVATE ${X11_INCLUDE_DIR})
    endif()
    target_link_libraries(stock_market_tycoon GL m pthread dl rt)
endif()
