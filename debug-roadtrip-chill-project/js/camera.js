/**
 * Roadtrip Chill - Sistema de Cámara y Renderizado
 * Maneja las diferentes vistas de cámara, ciclo día/noche y efectos visuales
 */

// Variables temporales para interpolación de cámara
var _camPos = null;
var _camLook = null;

// Actualizar cámara principal
function updateCamera(dt) {
  if (G.photoMode) {
    updatePhotoCamera(dt);
    return;
  }

  if (G.onFoot) {
    // La cámara se actualiza en updateOnFootCamera
    return;
  }

  if (!G.vehicle) return;

  var targetPos, targetLook;

  // Modo 0: Tercera persona clásica
  if (G.cameraMode === 0) {
    var camDist = 12 + G.speed * 0.05;
    var camHeight = 5 + G.speed * 0.02;

    targetPos = {
      x: G.vehicle.position.x + Math.sin(G.heading) * camDist,
      y: camHeight,
      z: G.vehicle.position.z + Math.cos(G.heading) * camDist
    };
    targetLook = {
      x: G.vehicle.position.x - Math.sin(G.heading) * 10,
      y: 2,
      z: G.vehicle.position.z - Math.cos(G.heading) * 10
    };
  }
  // Modo 1: Vista más cercana/deportiva
  else if (G.cameraMode === 1) {
    var closeDist = 8;
    var closeHeight = 3;

    targetPos = {
      x: G.vehicle.position.x + Math.sin(G.heading) * closeDist,
      y: closeHeight,
      z: G.vehicle.position.z + Math.cos(G.heading) * closeDist
    };
    targetLook = {
      x: G.vehicle.position.x - Math.sin(G.heading) * 5,
      y: 1,
      z: G.vehicle.position.z - Math.cos(G.heading) * 5
    };
  }
  // Modo 2: Primera persona (desde el conductor)
  else {
    targetPos = {
      x: G.vehicle.position.x - Math.sin(G.heading) * 0.5,
      y: G.cabinBottom + 1.2,
      z: G.vehicle.position.z - Math.cos(G.heading) * 0.5
    };
    targetLook = {
      x: G.vehicle.position.x - Math.sin(G.heading) * 20,
      y: G.cabinBottom + 1,
      z: G.vehicle.position.z - Math.cos(G.heading) * 20
    };
  }

  // Interpolación suave
  if (!_camPos) _camPos = new THREE.Vector3();
  if (!_camLook) _camLook = new THREE.Vector3();

  _camPos.lerp(new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z), 0.1);
  _camLook.lerp(new THREE.Vector3(targetLook.x, targetLook.y, targetLook.z), 0.1);

  G.camera.position.copy(_camPos);
  G.camera.lookAt(_camLook);

  // Camera shake según velocidad y clima
  if (G.weather === 'rain' || G.speed > 60) {
    G.cameraShake = Math.min(G.cameraShake + dt * 0.5, 0.15);
  } else {
    G.cameraShake = Math.max(G.cameraShake - dt, 0);
  }

  if (G.cameraShake > 0.01) {
    G.camera.position.x += (Math.random() - 0.5) * G.cameraShake;
    G.camera.position.y += (Math.random() - 0.5) * G.cameraShake;
    G.camera.position.z += (Math.random() - 0.5) * G.cameraShake;
  }
}

// Actualizar cámara en modo pasajero
function updatePassengerCamera(dt) {
  if (!G.vehicle) return;

  // Vista desde el asiento del pasajero
  var offset = 0.8;
  var lookDist = 15;

  G.camera.position.set(
    G.vehicle.position.x + offset,
    G.cabinBottom + 1.1,
    G.vehicle.position.z
  );

  G.camera.lookAt(
    G.vehicle.position.x - Math.sin(G.heading) * lookDist,
    G.cabinBottom + 1,
    G.vehicle.position.z - Math.cos(G.heading) * lookDist
  );
}

// Actualizar cámara en modo foto
function updatePhotoCamera(dt) {
  var rotSpeed = 1.5;
  var moveSpeed = 8;

  // Rotación con Q/E
  if (G.keys['KeyQ']) {
    G.charHeading += rotSpeed * dt;
  }
  if (G.keys['KeyE']) {
    G.charHeading -= rotSpeed * dt;
  }

  // Movimiento con WASD
  var dx = 0, dz = 0;
  if (G.keys['KeyW'] || G.keys['ArrowUp']) {
    dx -= Math.sin(G.charHeading) * moveSpeed * dt;
    dz -= Math.cos(G.charHeading) * moveSpeed * dt;
  }
  if (G.keys['KeyS'] || G.keys['ArrowDown']) {
    dx += Math.sin(G.charHeading) * moveSpeed * dt;
    dz += Math.cos(G.charHeading) * moveSpeed * dt;
  }
  if (G.keys['KeyA'] || G.keys['ArrowLeft']) {
    dx -= Math.cos(G.charHeading) * moveSpeed * dt;
    dz += Math.sin(G.charHeading) * moveSpeed * dt;
  }
  if (G.keys['KeyD'] || G.keys['ArrowRight']) {
    dx += Math.cos(G.charHeading) * moveSpeed * dt;
    dz -= Math.sin(G.charHeading) * moveSpeed * dt;
  }

  // Obtener posición actual o inicializar
  var currentPos = getRefPos();
  currentPos.x += dx;
  currentPos.y += (G.keys['Shift'] ? moveSpeed : 0) * dt - (G.keys['Control'] ? moveSpeed : 0) * dt;
  currentPos.z += dz;

  G.camera.position.copy(currentPos);

  // Dirección de mirada
  var lookX = currentPos.x - Math.sin(G.charHeading);
  var lookY = currentPos.y - Math.tan(0.2);
  var lookZ = currentPos.z - Math.cos(G.charHeading);

  G.camera.lookAt(lookX, lookY, lookZ);
}

// Interpolar color
function lerpC(c1, c2, t) {
  return new THREE.Color(c1).lerp(new THREE.Color(c2), t).getHex();
}

// Actualizar ciclo día/noche
function updateDayNight(dt) {
  G.gameTime += dt * 60; // 1 segundo real = 1 minuto en juego

  if (G.gameTime >= 1440) {
    G.gameTime = 0;
  }

  // Hora del día (0-1440 minutos)
  var hour = G.gameTime / 60;
  var dayProgress = G.gameTime / 1440;

  // Colores del cielo según hora
  var skyColor;
  var fogColor;
  var sunIntensity = 1.2;
  var starOpacity = 0;

  if (hour >= 5 && hour < 7) {
    // Amanecer
    skyColor = lerpC(0x1a1a2e, 0x87CEEB, (hour - 5) / 2);
    fogColor = skyColor;
    sunIntensity = (hour - 5) / 2 * 1.2;
  } else if (hour >= 7 && hour < 17) {
    // Día
    skyColor = 0x87CEEB;
    fogColor = 0x87CEEB;
    sunIntensity = 1.2;
  } else if (hour >= 17 && hour < 19) {
    // Atardecer
    skyColor = lerpC(0x87CEEB, 0xff6b6b, (hour - 17) / 2);
    fogColor = skyColor;
    sunIntensity = 1.2 - (hour - 17) / 2 * 0.8;
  } else if (hour >= 19 && hour < 21) {
    // Anochecer
    skyColor = lerpC(0xff6b6b, 0x1a1a2e, (hour - 19) / 2);
    fogColor = skyColor;
    sunIntensity = 0.4 - (hour - 19) / 2 * 0.4;
    starOpacity = (hour - 19) / 2;
  } else {
    // Noche
    skyColor = 0x1a1a2e;
    fogColor = 0x1a1a2e;
    sunIntensity = 0;
    starOpacity = 1;
  }

  // Aplicar colores
  G.scene.background.setHex(skyColor);
  G.scene.fog.color.setHex(fogColor);

  if (G.skyMesh) {
    G.skyMesh.material.color.setHex(skyColor);
  }

  if (G.dirLight) {
    G.dirLight.intensity = sunIntensity;
  }

  if (G.starField) {
    G.starField.material.opacity = starOpacity;
  }

  // Posición del sol/luna
  var sunAngle = (dayProgress - 0.25) * Math.PI * 2;
  if (G.sunMesh) {
    G.sunMesh.position.x = Math.cos(sunAngle) * 300;
    G.sunMesh.position.y = Math.sin(sunAngle) * 300;
  }
  if (G.moonMesh) {
    G.moonMesh.position.x = -Math.cos(sunAngle) * 300;
    G.moonMesh.position.y = Math.sin(sunAngle) * 300;
  }
}

// Actualizar clima
function updateWeather(dt) {
  G.weatherTimer -= dt;

  if (G.weatherTimer <= 0) {
    // Cambiar clima aleatoriamente
    var rand = Math.random();
    if (rand < 0.7) {
      G.weather = 'clear';
    } else if (rand < 0.9) {
      G.weather = 'cloudy';
    } else {
      G.weather = 'rain';
    }

    G.weatherTimer = 60 + Math.random() * 120; // 1-3 minutos

    if (G.weather !== 'clear') {
      notify('🌤️ El clima cambió a ' + (G.weather === 'rain' ? 'lluvia' : 'nublado'));
    }
  }

  // Efectos visuales del clima
  if (G.rainParticles) {
    if (G.weather === 'rain') {
      G.rainParticles.material.opacity = 0.6;
    } else {
      G.rainParticles.material.opacity = 0;
    }

    // Animar partículas de lluvia
    if (G.weather === 'rain') {
      var positions = G.rainParticles.geometry.attributes.position.array;
      for (var i = 1; i < positions.length; i += 3) {
        positions[i] -= 2;
        if (positions[i] < 0) {
          positions[i] = 120;
        }
      }
      G.rainParticles.geometry.attributes.position.needsUpdate = true;
    }
  }

  // Ajustar niebla según clima
  if (G.weather === 'rain') {
    G.scene.fog.near = 50;
    G.scene.fog.far = 200;
  } else if (G.weather === 'cloudy') {
    G.scene.fog.near = 80;
    G.scene.fog.far = 300;
  } else {
    G.scene.fog.near = 100;
    G.scene.fog.far = 400;
  }
}

// Obtener posición de referencia para la cámara
function getRefPos() {
  if (!G.camera.userData.refPos) {
    G.camera.userData.refPos = G.camera.position.clone();
  }
  return G.camera.userData.refPos;
}

// Exportar funciones
if (typeof window !== 'undefined') {
  window.updateCamera = updateCamera;
  window.updatePassengerCamera = updatePassengerCamera;
  window.updatePhotoCamera = updatePhotoCamera;
  window.lerpC = lerpC;
  window.updateDayNight = updateDayNight;
  window.updateWeather = updateWeather;
  window.getRefPos = getRefPos;
}
