#ifndef BOARD_H
#define BOARD_H

#include "raylib.h"
#include <vector>
#include <string>

struct Sector3D {
    std::string id;
    std::string name;
    Vector3 position;
    Vector3 size;
    Color color;
    float rotation;
    bool isSelected;
};

struct CompanyMarker {
    std::string companyId;
    std::string companyName;
    Vector3 position;
    Model model;
    bool isHighlighted;
    float price;
};

struct CameraControl {
    Camera3D camera;
    Vector3 target;
    float distance;
    float rotationSpeed;
    float zoomSpeed;
    int viewPreset; // 0: libre, 1: superior, 2: lateral, 3: detalle
};

class Board {
private:
    std::vector<Sector3D> sectors;
    std::vector<CompanyMarker> companyMarkers;
    CameraControl cameraControl;
    Vector3 boardCenter;
    float boardSize;
    
    // Para rotación independiente por jugador
    std::vector<Camera3D> playerCameras;
    int activePlayerCamera;
    
public:
    Board();
    ~Board();
    
    void initialize();
    void update();
    void draw();
    
    // Gestión de cámara
    void rotateCamera(Vector2 mouseDelta);
    void zoomCamera(float delta);
    void setCameraPreset(int preset);
    void setPlayerCamera(int playerId);
    Camera3D& getActiveCamera();
    
    // Interacción
    CompanyMarker* raycastCompany(Ray ray);
    Sector3D* raycastSector(Ray ray);
    bool isMouseOverCompany(Vector2 mousePos);
    bool isMouseOverSector(Vector2 mousePos);
    
    // Renderizado específico
    void drawSectors();
    void drawCompanies();
    void drawGrid();
    void drawLabels();
    
    // Utilidades
    Vector3 getSectorPosition(const std::string& sectorId);
    Vector3 getCompanyPosition(const std::string& companyId);
    void highlightCompany(const std::string& companyId, bool highlight);
    void highlightSector(const std::string& sectorId, bool highlight);
    
    // Limpieza
    void unload();
};

#endif // BOARD_H
