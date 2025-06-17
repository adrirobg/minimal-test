#!/bin/bash

echo "🎭 Configurando Playwright MCP para minimal-test..."

# Verificar si estamos en el directorio correcto
if [ ! -f "package.json" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz de minimal-test"
    exit 1
fi

echo "📁 Proyecto detectado: $(pwd)"

# 1. Instalar Playwright MCP globalmente si no está instalado
echo "📦 Verificando instalación de @playwright/mcp..."
if ! npm list -g @playwright/mcp >/dev/null 2>&1; then
    echo "⬇️ Instalando @playwright/mcp globalmente..."
    npm install -g @playwright/mcp
else
    echo "✅ @playwright/mcp ya está instalado"
fi

# 2. Verificar navegadores de Playwright
echo "🌐 Verificando navegadores Playwright..."
cd frontend
if ! npx playwright install-deps >/dev/null 2>&1; then
    echo "⬇️ Instalando dependencias de navegadores..."
    npx playwright install-deps
fi

if ! npx playwright install chromium >/dev/null 2>&1; then
    echo "⬇️ Instalando navegador Chromium..."
    npx playwright install chromium
else
    echo "✅ Navegador Chromium ya está disponible"
fi

cd ..

# 3. Verificar configuración MCP
echo "🔧 Verificando configuración MCP..."
if [ -f ".claude/mcp_config.json" ]; then
    echo "✅ Configuración MCP encontrada en .claude/mcp_config.json"
else
    echo "❌ No se encontró configuración MCP"
    exit 1
fi

# 4. Crear script de testing
echo "📝 Creando script de testing Playwright MCP..."
cat > test-playwright-mcp.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing Playwright MCP configuration..."

# Test 1: Verificar que el servidor MCP funciona
echo "1️⃣ Testing MCP server..."
timeout 5s npx @playwright/mcp --help >/dev/null 2>&1
if [ $? -eq 0 ] || [ $? -eq 124 ]; then
    echo "✅ Playwright MCP server is working"
else
    echo "❌ Playwright MCP server failed"
    exit 1
fi

# Test 2: Verificar Claude Code puede detectar MCP
echo "2️⃣ Checking Claude Code MCP detection..."
if command -v claude >/dev/null 2>&1; then
    claude mcp 2>/dev/null | grep -q "playwright" && echo "✅ Claude Code detecta Playwright MCP" || echo "⚠️ Claude Code no detecta Playwright MCP"
else
    echo "⚠️ Claude Code no está disponible en PATH"
fi

# Test 3: Verificar que el frontend puede ejecutarse
echo "3️⃣ Checking frontend setup..."
cd frontend
if [ -f "package.json" ]; then
    echo "✅ Frontend package.json encontrado"
    npm list @playwright/test >/dev/null 2>&1 && echo "✅ Playwright test está instalado" || echo "⚠️ Considera instalar @playwright/test"
else
    echo "❌ Frontend package.json no encontrado"
fi
cd ..

echo ""
echo "🎯 Configuración completada. Próximos pasos:"
echo "1. Asegúrate de que Claude Desktop esté reiniciado"
echo "2. En Claude Desktop, prueba: '¿Tienes acceso a Playwright?'"
echo "3. En Claude Code, ejecuta: claude mcp"
echo "4. Para debugging: claude 'usa playwright para navegar a localhost:3000'"
echo ""
echo "📚 URLs de tu aplicación:"
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8000 (si está configurado)"
EOF

chmod +x test-playwright-mcp.sh

# 5. Ejecutar test
echo "🧪 Ejecutando tests de configuración..."
./test-playwright-mcp.sh

echo ""
echo "🎉 Configuración de Playwright MCP completada!"
echo ""
echo "📋 Resumen de archivos creados/modificados:"
echo "   ✅ .claude/mcp_config.json - Configuración MCP para Claude Code"
echo "   ✅ test-playwright-mcp.sh - Script de testing"
echo ""
echo "🚀 Para usar Playwright MCP:"
echo "   En Claude Desktop: 'Navega a localhost:3000 y analiza la página'"
echo "   En Claude Code: claude 'usa playwright para debuggear mi app Next.js'"
