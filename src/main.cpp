#include "raylib.h"
#include "game.h"
#include <iostream>

#if defined(PLATFORM_WEB)
    #include <emscripten/emscripten.h>
#endif

// Variables globales para el bucle del juego
Game* game = nullptr;

void UpdateDrawFrame(void);

int main(int argc, char* argv[]) {
    // Configuración inicial de la ventana
    const int screenWidth = 1280;
    const int screenHeight = 720;
    
    // Configurar hints para OpenGL
    SetConfigFlags(FLAG_MSAA_4X_HINT);  // Antialiasing
    SetConfigFlags(FLAG_VSYNC_HINT);    // Sincronización vertical
    
    // Crear ventana
    InitWindow(screenWidth, screenHeight, "Stock Market Tycoon");
    SetTargetFPS(60);
    
    // Iniciar el juego
    game = new Game();
    
    if (!game->initialize()) {
        std::cerr << "Error al inicializar el juego" << std::endl;
        CloseWindow();
        delete game;
        return 1;
    }
    
    #if defined(PLATFORM_WEB)
        // Para compilación web
        emscripten_set_main_loop(UpdateDrawFrame, 0, 1);
    #else
        // Bucle principal para escritorio
        while (!WindowShouldClose()) {
            UpdateDrawFrame();
        }
    #endif
    
    // Limpieza
    game->unload();
    delete game;
    CloseWindow();
    
    return 0;
}

void UpdateDrawFrame(void) {
    if (game != nullptr) {
        game->update();
        game->draw();
    }
}
