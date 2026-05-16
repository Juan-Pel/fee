#include "ui.h"
#include <cmath>

UI::UI() : currentState(UIState::MENU_MAIN), previousState(UIState::MENU_MAIN),
           showEventCard(false), cardAnimationProgress(0), showTradeScreen(false),
           turnTimer(60), maxTurnTime(60) {
}

void UI::initialize() {
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    // Definir áreas principales
    gameArea = {250, 50, screenWidth - 300, screenHeight - 100};
    sidebarLeft = {0, 0, 250, screenHeight};
    sidebarRight = {screenWidth - 250, 0, 250, screenHeight};
    topBar = {0, 0, screenWidth, 50};
    bottomBar = {0, screenHeight - 50, screenWidth, 50};
    
    // Crear botones del menú principal
    Button btn;
    btn.bounds = {(float)(screenWidth/2 - 150), (float)(screenHeight/2 - 80), 300, 50};
    btn.text = "Partida Local";
    btn.enabled = true;
    btn.visible = true;
    btn.normalColor = BLUE;
    btn.hoverColor = SKYBLUE;
    btn.pressedColor = DARKBLUE;
    btn.id = 1;
    buttons.push_back(btn);
    
    btn.bounds.y += 70;
    btn.text = "Multijugador Online";
    btn.id = 2;
    buttons.push_back(btn);
    
    btn.bounds.y += 70;
    btn.text = "Opciones";
    btn.id = 3;
    buttons.push_back(btn);
    
    btn.bounds.y += 70;
    btn.text = "Salir";
    btn.id = 4;
    buttons.push_back(btn);
    
    // Paneles del HUD del juego
    Panel panel;
    panel.bounds = {0, 50, 250, screenHeight - 100};
    panel.type = PanelType::PLAYER_PORTFOLIO;
    panel.visible = false;
    panel.collapsible = true;
    panel.collapsed = false;
    panel.title = "Portafolio";
    panels.push_back(panel);
    
    panel.bounds = {(float)(screenWidth - 250), 50, 250, screenHeight - 100};
    panel.type = PanelType::MARKET_INFO;
    panel.visible = false;
    panel.collapsible = true;
    panel.collapsed = false;
    panel.title = "Mercado";
    panels.push_back(panel);
    
    panel.bounds = {(float)(screenWidth/2 - 200), (float)(screenHeight - 120), 400, 70};
    panel.type = PanelType::ACTION_PANEL;
    panel.visible = false;
    panel.collapsible = false;
    panel.collapsed = false;
    panel.title = "Acciones";
    panels.push_back(panel);
}

void UI::update() {
    Vector2 mousePos = GetMousePosition();
    
    // Actualizar temporizador
    if (currentState == UIState::PLAYING) {
        turnTimer -= GetFrameTime();
        if (turnTimer <= 0) {
            turnTimer = 0;
            // El juego debe manejar el cambio de turno automáticamente
        }
    }
    
    // Animación de carta de evento
    if (showEventCard) {
        cardAnimationProgress += GetFrameTime() * 2.0f;
        if (cardAnimationProgress > 1.0f) cardAnimationProgress = 1.0f;
    }
}

void UI::draw() {
    switch (currentState) {
        case UIState::MENU_MAIN:
            drawMainMenu();
            break;
        case UIState::MENU_MULTIPLAYER:
            drawMultiplayerMenu();
            break;
        case UIState::GAME_SETUP:
            drawGameSetup();
            break;
        case UIState::PLAYING:
            drawGameHUD();
            break;
        case UIState::PAUSED:
            drawGameHUD();
            drawPauseMenu();
            break;
        case UIState::VICTORY:
            drawVictoryScreen();
            break;
        case UIState::TRADE_SCREEN:
            drawGameHUD();
            drawTradeScreen();
            break;
        default:
            break;
    }
    
    // Dibujar carta de evento si está visible
    if (showEventCard) {
        drawCardPopup();
    }
}

void UI::setState(UIState state) {
    previousState = currentState;
    currentState = state;
    
    // Mostrar/ocultar paneles según el estado
    bool showPanels = (state == UIState::PLAYING || state == UIState::PAUSED);
    for (auto& panel : panels) {
        panel.visible = showPanels;
    }
}

UIState UI::getState() const {
    return currentState;
}

void UI::drawMainMenu() {
    ClearBackground(DARKBLUE);
    
    // Título
    DrawTextCentered("STOCK MARKET TYCOON", 
                     {(float)GetScreenWidth()/2, 100}, 60, WHITE);
    DrawTextCentered("Simulador de Mercado Bursátil",
                     {(float)GetScreenWidth()/2, 170}, 30, LIGHTGRAY);
    
    // Botones
    for (auto& button : buttons) {
        if (button.visible && button.id <= 4) {
            drawButton(button);
        }
    }
    
    // Instrucciones
    DrawTextCentered("Click en 'Partida Local' para jugar contra IA",
                     {(float)GetScreenWidth()/2, (float)GetScreenHeight() - 80}, 20, GRAY);
}

void UI::drawMultiplayerMenu() {
    ClearBackground(DARKBLUE);
    
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    DrawTextCentered("Multijugador Online", 
                     {(float)screenWidth/2, 80}, 50, WHITE);
    
    // Botón Crear Sala
    Button createBtn = {(float)(screenWidth/2 - 150), (float)(screenHeight/2 - 60), 
                        300, 50, "Crear Sala", true, true, GREEN, LIME, DARKGREEN, 10};
    drawButton(createBtn);
    
    // Botón Unirse a Sala
    Button joinBtn = {(float)(screenWidth/2 - 150), (float)(screenHeight/2 + 10), 
                      300, 50, "Unirse a Sala", true, true, ORANGE, GOLD, DARKORANGE, 11};
    drawButton(joinBtn);
    
    // Campo para código de sala
    InputField codeField = {(float)(screenWidth/2 - 150), (float)(screenHeight/2 + 80),
                            300, 40, "", "Código de Sala", false, 10, 20};
    drawInputField(codeField);
    
    // Botón Volver
    Button backBtn = {(float)(screenWidth/2 - 100), (float)(screenHeight - 80),
                      200, 40, "Volver", true, true, GRAY, LIGHTGRAY, DARKGRAY, 99};
    drawButton(backBtn);
}

void UI::drawGameSetup() {
    ClearBackground(DARKBLUE);
    
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    DrawTextCentered("Configuración de Partida", 
                     {(float)screenWidth/2, 60}, 45, WHITE);
    
    // Modo de juego
    DrawTextCentered("Modo de Juego:", {(float)screenWidth/2, 140}, 25, LIGHTGRAY);
    
    Button quickBtn = {(float)(screenWidth/2 - 160), 170, 100, 40, "Rápida", true, true, BLUE, SKYBLUE, DARKBLUE, 20};
    Button stdBtn = {(float)(screenWidth/2 - 30), 170, 100, 40, "Estándar", true, true, BLUE, SKYBLUE, DARKBLUE, 21};
    Button extBtn = {(float)(screenWidth/2 + 100), 170, 100, 40, "Extendida", true, true, BLUE, SKYBLUE, DARKBLUE, 22};
    
    drawButton(quickBtn);
    drawButton(stdBtn);
    drawButton(extBtn);
    
    // Condición de victoria
    DrawTextCentered("Condición de Victoria:", {(float)screenWidth/2, 250}, 25, LIGHTGRAY);
    
    Button magBtn = {(float)(screenWidth/2 - 160), 280, 100, 40, "Capital", true, true, PURPLE, PLUM, DARKPURPLE, 30};
    Button oliBtn = {(float)(screenWidth/2 - 30), 280, 100, 40, "Control", true, true, PURPLE, PLUM, DARKPURPLE, 31};
    Button infBtn = {(float)(screenWidth/2 + 100), 280, 100, 40, "Influencia", true, true, PURPLE, PLUM, DARKPURPLE, 32};
    
    drawButton(magBtn);
    drawButton(oliBtn);
    drawButton(infBtn);
    
    // Tiempo por turno
    DrawTextCentered("Tiempo por Turno:", {(float)screenWidth/2, 380}, 25, LIGHTGRAY);
    DrawTextCentered("60 segundos", {(float)screenWidth/2, 420}, 30, YELLOW);
    
    // Botón Iniciar
    Button startBtn = {(float)(screenWidth/2 - 100), (float)(screenHeight - 120), 200, 50, 
                       "INICIAR PARTIDA", true, true, GREEN, LIME, DARKGREEN, 50};
    drawButton(startBtn);
    
    // Botón Volver
    Button backBtn = {(float)(screenWidth/2 - 100), (float)(screenHeight - 60), 200, 40, 
                      "Volver", true, true, GRAY, LIGHTGRAY, DARKGRAY, 99};
    drawButton(backBtn);
}

void UI::drawGameHUD() {
    // Fondo principal
    ClearBackground(BLACK);
    
    // Barra superior con información del turno
    DrawRectangleRec(topBar, DARKGRAY);
    DrawLine(0, 50, GetScreenWidth(), 50, GRAY);
    
    // Temporizador
    drawTurnTimer();
    
    // Información del jugador actual
    DrawTextWithShadow("Turno: Jugador 1", {20, 15}, 24, WHITE, BLACK);
    
    // Ronda
    std::string roundText = "Ronda: 1";
    DrawTextWithShadow(roundText.c_str(), {(float)GetScreenWidth()/2 - 50, 15}, 24, WHITE, BLACK);
    
    // Paneles laterales
    for (auto& panel : panels) {
        if (panel.visible) {
            drawPanel(panel);
        }
    }
    
    // Botones de acción rápida
    drawActionButtons();
    
    // Botón de pausa
    Button pauseBtn = {(float)(GetScreenWidth() - 60), 10, 40, 30, "||", true, true, 
                       GRAY, LIGHTGRAY, DARKGRAY, 100};
    drawButton(pauseBtn);
}

void UI::drawPauseMenu() {
    // Overlay semitransparente
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), Fade(BLACK, 0.7f));
    
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    DrawTextCentered("PAUSA", {(float)screenWidth/2, (float)screenHeight/2 - 100}, 60, WHITE);
    
    Button resumeBtn = {(float)(screenWidth/2 - 100), (float)(screenHeight/2 - 20), 
                        200, 50, "Continuar", true, true, GREEN, LIME, DARKGREEN, 101};
    drawButton(resumeBtn);
    
    Button settingsBtn = {(float)(screenWidth/2 - 100), (float)(screenHeight/2 + 40), 
                          200, 50, "Opciones", true, true, BLUE, SKYBLUE, DARKBLUE, 102};
    drawButton(settingsBtn);
    
    Button quitBtn = {(float)(screenWidth/2 - 100), (float)(screenHeight/2 + 100), 
                      200, 50, "Salir al Menú", true, true, RED, PINK, DARKRED, 103};
    drawButton(quitBtn);
}

void UI::drawVictoryScreen() {
    ClearBackground(GOLD);
    
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    DrawTextCentered("¡VICTORIA!", {(float)screenWidth/2, 100}, 80, DARKBLUE);
    DrawTextCentered("Jugador 1 gana", {(float)screenWidth/2, 200}, 50, DARKBLUE);
    
    Button menuBtn = {(float)(screenWidth/2 - 100), (float)(screenHeight/2 + 50), 
                      200, 50, "Volver al Menú", true, true, BLUE, SKYBLUE, DARKBLUE, 200};
    drawButton(menuBtn);
}

void UI::drawTradeScreen() {
    // Overlay
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), Fade(BLACK, 0.8f));
    
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    DrawTextCentered("INTERCAMBIO", {(float)screenWidth/2, 80}, 50, WHITE);
    
    // Área del jugador 1
    DrawRectangle(screenWidth/4 - 150, 150, 300, 300, Fade(BLUE, 0.3f));
    DrawRectangleLines(screenWidth/4 - 150, 150, 300, 300, WHITE);
    DrawTextCentered("Tu Oferta", {(float)screenWidth/4, 130}, 25, WHITE);
    
    // Área del jugador 2
    DrawRectangle(3*screenWidth/4 - 150, 150, 300, 300, Fade(RED, 0.3f));
    DrawRectangleLines(3*screenWidth/4 - 150, 150, 300, 300, WHITE);
    DrawTextCentered("Oferta Recibida", {(float)(3*screenWidth/4), 130}, 25, WHITE);
    
    // Botones de acción
    Button acceptBtn = {(float)(screenWidth/2 - 120), (float)(screenHeight - 120), 
                        100, 40, "Aceptar", true, true, GREEN, LIME, DARKGREEN, 300};
    drawButton(acceptBtn);
    
    Button rejectBtn = {(float)(screenWidth/2 + 20), (float)(screenHeight - 120), 
                        100, 40, "Rechazar", true, true, RED, PINK, DARKRED, 301};
    drawButton(rejectBtn);
}

void UI::drawCardPopup() {
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    float scale = sinf(cardAnimationProgress * PI) * 0.3f + 0.7f;
    int cardWidth = 500;
    int cardHeight = 350;
    
    int posX = (screenWidth - cardWidth) / 2;
    int posY = (screenHeight - cardHeight) / 2;
    
    // Sombra
    DrawRectangle(posX + 10, posY + 10, cardWidth, cardHeight, Fade(BLACK, 0.5f));
    
    // Carta
    DrawRectangle(posX, posY, cardWidth, cardHeight, WHITE);
    DrawRectangleLines(posX, posY, cardWidth, cardHeight, GOLD);
    
    // Borde interior
    DrawRectangle(posX + 10, posY + 10, cardWidth - 20, cardHeight - 20, 
                  Fade(YELLOW, 0.2f));
    
    // Título
    DrawTextCentered(currentEventTitle.c_str(), 
                     {(float)(posX + cardWidth/2), (float)(posY + 40)}, 32, DARKBLUE);
    
    // Descripción
    int textWidth = cardWidth - 60;
    const char* desc = currentEventDescription.c_str();
    int fontSize = 20;
    
    // Dibujar descripción centrada
    DrawTextCentered(desc, {(float)(posX + cardWidth/2), (float)(posY + 120)}, 
                     fontSize, DARKGRAY);
    
    // Instrucción
    DrawTextCentered("[Click para continuar]", 
                     {(float)(posX + cardWidth/2), (float)(posY + cardHeight - 40)}, 
                     18, GRAY);
}

void UI::drawButton(Button& button) {
    if (!button.visible) return;
    
    Vector2 mousePos = GetMousePosition();
    bool isHovered = CheckCollisionPointRec(mousePos, button.bounds);
    bool isPressed = isHovered && IsMouseButtonDown(MOUSE_BUTTON_LEFT);
    
    Color color = button.normalColor;
    if (isPressed && button.enabled) color = button.pressedColor;
    else if (isHovered && button.enabled) color = button.hoverColor;
    else if (!button.enabled) color = GRAY;
    
    // Dibujar botón con borde redondeado
    DrawRectangleRounded(button.bounds, 0.3f, 8, color);
    DrawRectangleRoundedLines(button.bounds, 0.3f, 8, 2, DARKGRAY);
    
    // Texto centrado
    int textWidth = MeasureText(button.text.c_str(), 20);
    Vector2 textPos = {
        button.bounds.x + (button.bounds.width - textWidth) / 2,
        button.bounds.y + (button.bounds.height - 20) / 2
    };
    
    DrawText(button.text.c_str(), (int)textPos.x, (int)textPos.y, 20, WHITE);
}

void UI::drawInputField(InputField& field) {
    // Fondo
    DrawRectangleRec(field.bounds, WHITE);
    DrawRectangleLinesEx(field.bounds, 2, field.active ? BLUE : GRAY);
    
    // Texto o placeholder
    const char* text = field.text.empty() ? field.placeholder.c_str() : field.text.c_str();
    Color textColor = field.text.empty() ? GRAY : BLACK;
    
    DrawText(text, (int)field.bounds.x + 10, 
             (int)(field.bounds.y + (field.bounds.height - 20) / 2), 20, textColor);
}

void UI::drawPanel(Panel& panel) {
    if (!panel.visible) return;
    
    // Fondo del panel
    DrawRectangleRec(panel.bounds, Fade(DARKGRAY, 0.9f));
    DrawRectangleLinesEx(panel.bounds, 2, GRAY);
    
    // Título
    DrawText(panel.title.c_str(), (int)panel.bounds.x + 10, (int)panel.bounds.y + 10, 
             20, WHITE);
    
    // Línea separadora
    DrawLine((int)panel.bounds.x, (int)panel.bounds.y + 35, 
             (int)(panel.bounds.x + panel.bounds.width), (int)panel.bounds.y + 35, GRAY);
}

void UI::drawTurnTimer() {
    int screenWidth = GetScreenWidth();
    float barWidth = 300;
    float barHeight = 20;
    float barX = (screenWidth - barWidth) / 2;
    
    // Fondo de la barra
    DrawRectangle((int)barX, 10, (int)barWidth, (int)barHeight, DARKGRAY);
    
    // Barra de progreso
    float progress = turnTimer / maxTurnTime;
    Color barColor = GREEN;
    if (progress < 0.3f) barColor = RED;
    else if (progress < 0.5f) barColor = YELLOW;
    
    DrawRectangle((int)barX + 2, 12, (int)((barWidth - 4) * progress), (int)(barHeight - 4), barColor);
    
    // Texto del tiempo
    std::string timeText = std::to_string((int)turnTimer) + "s";
    DrawTextWithShadow(timeText.c_str(), 
                       {(float)(screenWidth/2 - 15), 12}, 18, WHITE, BLACK);
}

void UI::drawActionButtons() {
    int screenWidth = GetScreenWidth();
    int screenHeight = GetScreenHeight();
    
    // Botones de acción en la parte inferior
    Button buyBtn = {(float)(screenWidth/2 - 220), (float)(screenHeight - 90), 
                     100, 35, "Comprar", true, true, GREEN, LIME, DARKGREEN, 200};
    Button sellBtn = {(float)(screenWidth/2 - 110), (float)(screenHeight - 90), 
                      100, 35, "Vender", true, true, RED, PINK, DARKRED, 201};
    Button tradeBtn = {(float)(screenWidth/2), (float)(screenHeight - 90), 
                       100, 35, "Intercambio", true, true, ORANGE, GOLD, DARKORANGE, 202};
    Button cardBtn = {(float)(screenWidth/2 + 110), (float)(screenHeight - 90), 
                      100, 35, "Carta", true, true, PURPLE, PLUM, DARKPURPLE, 203};
    
    drawButton(buyBtn);
    drawButton(sellBtn);
    drawButton(tradeBtn);
    drawButton(cardBtn);
}

bool UI::handleButtonClick(int buttonId) {
    // El juego debe implementar la lógica específica
    return true;
}

void UI::showEventCard(const std::string& title, const std::string& description) {
    currentEventTitle = title;
    currentEventDescription = description;
    showEventCard = true;
    cardAnimationProgress = 0;
}

void UI::hideEventCard() {
    showEventCard = false;
    cardAnimationProgress = 0;
}

void UI::setTurnTimer(float time) {
    turnTimer = time;
    maxTurnTime = time;
}

float UI::getTurnTimer() const {
    return turnTimer;
}

void UI::setMaxTurnTime(float time) {
    maxTurnTime = time;
}

// Funciones de utilidad
void DrawRectangleRoundedLines(Rectangle rec, float roundness, int segments, float lineThick, Color color) {
    // Implementación simplificada
    DrawRectangleLinesEx(rec, (int)lineThick, color);
}

void DrawTextCentered(const std::string& text, Vector2 position, int fontSize, Color color) {
    int textWidth = MeasureText(text.c_str(), fontSize);
    DrawText(text.c_str(), (int)(position.x - textWidth/2), (int)position.y, fontSize, color);
}

void DrawTextWithShadow(const std::string& text, Vector2 position, int fontSize, Color textColor, Color shadowColor) {
    DrawText(text.c_str(), (int)position.x + 2, (int)position.y + 2, fontSize, shadowColor);
    DrawText(text.c_str(), (int)position.x, (int)position.y, fontSize, textColor);
}
