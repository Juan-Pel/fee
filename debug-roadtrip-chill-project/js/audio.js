// Sistema de Audio para Roadtrip Chill
// Maneja música, efectos de sonido y radio integrada

const AUDIO = {
    ctx: null,
    masterGain: null,
    musicVolume: 0.5,
    sfxVolume: 0.5,
    currentMusic: null,
    radioStation: null,
    isRadioPlaying: false,

    // Inicializar contexto de audio
    init() {
        try {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.ctx.createGain();
            this.masterGain.connect(this.ctx.destination);
            this.masterGain.gain.value = 1.0;
            console.log('Sistema de audio inicializado');
        } catch (e) {
            console.warn('Web Audio API no disponible:', e);
        }
    },

    // Configurar volúmenes
    setVolumes(musicVol, sfxVol) {
        this.musicVolume = Math.max(0, Math.min(1, musicVol));
        this.sfxVolume = Math.max(0, Math.min(1, sfxVol));
        
        if (this.currentMusic) {
            this.currentMusic.volume = this.musicVolume;
        }
    },

    // Efectos de sonido predefinidos
    sfx: {
        engine: null,
        horn: null,
        click: null,
        rain: null,
        wind: null
    },

    // Reproducir efecto de sonido
    playSFX(name, loop = false, volume = 1.0) {
        if (!this.ctx) this.init();
        if (!this.ctx) return null;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.ctx.currentTime;
        
        switch(name) {
            case 'engine':
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(80, now);
                osc.frequency.linearRampToValueAtTime(120, now + 0.5);
                gain.gain.setValueAtTime(0, now);
                gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.3, now + 0.5);
                break;
                
            case 'horn':
                osc.type = 'square';
                osc.frequency.setValueAtTime(400, now);
                osc.frequency.setValueAtTime(600, now + 0.1);
                gain.gain.setValueAtTime(0, now);
                gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.5, now + 0.05);
                gain.gain.linearRampToValueAtTime(0, now + 0.5);
                osc.stop(now + 0.5);
                break;
                
            case 'click':
                osc.type = 'sine';
                osc.frequency.setValueAtTime(800, now);
                gain.gain.setValueAtTime(this.sfxVolume * 0.3, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
                osc.stop(now + 0.1);
                break;
                
            case 'rain':
                // Ruido blanco para lluvia
                const bufferSize = this.ctx.sampleRate * 2;
                const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
                const data = buffer.getChannelData(0);
                for (let i = 0; i < bufferSize; i++) {
                    data[i] = Math.random() * 2 - 1;
                }
                
                const noise = this.ctx.createBufferSource();
                noise.buffer = buffer;
                noise.loop = true;
                
                const filter = this.ctx.createBiquadFilter();
                filter.type = 'lowpass';
                filter.frequency.value = 800;
                
                noise.connect(filter);
                filter.connect(gain);
                gain.connect(this.masterGain);
                
                gain.gain.setValueAtTime(this.sfxVolume * 0.2, now);
                noise.start(now);
                
                if (!loop) {
                    noise.stop(now + 5);
                }
                
                return { source: noise, gain: gain };
                
            case 'wind':
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(200, now);
                osc.frequency.linearRampToValueAtTime(300, now + 2);
                gain.gain.setValueAtTime(0, now);
                gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.15, now + 1);
                break;
                
            default:
                osc.type = 'sine';
                osc.frequency.setValueAtTime(440, now);
                gain.gain.setValueAtTime(this.sfxVolume * 0.3, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                osc.stop(now + 0.3);
        }
        
        if (name !== 'rain') {
            osc.start(now);
            if (!loop) {
                osc.stop(now + 2);
            }
        }
        
        return { source: osc, gain: gain };
    },

    // Detener efecto de sonido
    stopSFX(soundObj) {
        if (soundObj && soundObj.source) {
            const now = this.ctx.currentTime;
            soundObj.gain.gain.linearRampToValueAtTime(0, now + 0.1);
            soundObj.source.stop(now + 0.1);
        }
    },

    // Configurar radio con URL externa (YouTube, Spotify, etc.)
    setupRadio(url, type = 'youtube') {
        if (!this.currentMusic) {
            this.currentMusic = new Audio();
            this.currentMusic.loop = true;
        }

        let streamUrl = url;
        
        // Convertir URLs a streams cuando sea posible
        if (type === 'youtube') {
            // Nota: YouTube requiere API oficial o servicios de proxy
            console.log('Para YouTube, usar ID del video');
            const videoId = this.extractYouTubeID(url);
            if (videoId) {
                console.log(`Video ID: ${videoId}`);
                // Se necesitaría un backend para extraer audio
            }
        } else if (type === 'spotify') {
            console.log('Spotify requiere autenticación OAuth');
        } else if (type === 'direct' || type === 'mp3') {
            streamUrl = url;
        }

        this.currentMusic.src = streamUrl;
        this.currentMusic.volume = this.musicVolume;
        this.radioStation = url;
        
        return this.currentMusic;
    },

    // Extraer ID de YouTube
    extractYouTubeID(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    },

    // Controles de radio
    playRadio() {
        if (this.currentMusic) {
            this.currentMusic.play().then(() => {
                this.isRadioPlaying = true;
                console.log('Radio reproduciendo');
            }).catch(e => {
                console.warn('Error reproduciendo radio:', e);
            });
        }
    },

    pauseRadio() {
        if (this.currentMusic) {
            this.currentMusic.pause();
            this.isRadioPlaying = false;
        }
    },

    stopRadio() {
        this.pauseRadio();
        if (this.currentMusic) {
            this.currentMusic.src = '';
            this.radioStation = null;
        }
    },

    setRadioVolume(volume) {
        this.musicVolume = Math.max(0, Math.min(1, volume));
        if (this.currentMusic) {
            this.currentMusic.volume = this.musicVolume;
        }
    },

    // Música ambiental procedural (cuando no hay radio)
    playAmbientMusic(type = 'chill') {
        if (!this.ctx) this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        
        // Crear pad ambiental
        const createPad = (freq, type) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            const filter = this.ctx.createBiquadFilter();
            
            osc.type = type;
            osc.frequency.value = freq;
            
            filter.type = 'lowpass';
            filter.frequency.value = 2000;
            
            osc.connect(filter);
            filter.connect(gain);
            gain.connect(this.masterGain);
            
            gain.gain.setValueAtTime(0, now);
            gain.gain.linearRampToValueAtTime(this.musicVolume * 0.1, now + 2);
            
            osc.start(now);
            
            return { osc, gain, filter };
        };

        // Acordes chill progresivos
        const chords = {
            chill: [261.63, 329.63, 392.00], // C major
            sunset: [329.63, 415.30, 493.88], // E major
            night: [196.00, 246.94, 293.66]  // G minor
        };

        const selectedChord = chords[type] || chords.chill;
        const pads = selectedChord.map(freq => createPad(freq, 'sine'));

        // LFO para modulación suave
        const lfo = this.ctx.createOscillator();
        const lfoGain = this.ctx.createGain();
        lfo.frequency.value = 0.1;
        lfoGain.gain.value = 200;
        lfo.connect(lfoGain);
        
        pads.forEach(pad => {
            lfoGain.connect(pad.filter.frequency);
        });
        
        lfo.start(now);

        return { pads, lfo };
    },

    // Sonido de motor dinámico (basado en velocidad)
    updateEngineSound(speed) {
        if (!this.sfx.engine) {
            this.sfx.engine = this.playSFX('engine', true);
        }
        
        if (this.sfx.engine && this.sfx.engine.source) {
            const now = this.ctx.currentTime;
            const baseFreq = 80 + (Math.abs(speed) * 2);
            this.sfx.engine.source.frequency.linearRampToValueAtTime(
                Math.min(baseFreq, 300), 
                now + 0.1
            );
        }
    },

    // Limpiar todo el audio
    cleanup() {
        this.stopRadio();
        Object.values(this.sfx).forEach(sfx => {
            if (sfx) this.stopSFX(sfx);
        });
        
        if (this.ctx) {
            this.ctx.close();
            this.ctx = null;
        }
    }
};

// Hacer disponible globalmente
if (typeof window !== 'undefined') {
    window.AUDIO = AUDIO;
}
