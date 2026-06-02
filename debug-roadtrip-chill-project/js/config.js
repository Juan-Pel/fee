/**
 * Roadtrip Chill - Configuración Global del Juego
 * Módulo que contiene el estado global y configuraciones principales
 */

var G = {
  mode: 'medium',
  players: 2,
  vehicleColor: '#4a90d9',
  running: false,
  photoMode: false,
  speed: 0,
  maxSpeed: 80,
  distance: 0,
  targetDistance: 150,
  fuel: 100,
  money: 500,
  sleepiness: 0,
  gameTime: 720,
  cameraMode: 0,
  weather: 'clear',
  weatherTimer: 0,
  driverIdx: 0,
  photosTaken: 0,
  eventsCompleted: 0,
  lastEventTime: 0,
  nextEventTime: 0,
  currentEventVisual: null,
  heading: 0,
  steerAngle: 0,
  vehicle: null,
  vehicleBody: null,
  cabinBottom: 0,
  wheels: [],
  vw: 2.2,
  vh: 0.8,
  vl: 4.5,
  cw: 1.8,
  ch: 0.9,
  cl: 2.4,
  scene: null,
  camera: null,
  renderer: null,
  clock: null,
  ground: null,
  decorPool: [],
  rainParticles: null,
  starField: null,
  skyMesh: null,
  dirLight: null,
  sunMesh: null,
  moonMesh: null,
  motels: [],
  nearestMotelIdx: -1,
  atMotel: false,
  motelCooldown: 0,
  activeMotelIdx: -1,
  collisionCooldown: 0,
  cameraShake: 0,
  gasStations: [],
  pushingCar: false,
  otherCars: [],
  onFoot: false,
  character: null,
  charHeading: 0,
  charBobTime: 0,
  interiorGroup: null,
  keys: {},
  radioActive: false,
  ytPlayer: null,
  ytReady: false,
  ytApiLoaded: false,
  paused: false
};

// Colores disponibles para personalización
var COLORS = [
  '#4a90d9', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
  '#1abc9c', '#e67e22', '#3498db', '#e91e63', '#00bcd4'
];

// Eventos visuales con sus efectos
var VISUAL_EVENTS = [
  { type: 'deer', msg: '🦌 ¡Ciervo cruzando!', impact: { sleep: 3 }, result: 'Frenaste para el ciervo', dur: 8 },
  { type: 'bird', msg: '🦅 ¡Mirá arriba!', impact: { sleep: -2 }, result: '¡Qué vista!', dur: 6 },
  { type: 'rainbow', msg: '🌈 ¡Arcoíris!', impact: { sleep: -5 }, result: 'Arcoíris a la vista', dur: 10 },
  { type: 'stalled', msg: '🚗 Auto averiado', impact: { sleep: 3 }, result: 'Esquivaste el auto', dur: 12 },
  { type: 'scenic', msg: '🏔️ Vista panorámica', impact: { sleep: -8 }, result: 'Qué hermoso paisaje...', dur: 15 }
];

// Helper: aplicar posición sin romper referencias internas de Three.js
function setPos(obj, x, y, z) {
  obj.position.set(x, y, z);
  return obj;
}

// Helper: oscurecer un color hex
function darkenColor(hex, factor) {
  var r = parseInt(hex.slice(1, 3), 16);
  var g = parseInt(hex.slice(3, 5), 16);
  var b = parseInt(hex.slice(5, 7), 16);
  r = Math.floor(r * factor);
  g = Math.floor(g * factor);
  b = Math.floor(b * factor);
  return '#' + [r, g, b].map(function(v) {
    return v.toString(16).padStart(2, '0');
  }).join('');
}

// Curva de la ruta
function getRoadCurve(z) {
  return Math.sin(z * 0.003) * 30 + Math.sin(z * 0.007) * 15 + Math.sin(z * 0.001) * 10;
}

// Exportar para uso en otros módulos
if (typeof window !== 'undefined') {
  window.G = G;
  window.COLORS = COLORS;
  window.VISUAL_EVENTS = VISUAL_EVENTS;
  window.setPos = setPos;
  window.darkenColor = darkenColor;
  window.getRoadCurve = getRoadCurve;
}
