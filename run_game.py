#!/usr/bin/env python3
"""
Launcher para Stock Market Tycoon - Interfaz Gráfica
Usa pywebview para crear una ventana nativa con HTML/JS frontend
y Python backend con toda la lógica del juego.
"""

import sys
import os

# Asegurar que el directorio actual esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from web_interface import run_web_app
        print("=" * 60)
        print("📈 STOCK MARKET TYCOON - Edición Interactiva")
        print("=" * 60)
        print("\nIniciando interfaz gráfica...")
        print("Si la ventana no aparece automáticamente, revisa la consola.\n")
        
        run_web_app()
        
    except ImportError as e:
        print(f"Error: No se pudo importar pywebview.")
        print(f"Instala con: pip install pywebview")
        print(f"Detalle: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al iniciar: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
