#include "board.h"
#include "raymath.h"

Board::Board() : boardCenter({0, 0, 0}), boardSize(100.0f), activePlayerCamera(0) {
    cameraControl.camera.position = {0, 80, 80};
    cameraControl.camera.target = {0, 0, 0};
    cameraControl.camera.up = {0, 1, 0};
    cameraControl.camera.fovy = 45.0f;
    cameraControl.camera.projection = CAMERA_PERSPECTIVE;
    cameraControl.distance = 100.0f;
    cameraControl.rotationSpeed = 0.5f;
    cameraControl.zoomSpeed = 2.0f;
    cameraControl.viewPreset = 0;
}

Board::~Board() {
    unload();
}

void Board::initialize() {
    // Crear sectores
    const char* sectorIds[] = {"TECH", "ENRG", "TOUR", "FIN", "HLTH", "REAL", "CONS", "IND"};
    const char* sectorNames[] = {"Tecnología", "Energía", "Turismo", "Finanzas", 
                                  "Salud", "Inmobiliario", "Consumo", "Industrial"};
    Color sectorColors[] = {BLUE, ORANGE, YELLOW, GREEN, PINK, BROWN, MAGENTA, GRAY};
    
    for (int i = 0; i < 8; i++) {
        Sector3D sector;
        sector.id = sectorIds[i];
        sector.name = sectorNames[i];
        
        // Posicionar en círculo
        float angle = (i * 2 * PI) / 8;
        sector.position.x = cosf(angle) * 30;
        sector.position.z = sinf(angle) * 30;
        sector.position.y = 0;
        
        sector.size = {15, 2, 15};
        sector.color = sectorColors[i];
        sector.rotation = 0;
        sector.isSelected = false;
        
        sectors.push_back(sector);
    }
    
    // Crear marcadores de empresas
    const char* companyIds[] = {"TECH1", "TECH2", "ENRG1", "ENRG2", "TOUR1", "TOUR2", 
                                 "FIN1", "FIN2", "HLTH1", "HLTH2", "REAL1", "REAL2",
                                 "CONS1", "CONS2", "IND1", "IND2"};
    const char* companyNames[] = {"TechCorp", "InnovateX", "PowerCo", "GreenEnergy",
                                   "TravelWorld", "HotelChain", "BankCorp", "InvestPlus",
                                   "PharmaInc", "BioTech", "EstatePro", "BuildCorp",
                                   "RetailMax", "FoodCo", "ManufactureX", "SteelWorks"};
    
    for (int i = 0; i < 16; i++) {
        CompanyMarker marker;
        marker.companyId = companyIds[i];
        marker.companyName = companyNames[i];
        
        // Posicionar cerca del sector correspondiente
        int sectorIndex = i / 2;
        float angle = (sectorIndex * 2 * PI) / 8;
        float offset = ((i % 2) == 0) ? 8.0f : -8.0f;
        
        marker.position.x = cosf(angle) * 30 + cosf(angle + PI/2) * offset;
        marker.position.z = sinf(angle) * 30 + sinf(angle + PI/2) * offset;
        marker.position.y = 2;
        
        marker.isHighlighted = false;
        marker.price = 100.0f;
        
        // Modelo simple (cilindro o cubo)
        marker.model = LoadModelFromMesh(GenMeshCube(2, 3, 2));
        
        companyMarkers.push_back(marker);
    }
}

void Board::update() {
    // Control de cámara con teclado
    if (IsKeyDown(KEY_ONE)) setCameraPreset(1);
    if (IsKeyDown(KEY_TWO)) setCameraPreset(2);
    if (IsKeyDown(KEY_THREE)) setCameraPreset(3);
    
    // Rotación con mouse
    if (IsMouseButtonDown(MOUSE_BUTTON_RIGHT)) {
        Vector2 delta = GetMouseDelta();
        rotateCamera(delta);
    }
    
    // Zoom con rueda
    float wheel = GetMouseWheelMove();
    zoomCamera(wheel);
    
    // Actualizar cámaras de jugadores
    if (!playerCameras.empty() && activePlayerCamera < playerCameras.size()) {
        cameraControl.camera = playerCameras[activePlayerCamera];
    }
}

void Board::draw() {
    BeginMode3D(cameraControl.camera);
    
    drawGrid();
    drawSectors();
    drawCompanies();
    drawLabels();
    
    EndMode3D();
}

void Board::rotateCamera(Vector2 mouseDelta) {
    float yaw = -mouseDelta.x * cameraControl.rotationSpeed * DEG2RAD;
    float pitch = -mouseDelta.y * cameraControl.rotationSpeed * DEG2RAD;
    
    Vector3 direction = Vector3Subtract(cameraControl.camera.position, cameraControl.camera.target);
    float distance = Vector3Length(direction);
    
    // Aplicar rotación
    Matrix yawMatrix = MatrixRotateY(yaw);
    direction = Vector3Transform(direction, yawMatrix);
    
    Matrix pitchMatrix = MatrixRotateX(pitch);
    direction = Vector3Transform(direction, pitchMatrix);
    
    // Limitar pitch
    if (direction.y > distance * 0.95f) direction.y = distance * 0.95f;
    if (direction.y < -distance * 0.95f) direction.y = -distance * 0.95f;
    
    cameraControl.camera.position = Vector3Add(cameraControl.camera.target, direction);
}

void Board::zoomCamera(float delta) {
    Vector3 direction = Vector3Subtract(cameraControl.camera.position, cameraControl.camera.target);
    float distance = Vector3Length(direction);
    
    distance -= delta * cameraControl.zoomSpeed;
    distance = fmaxf(20.0f, fminf(200.0f, distance));
    
    direction = Vector3Normalize(direction);
    cameraControl.camera.position = Vector3Add(cameraControl.camera.target, 
                                                Vector3Scale(direction, distance));
}

void Board::setCameraPreset(int preset) {
    switch (preset) {
        case 1: // Vista superior
            cameraControl.camera.position = {0, 100, 0};
            cameraControl.camera.target = {0, 0, 0};
            break;
        case 2: // Vista lateral
            cameraControl.camera.position = {100, 20, 0};
            cameraControl.camera.target = {0, 0, 0};
            break;
        case 3: // Vista detalle
            cameraControl.camera.position = {30, 30, 30};
            cameraControl.camera.target = {0, 0, 0};
            break;
    }
    cameraControl.viewPreset = preset;
}

void Board::setPlayerCamera(int playerId) {
    if (playerId >= playerCameras.size()) {
        Camera3D newCamera = cameraControl.camera;
        newCamera.position.x += playerId * 20;
        playerCameras.push_back(newCamera);
    }
    activePlayerCamera = playerId;
}

Camera3D& Board::getActiveCamera() {
    return cameraControl.camera;
}

CompanyMarker* Board::raycastCompany(Ray ray) {
    for (auto& marker : companyMarkers) {
        BoundingBox box = {
            {marker.position.x - 1, marker.position.y - 1.5f, marker.position.z - 1},
            {marker.position.x + 1, marker.position.y + 1.5f, marker.position.z + 1}
        };
        
        if (GetRayCollisionBox(ray, box).hit) {
            return &marker;
        }
    }
    return nullptr;
}

Sector3D* Board::raycastSector(Ray ray) {
    for (auto& sector : sectors) {
        BoundingBox box = {
            {sector.position.x - sector.size.x/2, sector.position.y - sector.size.y/2, sector.position.z - sector.size.z/2},
            {sector.position.x + sector.size.x/2, sector.position.y + sector.size.y/2, sector.position.z + sector.size.z/2}
        };
        
        if (GetRayCollisionBox(ray, box).hit) {
            return &sector;
        }
    }
    return nullptr;
}

bool Board::isMouseOverCompany(Vector2 mousePos) {
    Ray ray = GetCameraRay(cameraControl.camera, mousePos);
    return raycastCompany(ray) != nullptr;
}

bool Board::isMouseOverSector(Vector2 mousePos) {
    Ray ray = GetCameraRay(cameraControl.camera, mousePos);
    return raycastSector(ray) != nullptr;
}

void Board::drawSectors() {
    for (const auto& sector : sectors) {
        DrawCube(sector.position, sector.size.x, sector.size.y, sector.size.z, sector.color);
        DrawCubeWires(sector.position, sector.size.x, sector.size.y, sector.size.z, DARKGRAY);
    }
}

void Board::drawCompanies() {
    for (const auto& marker : companyMarkers) {
        Color color = marker.isHighlighted ? WHITE : LIGHTGRAY;
        DrawModel(marker.model, marker.position, 1.0f, color);
    }
}

void Board::drawGrid() {
    DrawGrid(20, 10.0f);
}

void Board::drawLabels() {
    // En una implementación completa, usaríamos texturas o fuentes 3D
    // Por ahora, dibujamos indicadores simples
    for (const auto& marker : companyMarkers) {
        Vector3 labelPos = {marker.position.x, marker.position.y + 3, marker.position.z};
        DrawText3D(marker.companyName.c_str(), labelPos, 2.0f, 0, WHITE);
    }
}

Vector3 Board::getSectorPosition(const std::string& sectorId) {
    for (const auto& sector : sectors) {
        if (sector.id == sectorId) {
            return sector.position;
        }
    }
    return {0, 0, 0};
}

Vector3 Board::getCompanyPosition(const std::string& companyId) {
    for (const auto& marker : companyMarkers) {
        if (marker.companyId == companyId) {
            return marker.position;
        }
    }
    return {0, 0, 0};
}

void Board::highlightCompany(const std::string& companyId, bool highlight) {
    for (auto& marker : companyMarkers) {
        if (marker.companyId == companyId) {
            marker.isHighlighted = highlight;
            break;
        }
    }
}

void Board::highlightSector(const std::string& sectorId, bool highlight) {
    for (auto& sector : sectors) {
        if (sector.id == sectorId) {
            sector.isSelected = highlight;
            break;
        }
    }
}

void Board::unload() {
    for (auto& marker : companyMarkers) {
        UnloadModel(marker.model);
    }
}
