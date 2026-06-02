/**
 * Roadtrip Chill - Sistema de Mundo y Generación Procedural
 * Maneja la creación del terreno, decoración, motels y estaciones de servicio
 */

// Crear árbol low-poly
function makeTree() {
  var g = new THREE.Group();
  var t = new THREE.Mesh(
    new THREE.CylinderGeometry(0.2, 0.4, 3, 6),
    new THREE.MeshLambertMaterial({ color: 0x6B4226 })
  );
  setPos(t, 0, 1.5, 0);
  t.castShadow = true;
  g.add(t);

  var leaves = new THREE.Mesh(
    new THREE.ConeGeometry(1.5, 3, 8),
    new THREE.MeshLambertMaterial({ color: 0x2d5a27 })
  );
  setPos(leaves, 0, 4, 0);
  leaves.castShadow = true;
  g.add(leaves);

  return g;
}

// Crear arbusto
function makeBush() {
  var b = new THREE.Mesh(
    new THREE.DodecahedronGeometry(1, 0),
    new THREE.MeshLambertMaterial({ color: 0x3d7a37 })
  );
  b.scale.set(1, 0.6, 1);
  b.castShadow = true;
  b.position.y = 0.3;
  return b;
}

// Crear roca
function makeRock() {
  var r = new THREE.Mesh(
    new THREE.DodecahedronGeometry(0.5, 0),
    new THREE.MeshLambertMaterial({ color: 0x888888 })
  );
  r.scale.set(1 + Math.random(), 0.5 + Math.random() * 0.5, 1 + Math.random());
  r.position.y = 0.25;
  r.castShadow = true;
  return r;
}

// Crear flores
function makeFlowers() {
  var f = new THREE.Group();
  var colors = [0xff6b6b, 0xfeca57, 0xff9ff3, 0x54a0ff];

  for (var i = 0; i < 5; i++) {
    var stem = new THREE.Mesh(
      new THREE.CylinderGeometry(0.02, 0.02, 0.4, 6),
      new THREE.MeshLambertMaterial({ color: 0x2d5a27 })
    );
    stem.position.y = 0.2;
    f.add(stem);

    var petal = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 8, 8),
      new THREE.MeshLambertMaterial({ color: colors[Math.floor(Math.random() * colors.length)] })
    );
    petal.position.y = 0.4;
    petal.position.x = (Math.random() - 0.5) * 0.3;
    petal.position.z = (Math.random() - 0.5) * 0.3;
    f.add(petal);
  }

  return f;
}

// Generar chunk de decoración
function generateChunk(startZ) {
  var chunkLength = 100;
  var decorations = [];

  for (var z = startZ; z < startZ + chunkLength; z += 5 + Math.random() * 10) {
    var side = Math.random() > 0.5 ? 1 : -1;
    var dist = 15 + Math.random() * 50;
    var x = getRoadCurve(z) + side * dist;

    var rand = Math.random();
    var decor;

    if (rand < 0.4) {
      decor = makeTree();
    } else if (rand < 0.6) {
      decor = makeBush();
    } else if (rand < 0.8) {
      decor = makeRock();
    } else {
      decor = makeFlowers();
    }

    decor.position.set(x, 0, z);
    G.scene.add(decor);
    decorations.push(decor);
  }

  G.decorPool = G.decorPool.concat(decorations);
  return decorations;
}

// Inicializar Three.js
function initThree() {
  // Remover canvas existente
  var existingCanvas = document.querySelector('canvas');
  if (existingCanvas) existingCanvas.remove();

  G.scene = new THREE.Scene();
  G.scene.background = new THREE.Color(0x87CEEB);
  G.scene.fog = new THREE.Fog(0x87CEEB, 100, 400);

  G.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 3000);
  G.camera.position.set(0, 6, 16);

  G.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  G.renderer.setSize(window.innerWidth, window.innerHeight);
  G.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  G.renderer.shadowMap.enabled = true;
  G.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  G.renderer.setClearColor(0x87CEEB);
  G.renderer.domElement.style.cssText = 'position:fixed!important;top:0!important;left:0!important;width:100vw!important;height:100vh!important;z-index:0!important;display:block!important';
  document.body.appendChild(G.renderer.domElement);

  G.clock = new THREE.Clock();

  window.addEventListener('resize', function() {
    G.camera.aspect = window.innerWidth / window.innerHeight;
    G.camera.updateProjectionMatrix();
    G.renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

// Construir el mundo
function buildWorld() {
  // Cielo
  var skyGeo = new THREE.SphereGeometry(1200, 16, 16);
  var skyMat = new THREE.MeshBasicMaterial({ color: 0x87CEEB, side: THREE.BackSide });
  G.skyMesh = new THREE.Mesh(skyGeo, skyMat);
  G.scene.add(G.skyMesh);

  // Sol
  G.sunMesh = new THREE.Mesh(
    new THREE.SphereGeometry(25, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0xffdd44 })
  );
  G.sunMesh.position.set(300, 200, -400);
  G.scene.add(G.sunMesh);

  // Luna
  G.moonMesh = new THREE.Mesh(
    new THREE.SphereGeometry(15, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0xeeeeff })
  );
  G.moonMesh.position.set(-300, 200, -400);
  G.scene.add(G.moonMesh);

  // Estrellas
  var sg = new THREE.BufferGeometry();
  var sp = [];
  for (var i = 0; i < 3000; i++) {
    var theta = Math.random() * Math.PI * 2,
      phi = Math.random() * Math.PI,
      r = 1100;
    sp.push(r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
  }
  sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
  G.starField = new THREE.Points(
    sg,
    new THREE.PointsMaterial({ color: 0xffffff, size: 2, transparent: true, opacity: 0 })
  );
  G.scene.add(G.starField);

  // Suelo
  G.ground = new THREE.Mesh(
    new THREE.PlaneGeometry(8000, 8000),
    new THREE.MeshLambertMaterial({ color: 0x4a8c3f, side: THREE.DoubleSide })
  );
  G.ground.rotation.x = -Math.PI / 2;
  G.ground.position.y = -0.55;
  G.ground.receiveShadow = true;
  G.scene.add(G.ground);

  // Luz ambiental
  G.scene.add(new THREE.AmbientLight(0xffffff, 0.7));

  // Luz direccional (sol)
  G.dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
  G.dirLight.position.set(100, 150, 100);
  G.dirLight.castShadow = true;
  G.dirLight.shadow.mapSize.set(2048, 2048);
  var sc = G.dirLight.shadow.camera;
  sc.near = 1;
  sc.far = 600;
  sc.left = -100;
  sc.right = 100;
  sc.top = 100;
  sc.bottom = -100;
  G.scene.add(G.dirLight);

  // Partículas de lluvia
  var rg = new THREE.BufferGeometry();
  var rp = [];
  for (var j = 0; j < 15000; j++)
    rp.push((Math.random() - 0.5) * 400, Math.random() * 120, (Math.random() - 0.5) * 400);
  rg.setAttribute('position', new THREE.Float32BufferAttribute(rp, 3));
  G.rainParticles = new THREE.Points(
    rg,
    new THREE.PointsMaterial({ color: 0xaabbcc, size: 0.3, transparent: true, opacity: 0 })
  );
  G.scene.add(G.rainParticles);

  // Generar decoración inicial
  generateChunk(-100);
  generateChunk(0);
  generateChunk(100);
}

// Colocar moteles en la ruta
function placeMotels() {
  G.motels = [];
  var motelInterval = 80;
  var totalMotels = Math.ceil(G.targetDistance / motelInterval) + 2;

  for (var i = 0; i < totalMotels; i++) {
    var z = i * motelInterval + 50;
    var x = getRoadCurve(z) + 25;

    var motel = new THREE.Group();

    // Edificio principal
    var building = new THREE.Mesh(
      new THREE.BoxGeometry(20, 6, 10),
      new THREE.MeshLambertMaterial({ color: 0xd4a574 })
    );
    building.position.set(0, 3, 0);
    building.castShadow = true;
    motel.add(building);

    // Techo
    var roof = new THREE.Mesh(
      new THREE.ConeGeometry(15, 4, 4),
      new THREE.MeshLambertMaterial({ color: 0x8b4513 })
    );
    roof.rotation.y = Math.PI / 4;
    roof.position.set(0, 8, 0);
    motel.add(roof);

    // Letrero "MOTEL"
    var signGeo = new THREE.BoxGeometry(8, 2, 0.5);
    var signMat = new THREE.MeshLambertMaterial({ color: 0xffff00 });
    var sign = new THREE.Mesh(signGeo, signMat);
    sign.position.set(0, 10, 0);
    motel.add(sign);

    // Poste del letrero
    var pole = new THREE.Mesh(
      new THREE.CylinderGeometry(0.3, 0.3, 12, 8),
      new THREE.MeshLambertMaterial({ color: 0x666666 })
    );
    pole.position.set(0, 6, 0);
    motel.add(pole);

    motel.position.set(x, 0, z);
    G.scene.add(motel);

    G.motels.push({
      mesh: motel,
      z: z,
      x: x,
      active: false,
      glow: null
    });
  }
}

// Colocar estaciones de servicio
function placeGasStations() {
  G.gasStations = [];
  var gasInterval = 120;
  var totalGas = Math.ceil(G.targetDistance / gasInterval) + 1;

  for (var i = 0; i < totalGas; i++) {
    var z = i * gasInterval + 80;
    var x = getRoadCurve(z) - 30;

    var station = new THREE.Group();

    // Techo de la estación
    var roof = new THREE.Mesh(
      new THREE.BoxGeometry(15, 1, 10),
      new THREE.MeshLambertMaterial({ color: 0xe74c3c })
    );
    roof.position.set(0, 5, 0);
    station.add(roof);

    // Columnas
    for (var c = -2; c <= 2; c += 2) {
      var col = new THREE.Mesh(
        new THREE.CylinderGeometry(0.3, 0.3, 5, 8),
        new THREE.MeshLambertMaterial({ color: 0xcccccc })
      );
      col.position.set(c * 4, 2.5, 3);
      station.add(col);
    }

    // Surtidores
    for (var p = -1; p <= 1; p += 2) {
      var pump = new THREE.Mesh(
        new THREE.BoxGeometry(1.5, 3, 1.5),
        new THREE.MeshLambertMaterial({ color: 0x3498db })
      );
      pump.position.set(p * 3, 1.5, 2);
      station.add(pump);
    }

    station.position.set(x, 0, z);
    G.scene.add(station);

    G.gasStations.push({
      mesh: station,
      z: z,
      x: x,
      active: false
    });
  }
}

// Exportar funciones
if (typeof window !== 'undefined') {
  window.initThree = initThree;
  window.buildWorld = buildWorld;
  window.generateChunk = generateChunk;
  window.placeMotels = placeMotels;
  window.placeGasStations = placeGasStations;
  window.makeTree = makeTree;
  window.makeBush = makeBush;
  window.makeRock = makeRock;
  window.makeFlowers = makeFlowers;
}
