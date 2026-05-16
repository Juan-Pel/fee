#!/bin/bash

# Script de compilación para Stock Market Tycoon

echo "🚀 Compilando Stock Market Tycoon..."

# Crear directorio de compilación
mkdir -p build
cd build

# Configurar con CMake
echo "📦 Configurando con CMake..."
cmake ..

if [ $? -ne 0 ]; then
    echo "❌ Error en la configuración de CMake"
    exit 1
fi

# Compilar
echo "🔨 Compilando..."
make -j$(nproc)

if [ $? -ne 0 ]; then
    echo "❌ Error en la compilación"
    exit 1
fi

echo "✅ ¡Compilación completada!"
echo ""
echo "Para ejecutar el juego:"
echo "  ./stock_market_tycoon"
echo ""
echo "O desde el directorio raíz:"
echo "  ./build/stock_market_tycoon"
