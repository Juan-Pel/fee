/**
 * Roadtrip Chill - Sistema Multijugador P2P
 * Maneja la conexión PeerJS, sincronización de estado y jugadores remotos
 */

var MP = {
  enabled: false,
  isHost: false,
  peer: null,
  roomCode: '',
  hostConnection: null,
  clientConnections: [],
  remotePlayers: {},
  remoteCars: {},
  remoteCharacters: {},
  hostCarMesh: null,
  myName: 'Jugador',
  myId: '',
  syncTimer: 0,
  connected: false,
  inHostCar: false
};

// Generar código de sala aleatorio
function generateRoomCode() {
  var chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  var code = '';
  for (var i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

// Obtener nombre del jugador
function getPlayerName() {
  var name = document.getElementById('playerName').value.trim();
  return name || 'Jugador';
}

// Mostrar notificación en UI
function showNotification(msg) {
  if (typeof notify === 'function') {
    notify(msg);
  } else {
    console.log('[MP Notification]', msg);
  }
}

// Crear sala (host)
function createRoom() {
  if (!MP.peer) {
    try {
      MP.peer = new Peer(null, {
        debug: 2
      });
    } catch (e) {
      showNotification('❌ Error al inicializar PeerJS');
      return;
    }
  }

  MP.peer.on('open', function(id) {
    MP.myId = id;
    MP.roomCode = generateRoomCode();
    MP.isHost = true;
    MP.enabled = true;

    document.getElementById('roomCodeDisplay').textContent = MP.roomCode;
    document.getElementById('roomInfo').style.display = 'block';
    document.getElementById('joinRoomSection').style.display = 'none';
    document.getElementById('connectionStatus').textContent = '🟢 Esperando jugadores...';

    updatePlayersList();
  });

  MP.peer.on('connection', function(conn) {
    if (MP.clientConnections.length >= 7) {
      conn.close();
      return;
    }

    conn.on('open', function() {
      MP.clientConnections.push(conn);

      conn.on('data', function(data) {
        handleClientData(conn, data);
      });

      conn.on('close', function() {
        var idx = MP.clientConnections.indexOf(conn);
        if (idx > -1) MP.clientConnections.splice(idx, 1);
        updatePlayersList();
      });

      updatePlayersList();
    });
  });

  MP.peer.on('error', function(err) {
    showNotification('❌ Error de conexión: ' + err.type);
  });
}

// Unirse a sala (cliente)
function joinRoom() {
  var code = document.getElementById('roomCodeInput').value.trim().toUpperCase();
  if (!code) {
    showNotification('❌ Ingresá un código de sala');
    return;
  }

  if (!MP.peer) {
    try {
      MP.peer = new Peer(null, {
        debug: 2
      });
    } catch (e) {
      showNotification('❌ Error al inicializar PeerJS');
      return;
    }
  }

  document.getElementById('connectionStatus').textContent = '🟡 Conectando...';

  MP.peer.on('open', function(id) {
    MP.myId = id;
    MP.isHost = false;
    MP.enabled = true;

    var conn = MP.peer.connect(code, {
      metadata: {
        name: getPlayerName()
      }
    });

    conn.on('open', function() {
      MP.hostConnection = conn;
      MP.connected = true;

      document.getElementById('roomInfo').style.display = 'block';
      document.getElementById('joinRoomSection').style.display = 'none';
      document.getElementById('connectionStatus').textContent = '🟢 Conectado a la sala';

      conn.on('data', function(data) {
        handleHostData(conn, data);
      });

      conn.on('close', function() {
        MP.connected = false;
        showNotification('❌ Desconectado del host');
      });
    });

    conn.on('error', function(err) {
      showNotification('❌ Error al conectar: ' + err.type);
    });
  });

  MP.peer.on('error', function(err) {
    showNotification('❌ Error de PeerJS: ' + err.type);
  });
}

// Manejar datos recibidos como host
function handleHostData(conn, data) {
  if (!data || !data.type) return;

  switch (data.type) {
    case 'join':
      MP.remotePlayers[conn.peer] = {
        name: data.name || 'Jugador',
        id: conn.peer
      };
      updatePlayersList();
      broadcastToClients({
        type: 'playerJoined',
        playerId: conn.peer,
        name: data.name
      });
      break;

    case 'update':
      if (MP.remoteCars[conn.peer]) {
        MP.remoteCars[conn.peer].position.set(data.x, data.y, data.z);
        MP.remoteCars[conn.peer].rotation.y = data.rotation;
      }
      break;

    case 'chat':
      showNotification('💬 ' + (data.name || 'Jugador') + ': ' + data.message);
      break;
  }
}

// Manejar datos recibidos como cliente
function handleClientData(data) {
  if (!data || !data.type) return;

  switch (data.type) {
    case 'gameState':
      G.distance = data.distance;
      G.fuel = data.fuel;
      G.sleepiness = data.sleepiness;
      G.gameTime = data.gameTime;
      G.weather = data.weather;
      break;

    case 'playerJoined':
      MP.remotePlayers[data.playerId] = {
        name: data.name,
        id: data.playerId
      };
      updatePlayersList();
      break;

    case 'playerLeft':
      delete MP.remotePlayers[data.playerId];
      updatePlayersList();
      break;

    case 'startGame':
      startMultiplayerGame();
      break;
  }
}

// Broadcast a todos los clientes
function broadcastToClients(data) {
  for (var i = 0; i < MP.clientConnections.length; i++) {
    var conn = MP.clientConnections[i];
    if (conn.open) {
      conn.send(data);
    }
  }
}

// Actualizar lista de jugadores en UI
function updatePlayersList() {
  var list = document.getElementById('playersList');
  if (!list) return;

  var html = '<strong style="color:#f0e68c">🎮 ' + getPlayerName() + ' (Host)</strong><br>';

  for (var id in MP.remotePlayers) {
    var p = MP.remotePlayers[id];
    html += '👤 ' + p.name + '<br>';
  }

  var total = 1 + Object.keys(MP.remotePlayers).length;
  html += '<br><span style="color:#8888aa">' + total + '/8 jugadores</span>';

  list.innerHTML = html;
}

// Actualización multijugador en el loop principal
function updateMultiplayer(dt) {
  if (!MP.enabled || !G.running) return;

  MP.syncTimer += dt;

  if (MP.isHost) {
    // Host envía estado del juego cada 100ms
    if (MP.syncTimer >= 0.1) {
      MP.syncTimer = 0;
      broadcastToClients({
        type: 'gameState',
        distance: G.distance,
        fuel: G.fuel,
        sleepiness: G.sleepiness,
        gameTime: G.gameTime,
        weather: G.weather
      });
    }
  } else {
    // Cliente envía su input/posición al host
    if (MP.syncTimer >= 0.05 && MP.hostConnection && MP.hostConnection.open) {
      MP.syncTimer = 0;

      if (G.onFoot && G.character) {
        MP.hostConnection.send({
          type: 'update',
          x: G.character.position.x,
          y: G.character.position.y,
          z: G.character.position.z,
          rotation: G.charHeading,
          onFoot: true
        });
      } else if (G.vehicle) {
        MP.hostConnection.send({
          type: 'update',
          x: G.vehicle.position.x,
          y: G.vehicle.position.y,
          z: G.vehicle.position.z,
          rotation: G.heading,
          onFoot: false
        });
      }
    }
  }
}

// Crear personaje remoto
function createRemoteCharacter(name) {
  var group = new THREE.Group();

  var bodyMat = new THREE.MeshLambertMaterial({
    color: 0x3498db
  });
  var bodyGeo = new THREE.CapsuleGeometry(0.3, 0.7, 4, 8);
  var body = new THREE.Mesh(bodyGeo, bodyMat);
  body.position.y = 0.65;
  group.add(body);

  var headGeo = new THREE.SphereGeometry(0.25, 8, 8);
  var head = new THREE.Mesh(headGeo, bodyMat);
  head.position.y = 1.4;
  group.add(head);

  group.userData = {
    name: name,
    bobTime: Math.random() * Math.PI * 2
  };

  return group;
}

// Crear auto remoto
function createRemoteCar(color, name) {
  var group = new THREE.Group();

  var carColor = new THREE.Color(color || '#4a90d9');
  var darkColor = darkenColor(color || '#4a90d9', 0.7);

  // Cuerpo principal
  var bodyGeo = new THREE.BoxGeometry(2.2, 0.8, 4.5);
  var bodyMat = new THREE.MeshLambertMaterial({
    color: carColor
  });
  var body = new THREE.Mesh(bodyGeo, bodyMat);
  body.position.y = 0.7;
  body.castShadow = true;
  group.add(body);

  // Cabina
  var cabinGeo = new THREE.BoxGeometry(1.8, 0.6, 2.4);
  var cabinMat = new THREE.MeshLambertMaterial({
    color: 0x333333
  });
  var cabin = new THREE.Mesh(cabinGeo, cabinMat);
  cabin.position.set(0, 1.3, -0.2);
  group.add(cabin);

  // Ruedas
  var wheelGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.2, 12);
  var wheelMat = new THREE.MeshLambertMaterial({
    color: 0x222222
  });

  var positions = [
    [-1.2, 0.35, 1.5],
    [1.2, 0.35, 1.5],
    [-1.2, 0.35, -1.5],
    [1.2, 0.35, -1.5]
  ];

  for (var i = 0; i < 4; i++) {
    var wheel = new THREE.Mesh(wheelGeo, wheelMat);
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(positions[i][0], positions[i][1], positions[i][2]);
    group.add(wheel);
  }

  group.userData = {
    name: name,
    color: color
  };

  return group;
}

// Exportar para uso en otros módulos
if (typeof window !== 'undefined') {
  window.MP = MP;
  window.generateRoomCode = generateRoomCode;
  window.getPlayerName = getPlayerName;
  window.createRoom = createRoom;
  window.joinRoom = joinRoom;
  window.handleHostData = handleHostData;
  window.handleClientData = handleClientData;
  window.broadcastToClients = broadcastToClients;
  window.updatePlayersList = updatePlayersList;
  window.updateMultiplayer = updateMultiplayer;
  window.createRemoteCharacter = createRemoteCharacter;
  window.createRemoteCar = createRemoteCar;
}
