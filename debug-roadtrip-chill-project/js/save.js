// Sistema de Guardado para Roadtrip Chill
// Guarda progreso, estadísticas y configuración del jugador

const SAVE = {
    slotName: 'roadtrip_save_v1',
    
    // Datos por defecto
    defaultData: {
        totalDistance: 0,
        totalTrips: 0,
        totalTimePlayed: 0,
        bestStreak: 0, // Mayor tiempo sin dormir
        moneyEarned: 0,
        photosTaken: 0,
        eventsCompleted: 0,
        unlockedColors: ['white'],
        unlockedVehicles: ['car'],
        settings: {
            musicVolume: 0.5,
            sfxVolume: 0.5,
            sensitivity: 1.0,
            showHints: true
        },
        lastPosition: null,
        lastTrip: null
    },

    // Cargar datos guardados
    load() {
        try {
            const saved = localStorage.getItem(this.slotName);
            if (saved) {
                const parsed = JSON.parse(saved);
                return { ...this.defaultData, ...parsed };
            }
        } catch (e) {
            console.warn('Error cargando partida:', e);
        }
        return { ...this.defaultData };
    },

    // Guardar datos
    save(data) {
        try {
            const toSave = { ...this.defaultData, ...data };
            localStorage.setItem(this.slotName, JSON.stringify(toSave));
            console.log('Partida guardada exitosamente');
            return true;
        } catch (e) {
            console.error('Error guardando partida:', e);
            return false;
        }
    },

    // Auto-guardado periódico (cada 2 minutos)
    autoSaveInterval: null,
    startAutoSave(callback) {
        this.stopAutoSave();
        this.autoSaveInterval = setInterval(() => {
            if (callback) callback();
        }, 120000); // 2 minutos
    },

    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    },

    // Guardar progreso actual del juego
    saveGameProgress(gameState) {
        const current = this.load();
        const progress = {
            totalDistance: current.totalDistance + (gameState.distanceTraveled || 0),
            totalTrips: current.totalTrips + 1,
            totalTimePlayed: current.totalTimePlayed + (gameState.playTime || 0),
            moneyEarned: current.moneyEarned + (gameState.moneySpent || 0),
            photosTaken: current.photosTaken + (gameState.photosTaken || 0),
            eventsCompleted: current.eventsCompleted + (gameState.eventsCompleted || 0),
            lastPosition: gameState.position ? {
                x: gameState.position.x,
                z: gameState.position.z
            } : null,
            lastTrip: new Date().toISOString(),
            settings: current.settings
        };
        
        // Mantener desbloqueos
        progress.unlockedColors = current.unlockedColors;
        progress.unlockedVehicles = current.unlockedVehicles;
        
        return this.save(progress);
    },

    // Desbloquear nuevo color/vehículo
    unlockItem(type, item) {
        const current = this.load();
        const key = type === 'color' ? 'unlockedColors' : 'unlockedVehicles';
        
        if (!current[key].includes(item)) {
            current[key].push(item);
            this.save(current);
            return true;
        }
        return false;
    },

    // Resetear progreso (útil para testing)
    reset() {
        localStorage.removeItem(this.slotName);
        console.log('Progreso reseteado');
        return { ...this.defaultData };
    },

    // Exportar partida a archivo
    exportSave() {
        const data = this.load();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `roadtrip_save_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    // Importar partida desde archivo
    importSave(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    this.save(data);
                    resolve(data);
                } catch (err) {
                    reject('Archivo inválido');
                }
            };
            reader.onerror = () => reject('Error leyendo archivo');
            reader.readAsText(file);
        });
    }
};

// Hacer disponible globalmente
if (typeof window !== 'undefined') {
    window.SAVE = SAVE;
}
