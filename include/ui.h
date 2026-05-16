#ifndef UI_H
#define UI_H

#include "raylib.h"
#include <string>
#include <vector>

enum class UIState {
    MENU_MAIN,
    MENU_MULTIPLAYER,
    LOBBY_CREATE,
    LOBBY_JOIN,
    GAME_SETUP,
    PLAYING,
    PAUSED,
    TURN_END,
    VICTORY,
    TRADE_SCREEN,
    CARD_SCREEN
};

enum class PanelType {
    MARKET_INFO,
    PLAYER_PORTFOLIO,
    ACTION_PANEL,
    CHAT_TRADE,
    EVENT_CARD,
    SETTINGS
};

struct Button {
    Rectangle bounds;
    std::string text;
    bool enabled;
    bool visible;
    Color normalColor;
    Color hoverColor;
    Color pressedColor;
    int id;
};

struct InputField {
    Rectangle bounds;
    std::string text;
    std::string placeholder;
    bool active;
    int maxLength;
    int id;
};

struct Panel {
    Rectangle bounds;
    PanelType type;
    bool visible;
    bool collapsible;
    bool collapsed;
    std::string title;
};

struct TradeOffer {
    int fromPlayer;
    int toPlayer;
    std::vector<std::pair<std::string, int>> offeredStocks; // companyId, quantity
    std::vector<std::pair<std::string, int>> requestedStocks;
    float offeredMoney;
    float requestedMoney;
    bool accepted;
    bool rejected;
};

class UI {
private:
    UIState currentState;
    UIState previousState;
    
    std::vector<Button> buttons;
    std::vector<InputField> inputFields;
    std::vector<Panel> panels;
    
    // Elementos específicos
    Rectangle gameArea;
    Rectangle sidebarLeft;
    Rectangle sidebarRight;
    Rectangle topBar;
    Rectangle bottomBar;
    
    // Para cartas de eventos
    bool showEventCard;
    float cardAnimationProgress;
    std::string currentEventTitle;
    std::string currentEventDescription;
    
    // Para trading
    bool showTradeScreen;
    TradeOffer currentTrade;
    
    // Temporizador visual
    float turnTimer;
    float maxTurnTime;
    
public:
    UI();
    
    void initialize();
    void update();
    void draw();
    
    // Gestión de estados
    void setState(UIState state);
    UIState getState() const;
    void pushState(UIState state);
    void popState();
    
    // Dibujado específico
    void drawMainMenu();
    void drawMultiplayerMenu();
    void drawLobby();
    void drawGameSetup();
    void drawGameHUD();
    void drawPauseMenu();
    void drawVictoryScreen();
    void drawTradeScreen();
    void drawCardPopup();
    
    // Elementos de interfaz
    void drawButton(Button& button);
    void drawInputField(InputField& field);
    void drawPanel(Panel& panel);
    void drawTurnTimer();
    void drawPlayerInfo(int playerId);
    void drawMarketSummary();
    void drawPortfolio();
    void drawActionButtons();
    void drawChatMessage(const std::string& message, Color color);
    
    // Eventos de entrada
    bool handleButtonClick(int buttonId);
    bool handleInputTyping(int fieldId, int key);
    void handleMouseClick(Vector2 mousePos);
    void handleMouseHover(Vector2 mousePos);
    
    // Utilidades
    void showEventCard(const std::string& title, const std::string& description);
    void hideEventCard();
    void startTrade(int fromPlayer, int toPlayer);
    void acceptTrade();
    void rejectTrade();
    
    // Getters/Setters
    void setTurnTimer(float time);
    float getTurnTimer() const;
    void setMaxTurnTime(float time);
    
    std::string getInputText(int fieldId) const;
    void setInputText(int fieldId, const std::string& text);
};

// Funciones de utilidad para dibujar
void DrawRectangleRoundedLines(Rectangle rec, float roundness, int segments, float lineThick, Color color);
void DrawTextCentered(const std::string& text, Vector2 position, int fontSize, Color color);
void DrawTextWithShadow(const std::string& text, Vector2 position, int fontSize, Color textColor, Color shadowColor);

#endif // UI_H
