/**
 * Roadtrip Chill - Sistema de Vehículos y Personajes
 * Maneja la creación del vehículo, personajes y controles de movimiento
 */

// Crear vehículo según número de jugadores
function createVehicle() {
  G.vehicle = new THREE.Group();

  var carColor = new THREE.Color(G.vehicleColor);
  var darkColor = darkenColor(G.vehicleColor, 0.7);

  // Cuerpo principal (varía según cantidad de jugadores)
  var bodyGeo = new THREE.BoxGeometry(G.vw, G.vh, G.vl);
  var bodyMat = new THREE.MeshLambertMaterial({ color: carColor });
  G.vehicleBody = new THREE.Mesh(bodyGeo, bodyMat);
  G.vehicleBody.position.y = G.vh / 2 + 0.3;
  G.vehicleBody.castShadow = true;
  G.vehicle.add(G.vehicleBody);

  // Cabina
  var cabinGeo = new THREE.BoxGeometry(G.cw, G.ch, G.cl);
  var cabinMat = new THREE.MeshLambertMaterial({ color: 0x333333 });
  var cabin = new THREE.Mesh(cabinGeo, cabinMat);
  cabin.position.set(0, G.vh + G.ch / 2, -0.2);
  cabin.castShadow = true;
  G.vehicle.add(cabin);

  G.cabinBottom = G.vh;

  // Ruedas
  G.wheels = [];
  var wheelGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.2, 12);
  var wheelMat = new THREE.MeshLambertMaterial({ color: 0x222222 });

  var wheelPositions = [
    [-G.vw / 2 - 0.1, 0.35, G.vl / 2 - 0.8],
    [G.vw / 2 + 0.1, 0.35, G.vl / 2 - 0.8],
    [-G.vw / 2 - 0.1, 0.35, -G.vl / 2 + 0.8],
    [G.vw / 2 + 0.1, 0.35, -G.vl / 2 + 0.8]
  ];

  for (var i = 0; i < 4; i++) {
    var wheel = new THREE.Mesh(wheelGeo, wheelMat);
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(wheelPositions[i][0], wheelPositions[i][1], wheelPositions[i][2]);
    G.vehicle.add(wheel);
    G.wheels.push(wheel);
  }

  // Faros delanteros
  var headlightGeo = new THREE.SphereGeometry(0.2, 8, 8);
  var headlightMat = new THREE.MeshLambertMaterial({ color: 0xffffaa, emissive: 0xffffaa, emissiveIntensity: 0.5 });

  var hlLeft = new THREE.Mesh(headlightGeo, headlightMat);
  hlLeft.position.set(-G.vw / 3, 0.6, G.vl / 2 + 0.1);
  G.vehicle.add(hlLeft);

  var hlRight = new THREE.Mesh(headlightGeo, headlightMat);
  hlRight.position.set(G.vw / 3, 0.6, G.vl / 2 + 0.1);
  G.vehicle.add(hlRight);

  // Luces traseras
  var taillightMat = new THREE.MeshLambertMaterial({ color: 0xff0000, emissive: 0xff0000, emissiveIntensity: 0.3 });

  var tlLeft = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.3, 0.1), taillightMat);
  tlLeft.position.set(-G.vw / 3, 0.7, -G.vl / 2 - 0.1);
  G.vehicle.add(tlLeft);

  var tlRight = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.3, 0.1), taillightMat);
  tlRight.position.set(G.vw / 3, 0.7, -G.vl / 2 - 0.1);
  G.vehicle.add(tlRight);

  G.vehicle.position.set(0, 0, 0);
  G.scene.add(G.vehicle);

  // Crear personaje(s) dentro del vehículo
  createCharacter();
}

// Crear personaje
function createCharacter() {
  G.character = new THREE.Group();

  // Cuerpo
  var bodyMat = new THREE.MeshLambertMaterial({ color: 0x3498db });
  var bodyGeo = new THREE.CapsuleGeometry(0.3, 0.7, 4, 8);
  var body = new THREE.Mesh(bodyGeo, bodyMat);
  body.position.y = 0.65;
  G.character.add(body);

  // Cabeza
  var headGeo = new THREE.SphereGeometry(0.25, 8, 8);
  var head = new THREE.Mesh(headGeo, bodyMat);
  head.position.y = 1.4;
  G.character.add(head);

  G.character.visible = false;
  G.scene.add(G.character);

  // Grupo interior para pasajeros
  G.interiorGroup = new THREE.Group();
  G.vehicle.add(G.interiorGroup);

  // Crear asientos/pasajeros según cantidad
  var passengerCount = G.players - 1;
  for (var i = 0; i < passengerCount; i++) {
    var passenger = new THREE.Group();

    var pBody = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.25, 0.6, 4, 8),
      new THREE.MeshLambertMaterial({ color: COLORS[i % COLORS.length] })
    );
    pBody.position.y = 0.5;
    passenger.add(pBody);

    var pHead = new THREE.Mesh(
      new THREE.SphereGeometry(0.2, 8, 8),
      new THREE.MeshLambertMaterial({ color: COLORS[i % COLORS.length] })
    );
    pHead.position.y = 1.1;
    passenger.add(pHead);

    // Posicionar según lugar en el vehículo
    if (i === 0) {
      passenger.position.set(G.vw / 3, G.cabinBottom, 0.3);
    } else if (i === 1) {
      passenger.position.set(-G.vw / 3, G.cabinBottom, 0.3);
    } else {
      var row = Math.floor((i - 2) / 2);
      var side = (i - 2) % 2 === 0 ? -1 : 1;
      passenger.position.set(side * G.vw / 4, G.cabinBottom, -0.5 - row * 0.8);
    }

    G.interiorGroup.add(passenger);
  }
}

// Configurar controles
function setupControls() {
  document.addEventListener('keydown', function(e) {
    G.keys[e.code] = true;

    // Pausa
    if (e.code === 'Escape') {
      togglePause();
    }

    // Subir/bajar del auto
    if (e.code === 'KeyF') {
      if (G.onFoot) {
        enterVehicle();
      } else {
        exitVehicle();
      }
    }

    // Modo foto
    if (e.code === 'KeyC' && !G.photoMode) {
      togglePhotoMode();
    }

    // Radio
    if (e.code === 'KeyR') {
      toggleRadio();
    }

    // Cambiar cámara
    if (e.code === 'KeyV') {
      G.cameraMode = (G.cameraMode + 1) % 3;
    }
  });

  document.addEventListener('keyup', function(e) {
    G.keys[e.code] = false;
  });
}

// Alternar pausa
function togglePause() {
  if (!G.running) return;

  G.paused = !G.paused;
  var pauseMenu = document.getElementById('pauseMenu');

  if (G.paused) {
    pauseMenu.classList.remove('hidden');
  } else {
    pauseMenu.classList.add('hidden');
  }
}

// Bajar del vehículo
function exitVehicle() {
  if (!G.vehicle) return;

  G.onFoot = true;
  G.speed = 0;

  // Posicionar personaje al lado del auto
  var vehiclePos = G.vehicle.position;
  G.character.position.set(
    vehiclePos.x + 2,
    0,
    vehiclePos.z + 2
  );
  G.character.visible = true;
  G.character.rotation.y = G.charHeading;

  // Ocultar modelo del auto o hacerlo semi-transparente
  if (G.vehicleBody) {
    G.vehicleBody.material.transparent = true;
    G.vehicleBody.material.opacity = 0.3;
  }
}

// Subir al vehículo
function enterVehicle() {
  if (!G.vehicle) return;

  var dist = G.character.position.distanceTo(G.vehicle.position);
  if (dist > 5) {
    notify('🚗 Acercate al auto para subir');
    return;
  }

  G.onFoot = false;
  G.character.visible = false;

  // Restaurar opacidad del auto
  if (G.vehicleBody) {
    G.vehicleBody.material.transparent = false;
    G.vehicleBody.material.opacity = 1;
  }

  notify('🚙 Subiste al auto');
}

// Actualizar personaje a pie
function updateOnFoot(dt) {
  if (!G.onFoot || !G.character) return;

  var moveSpeed = 3;
  var rotSpeed = 2;

  // Rotación
  if (G.keys['KeyA'] || G.keys['ArrowLeft']) {
    G.charHeading += rotSpeed * dt;
  }
  if (G.keys['KeyD'] || G.keys['ArrowRight']) {
    G.charHeading -= rotSpeed * dt;
  }

  G.character.rotation.y = G.charHeading;

  // Movimiento
  var dx = 0, dz = 0;
  if (G.keys['KeyW'] || G.keys['ArrowUp']) {
    dx -= Math.sin(G.charHeading) * moveSpeed * dt;
    dz -= Math.cos(G.charHeading) * moveSpeed * dt;
  }
  if (G.keys['KeyS'] || G.keys['ArrowDown']) {
    dx += Math.sin(G.charHeading) * moveSpeed * dt;
    dz += Math.cos(G.charHeading) * moveSpeed * dt;
  }

  G.character.position.x += dx;
  G.character.position.z += dz;

  // Bobbing al caminar
  G.charBobTime += dt * 10;
  G.character.position.y = Math.abs(Math.sin(G.charBobTime)) * 0.1;

  // Actualizar cámara
  updateOnFootCamera(dt);
}

// Actualizar cámara en modo a pie
function updateOnFootCamera(dt) {
  if (!G.character) return;

  var camDist = 8;
  var camHeight = 4;

  G.camera.position.x = G.character.position.x - Math.sin(G.charHeading) * camDist;
  G.camera.position.z = G.character.position.z - Math.cos(G.charHeading) * camDist;
  G.camera.position.y = G.character.position.y + camHeight;

  G.camera.lookAt(G.character.position);
}

// Actualizar conducción
function updateDriving(dt) {
  if (G.onFoot || !G.vehicle) return;

  // Aceleración
  var accel = 0;
  if (G.keys['KeyW'] || G.keys['ArrowUp']) {
    accel = 15;
  } else if (G.keys['KeyS'] || G.keys['ArrowDown']) {
    accel = -10;
  }

  // Fricción
  var friction = 5;
  if (G.weather === 'rain') {
    friction = 3;
  }

  // Aplicar aceleración/fricción
  if (accel !== 0) {
    G.speed += accel * dt;
  } else {
    if (G.speed > 0) {
      G.speed -= friction * dt;
      if (G.speed < 0) G.speed = 0;
    } else if (G.speed < 0) {
      G.speed += friction * dt;
      if (G.speed > 0) G.speed = 0;
    }
  }

  // Limitar velocidad
  var currentMaxSpeed = G.maxSpeed;
  if (G.weather === 'rain') {
    currentMaxSpeed = G.maxSpeed * 0.7;
  }

  G.speed = Math.max(-currentMaxSpeed / 3, Math.min(currentMaxSpeed, G.speed));

  // Dirección
  var steerSpeed = 1.5;
  if (Math.abs(G.speed) < 1) {
    steerSpeed = 0;
  }

  if (G.keys['KeyA'] || G.keys['ArrowLeft']) {
    G.steerAngle += steerSpeed * dt;
  } else if (G.keys['KeyD'] || G.keys['ArrowRight']) {
    G.steerAngle -= steerSpeed * dt;
  } else {
    // Retornar volante al centro
    if (G.steerAngle > 0) {
      G.steerAngle -= 2 * dt;
      if (G.steerAngle < 0) G.steerAngle = 0;
    } else if (G.steerAngle < 0) {
      G.steerAngle += 2 * dt;
      if (G.steerAngle > 0) G.steerAngle = 0;
    }
  }

  G.steerAngle = Math.max(-0.5, Math.min(0.5, G.steerAngle));

  // Calcular movimiento
  var moveDist = G.speed * dt;
  G.heading += G.steerAngle * (G.speed / G.maxSpeed) * dt;

  G.vehicle.position.x -= Math.sin(G.heading) * moveDist;
  G.vehicle.position.z -= Math.cos(G.heading) * moveDist;
  G.vehicle.position.y = 0;

  G.vehicle.rotation.y = G.heading;

  // Actualizar distancia recorrida
  if (moveDist > 0) {
    G.distance += Math.abs(moveDist) / 1000;
  }

  // Girar ruedas delanteras visualmente
  for (var i = 0; i < 2; i++) {
    if (G.wheels[i]) {
      G.wheels[i].rotation.y = G.steerAngle;
    }
  }

  // Hacer girar todas las ruedas
  var wheelRotSpeed = G.speed * 0.1;
  for (var j = 0; j < G.wheels.length; j++) {
    G.wheels[j].rotation.x += wheelRotSpeed;
  }
}

// Exportar funciones
if (typeof window !== 'undefined') {
  window.createVehicle = createVehicle;
  window.createCharacter = createCharacter;
  window.setupControls = setupControls;
  window.togglePause = togglePause;
  window.exitVehicle = exitVehicle;
  window.enterVehicle = enterVehicle;
  window.updateOnFoot = updateOnFoot;
  window.updateOnFootCamera = updateOnFootCamera;
  window.updateDriving = updateDriving;
}
