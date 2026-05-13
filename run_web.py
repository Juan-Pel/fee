#!/usr/bin/env python3
"""
Launcher para Stock Market Tycoon - Interfaz Web
Ejecuta el servidor Flask con la interfaz gráfica del juego
"""
import sys
import os

# Añadir el directorio web al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web'))

from web.app import app, socketio

if __name__ == '__main__':
    print("=" * 60)
    print("📈 STOCK MARKET TYCOON - Interfaz Web")
    print("=" * 60)
    print("\nIniciando servidor...")
    print("\nAbre tu navegador en: http://localhost:8080")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    
    try:
        socketio.run(app, debug=False, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\nServidor detenido.")
        sys.exit(0)
