/**
 * Roadtrip Chill - Sistema de Juego Principal
 * Maneja el loop principal, actualizaciones de estado y lógica del juego
 */

// Actualizar sueño del conductor
function updateSleepiness(dt) {
  if (!G.running || G.paused) return;

  // El sueño aumenta con el tiempo
  G.sleepiness += dt * 0.5;

  // El sueño aumenta más rápido de noche
  var hour = G.gameTime / 60;
  if (hour >= 22 || hour < 6) {
    G.sleepiness += dt * 0.8;
  }

  // El sueño aumenta más rápido con lluvia
  if (G.weather === 'rain') {
    G.sleepiness += dt * 0.3;
  }

  // Limitar a 100
  G.sleepiness = Math.min(100, G.sleepiness);

  // Efectos cuando hay mucho sueño
  if (G.sleepiness > 70 && !G.atMotel) {
    document.getElementById('motelIndicator').classList.add('visible');
    
    // Reducir control del vehículo
    if (!G.onFoot && G.speed > 30) {
      G.steerAngle += (Math.random() - 0.5) * 0.02;
    }
  } else {
    document.getElementById('motelIndicator').classList.remove('visible');
  }

  // Si llega a 100, forzar parada
  if (G.sleepiness >= 100 && !G.atMotel) {
    G.speed *= 0.95;
    notify('😴 ¡Demasiado cansado! Parate en un motel');
  }
}

// Actualizar combustible
function updateFuel(dt) {
  if (!G.running || G.paused || G.onFoot) return;

  // Consumo base
  var consumption = 0.3;

  // Más consumo a alta velocidad
  if (G.speed > 60) {
    consumption += 0.2;
  }

  // Menos consumo a baja velocidad
  if (G.speed < 20) {
    consumption -= 0.1;
  }

  G.fuel -= consumption * dt;

  if (G.fuel <= 0) {
    G.fuel = 0;
    G.speed *= 0.98;
    notify('⛔ Sin combustible! Buscá una estación de servicio');
  }

  if (G.fuel < 20 && G.fuel > 0) {
    notify('⚠️ Combustible bajo');
  }
}

// Actualizar chunks del mundo
function updateChunks() {
  if (!G.vehicle) return;

  var playerZ = G.onFoot ? G.character.position.z : G.vehicle.position.z;

  // Generar nuevos chunks adelante
  while (G.decorPool.length === 0 || 
         G.decorPool[G.decorPool.length - 1].position.z < playerZ + 300) {
    var lastZ = G.decorPool.length > 0 ? 
                G.decorPool[G.decorPool.length - 1].position.z : 0;
    generateChunk(lastZ + 100);
  }

  // Eliminar chunks atrás
  for (var i = G.decorPool.length - 1; i >= 0; i--) {
    if (G.decorPool[i].position.z < playerZ - 200) {
      G.scene.remove(G.decorPool[i]);
      G.decorPool.splice(i, 1);
    }
  }
}

// Actualizar otros autos en la ruta
function updateOtherCars(dt) {
  if (!G.otherCars || G.otherCars.length === 0) return;

  for (var i = 0; i < G.otherCars.length; i++) {
    var car = G.otherCars[i];
    
    // Mover auto en dirección contraria o misma dirección
    var speed = car.userData.speed || 40;
    car.position.z += speed * dt;

    // Seguir curva de la ruta
    car.position.x = getRoadCurve(car.position.z);

    // Eliminar si está muy lejos
    var refZ = G.onFoot ? G.character.position.z : G.vehicle.position.z;
    if (Math.abs(car.position.z - refZ) > 500) {
      G.scene.remove(car);
      G.otherCars.splice(i, 1);
      i--;
    }
  }
}

// Verificar colisiones con autos
function checkCarCollisions(dt) {
  if (!G.vehicle || G.onFoot) return;

  G.collisionCooldown -= dt;

  for (var i = 0; i < G.otherCars.length; i++) {
    var other = G.otherCars[i];
    var dist = G.vehicle.position.distanceTo(other.position);

    if (dist < 5 && G.collisionCooldown <= 0) {
      // Colisión!
      G.speed *= 0.3;
      G.cameraShake = 0.3;
      G.collisionCooldown = 2;

      notify('💥 ¡Choque! Tené cuidado');

      // Pequeño aumento de sueño por estrés
      G.sleepiness += 5;

      break;
    }
  }
}

// Verificar eventos visuales
function checkVisualEvents(dt) {
  if (!G.running || G.paused) return;

  G.lastEventTime += dt;

  // Evento cada 30-90 segundos
  if (G.lastEventTime > G.nextEventTime) {
    G.lastEventTime = 0;
    G.nextEventTime = 30 + Math.random() * 60;

    // Elegir evento aleatorio
    var evt = VISUAL_EVENTS[Math.floor(Math.random() * VISUAL_EVENTS.length)];
    spawnVisualEvent(evt);
  }

  updateVisualEvents(dt);
}

// Spawnear evento visual
function spawnVisualEvent(evt) {
  if (G.currentEventVisual) {
    cleanupEvent();
  }

  G.currentEventVisual = evt;

  // Mostrar mensaje
  var indicator = document.getElementById('eventIndicator');
  indicator.textContent = evt.msg;
  indicator.classList.add('visible');

  // Spawnear objeto visual según tipo
  var refZ = G.onFoot ? G.character.position.z : G.vehicle.position.z;
  var eventZ = refZ + 100;

  switch (evt.type) {
    case 'deer':
      spawnDeer(eventZ);
      break;
    case 'bird':
      spawnBirds(eventZ);
      break;
    case 'rainbow':
      spawnRainbow(eventZ);
      break;
    case 'stalled':
      spawnStalledCar(eventZ);
      break;
    case 'scenic':
      spawnScenicView(eventZ);
      break;
  }

  // Ocultar indicador después de un tiempo
  setTimeout(function() {
    indicator.classList.remove('visible');
  }, evt.dur * 1000);
}

// Actualizar eventos visuales activos
function updateVisualEvents(dt) {
  if (!G.currentEventVisual) return;

  G.currentEventVisual.dur -= dt;

  if (G.currentEventVisual.dur <= 0) {
    // Aplicar efecto
    if (G.currentEventVisual.impact.sleep) {
      G.sleepiness = Math.max(0, Math.min(100, 
        G.sleepiness + G.currentEventVisual.impact.sleep));
    }

    notify(G.currentEventVisual.result);
    G.eventsCompleted++;

    cleanupEvent();
  }
}

// Limpiar evento visual
function cleanupEvent() {
  if (G.currentEventVisual && G.currentEventVisual.mesh) {
    G.scene.remove(G.currentEventVisual.mesh);
  }
  G.currentEventVisual = null;
}

// Spawnear ciervo
function spawnDeer(z) {
  var deer = new THREE.Group();

  var body = new THREE.Mesh(
    new THREE.BoxGeometry(0.5, 0.4, 1),
    new THREE.MeshLambertMaterial({ color: 0x8b4513 })
  );
  body.position.y = 0.5;
  deer.add(body);

  var head = new THREE.Mesh(
    new THREE.BoxGeometry(0.3, 0.3, 0.4),
    new THREE.MeshLambertMaterial({ color: 0x8b4513 })
  );
  head.position.set(0, 0.8, -0.4);
  deer.add(head);

  deer.position.set(getRoadCurve(z) + 5, 0, z);
  G.scene.add(deer);

  if (G.currentEventVisual) {
    G.currentEventVisual.mesh = deer;
  }
}

// Spawnear pájaros
function spawnBirds(z) {
  var birds = new THREE.Group();

  for (var i = 0; i < 5; i++) {
    var bird = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 8, 8),
      new THREE.MeshLambertMaterial({ color: 0xffffff })
    );
    bird.position.set(
      (Math.random() - 0.5) * 3,
      15 + Math.random() * 5,
      z + (Math.random() - 0.5) * 5
    );
    birds.add(bird);
  }

  G.scene.add(birds);

  if (G.currentEventVisual) {
    G.currentEventVisual.mesh = birds;
  }
}

// Spawnear arcoíris
function spawnRainbow(z) {
  var rainbow = new THREE.Group();
  var colors = [0xff0000, 0xff7f00, 0xffff00, 0x00ff00, 0x0000ff, 0x4b0082, 0x9400d3];

  for (var i = 0; i < colors.length; i++) {
    var arc = new THREE.Mesh(
      new THREE.TorusGeometry(30 - i * 4, 0.5, 8, 50, Math.PI),
      new THREE.MeshBasicMaterial({ color: colors[i], transparent: true, opacity: 0.6 })
    );
    arc.rotation.x = -Math.PI / 2;
    arc.position.set(getRoadCurve(z), 20, z + 50);
    rainbow.add(arc);
  }

  G.scene.add(rainbow);

  if (G.currentEventVisual) {
    G.currentEventVisual.mesh = rainbow;
  }
}

// Spawnear auto averiado
function spawnStalledCar(z) {
  var stalled = new THREE.Mesh(
    new THREE.BoxGeometry(2, 0.8, 4),
    new THREE.MeshLambertMaterial({ color: 0x555555 })
  );
  stalled.position.set(getRoadCurve(z) + 2, 0.4, z);
  G.scene.add(stalled);

  if (G.currentEventVisual) {
    G.currentEventVisual.mesh = stalled;
  }
}

// Spawnear vista panorámica
function spawnScenicView(z) {
  // La vista panorática es más un efecto de cámara que un objeto
  // Podríamos añadir montañas especiales o miradores
  var viewpoint = new THREE.Group();

  var mountain = new THREE.Mesh(
    new THREE.ConeGeometry(40, 60, 8),
    new THREE.MeshLambertMaterial({ color: 0x6b8c85 })
  );
  mountain.position.set(getRoadCurve(z) - 80, 30, z);
  viewpoint.add(mountain);

  G.scene.add(viewpoint);

  if (G.currentEventVisual) {
    G.currentEventVisual.mesh = viewpoint;
  }
}

// Actualizar indicador de motel
function updateMotelIndicator(dt) {
  if (!G.running || G.paused || G.atMotel) return;

  var refPos = G.onFoot ? G.character.position : G.vehicle.position;
  var minDist = Infinity;
  G.nearestMotelIdx = -1;

  for (var i = 0; i < G.motels.length; i++) {
    var motel = G.motels[i];
    var dist = Math.abs(motel.z - refPos.z);

    if (dist < minDist && dist < 100) {
      minDist = dist;
      G.nearestMotelIdx = i;
    }
  }

  // Mostrar/ocultar indicador
  var indicator = document.getElementById('motelIndicator');
  if (G.nearestMotelIdx !== -1 && G.sleepiness > 50) {
    indicator.style.display = 'block';
    indicator.textContent = '🏨 Motel a ' + Math.round(minDist) + 'm';
  } else {
    indicator.style.display = 'none';
  }
}

// Actualizar brillo de moteles
function updateMotelGlow(dt) {
  var refPos = G.onFoot ? G.character.position : G.vehicle.position;

  for (var i = 0; i < G.motels.length; i++) {
    var motel = G.motels[i];
    var dist = Math.abs(motel.z - refPos.z);

    if (dist < 30) {
      motel.active = true;
    } else {
      motel.active = false;
    }
  }
}

// Actualizar brillo de estaciones de servicio
function updateGasGlow(dt) {
  var refPos = G.onFoot ? G.character.position : G.vehicle.position;

  for (var i = 0; i < G.gasStations.length; i++) {
    var station = G.gasStations[i];
    var dist = Math.abs(station.z - refPos.z);

    if (dist < 30 && G.fuel < 50) {
      station.active = true;
    } else {
      station.active = false;
    }
  }
}

// Exportar funciones
if (typeof window !== 'undefined') {
  window.updateSleepiness = updateSleepiness;
  window.updateFuel = updateFuel;
  window.updateChunks = updateChunks;
  window.updateOtherCars = updateOtherCars;
  window.checkCarCollisions = checkCarCollisions;
  window.checkVisualEvents = checkVisualEvents;
  window.spawnVisualEvent = spawnVisualEvent;
  window.updateVisualEvents = updateVisualEvents;
  window.cleanupEvent = cleanupEvent;
  window.updateMotelIndicator = updateMotelIndicator;
  window.updateMotelGlow = updateMotelGlow;
  window.updateGasGlow = updateGasGlow;
}
