#!/bin/bash

# Setup Script para Sistema de Logging Híbrido
# Kairos BCP - PKM System Rewrite Experiment

set -e  # Exit on any error

echo "🚀 Iniciando setup del sistema de logging híbrido para Kairos BCP..."

# Colors para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para print con colores
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}📋${NC} $1"
}

# Verificar que estamos en la raíz del proyecto
if [ ! -f "mission_map.json" ]; then
    print_error "mission_map.json no encontrado. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

print_status "mission_map.json encontrado"

# Crear estructura de directorios
print_info "Creando estructura de directorios..."

mkdir -p logs
mkdir -p scripts
mkdir -p docs

print_status "Directorios creados: logs/, scripts/, docs/"

# Crear el script generador de TODO (necesitamos crearlo como archivo físico)
print_info "Creando script generador de TODO..."

cat > scripts/generate_todo.py << 'EOF'
#!/usr/bin/env python3
"""
Generador de TODO.md desde mission_map.json
Parte del sistema de logging híbrido para Kairos BCP
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_logs_directory():
    """Crear directorio de logs si no existe"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    return logs_dir

def load_mission_map():
    """Cargar mission_map.json"""
    try:
        with open('mission_map.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: mission_map.json no encontrado")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {e}")
        return None

def get_status_icon(task_id):
    """Determinar ícono de status basado en task_id"""
    # Lógica simple: si el task es 0.1, está done; resto pending
    if task_id == "0.1_install_context7":
        return "✅"
    else:
        return "⏳"

def generate_todo_content(mission_data):
    """Generar contenido completo del TODO.md"""
    
    # Header
    content = f"""# Kairos BCP - Development TODO

**Generated from**: `mission_map.json`  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Methodology**: Roo Code + Context7 + Mission Map  

## Legend
- ⏳ Pending
- 🚧 In Progress  
- ✅ Completed
- ❌ Failed/Blocked

## Progress Overview

"""
    
    # Progress overview
    total_tasks = 0
    completed_tasks = 0
    
    for phase in mission_data['phases']:
        phase_tasks = len(phase['tasks'])
        total_tasks += phase_tasks
        
        phase_completed = sum(1 for task in phase['tasks'] if get_status_icon(task['task_id']) == "✅")
        completed_tasks += phase_completed
        
        progress_percent = int((phase_completed / phase_tasks) * 100) if phase_tasks > 0 else 0
        progress_bar = "█" * (progress_percent // 10) + "░" * (10 - progress_percent // 10)
        
        content += f"**{phase['phase_id']}**: {progress_bar} {progress_percent}% ({phase_completed}/{phase_tasks})\\n"
    
    overall_progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    overall_bar = "█" * (overall_progress // 10) + "░" * (10 - overall_progress // 10)
    content += f"\\n**OVERALL**: {overall_bar} {overall_progress}% ({completed_tasks}/{total_tasks})\\n\\n"
    
    # Detailed phases and tasks
    for phase in mission_data['phases']:
        content += f"## {phase['phase_id']}: {phase['description']}\\n\\n"
        
        for task in phase['tasks']:
            status = get_status_icon(task['task_id'])
            content += f"### [{status}] {task['task_id']}\\n"
            content += f"**Description**: {task['description']}\\n\\n"
            
            # Dependencies
            if task['dependencies']:
                content += f"**Dependencies**: {', '.join(task['dependencies'])}\\n"
            else:
                content += f"**Dependencies**: None\\n"
            
            # Context7 libraries
            if task.get('context7_libraries'):
                libs = ', '.join(f"`{lib}`" for lib in task['context7_libraries'])
                content += f"**Context7 Libraries**: {libs}\\n"
            
            # Artifacts
            if task.get('artifacts_output'):
                artifacts = ', '.join(f"`{artifact}`" for artifact in task['artifacts_output'])
                content += f"**Expected Artifacts**: {artifacts}\\n"
            
            # Validation criteria
            content += f"**Validation**: {task['validation_criteria']}\\n"
            
            # Human checkpoint
            if task.get('human_checkpoint', False):
                content += f"**Human Checkpoint**: ⚠️ Required\\n"
            
            # Logging section for Claude Code
            content += f"\\n**Logging Notes** (for Claude Code):\\n"
            content += f"- [ ] Context7 documentation fetched\\n"
            content += f"- [ ] Artifacts created and validated\\n"
            content += f"- [ ] Validation criteria met\\n"
            content += f"- [ ] Progress logged to `logs/progress_log.md`\\n\\n"
            
            content += "---\\n\\n"
    
    # Footer with instructions
    content += f"""## Instructions for Claude Code

### Before starting any task:
1. Read this TODO.md to understand current status
2. Check `logs/progress_log.md` for previous context
3. Verify Context7 is working: include "use context7" in prompts

### During task execution:
1. Log progress in `logs/progress_log.md`
2. Update this file's status markers (⏳ → 🚧 → ✅)
3. Use Context7 for up-to-date documentation of specified libraries
4. Create artifacts as specified in each task

### After task completion:
1. Validate against criteria listed
2. Update progress overview percentages
3. Log any issues or learnings in progress_log.md

### Emergency Reset:
If experiment fails, use: `git checkout experiment-base` to restart

---
*Generated by: `scripts/generate_todo.py`*
*Mission Map: `mission_map.json`*
"""
    
    return content

def generate_initial_progress_log():
    """Generar progress_log.md inicial"""
    content = f"""# Development Progress Log

**Project**: Kairos BCP - PKM System Rewrite  
**Started**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Methodology**: Roo Code + Context7 + Mission Map  

## Session Log

### {datetime.now().strftime('%Y-%m-%d %H:%M')} - Project Initialization
- ✅ Mission map created (`mission_map.json`)
- ✅ Logging system implemented
- ✅ TODO.md generated from mission map
- ⏳ Ready for Phase 1.1 (backend_setup)

**Context7 Status**: Installed, ready to use with "use context7" directive

**Next Steps**: 
1. Create experimental branch
2. Begin Phase 1.1 backend setup
3. Test Context7 integration with FastAPI documentation

---

## Claude Code Instructions

When logging progress, use this format:

```
### YYYY-MM-DD HH:MM - Task: [task_id]
**Status**: [Started/In Progress/Completed/Blocked]
**Context7 Used**: [Libraries fetched]
**Artifacts Created**: [List files]
**Issues Encountered**: [Any problems]
**Validation Status**: [Pass/Fail/Pending]
```

Remember to:
- Log before starting each task
- Update TODO.md status markers
- Record Context7 usage and effectiveness
- Note any deviations from mission map

---
"""
    return content

def main():
    """Función principal"""
    print("🚀 Iniciando setup del sistema de logging híbrido...")
    
    # Crear directorio de logs
    logs_dir = create_logs_directory()
    print(f"📁 Directorio de logs creado: {logs_dir}")
    
    # Cargar mission map
    mission_data = load_mission_map()
    if not mission_data:
        return
    
    # Generar TODO.md
    todo_content = generate_todo_content(mission_data)
    todo_path = logs_dir / "todo.md"
    
    with open(todo_path, 'w', encoding='utf-8') as f:
        f.write(todo_content)
    print(f"📝 TODO.md generado: {todo_path}")
    
    # Generar progress_log.md inicial
    progress_content = generate_initial_progress_log()
    progress_path = logs_dir / "progress_log.md"
    
    with open(progress_path, 'w', encoding='utf-8') as f:
        f.write(progress_content)
    print(f"📊 Progress log creado: {progress_path}")
    
    # Crear archivos adicionales de tracking
    context7_path = logs_dir / "context7_usage.md"
    with open(context7_path, 'w', encoding='utf-8') as f:
        f.write(f"# Context7 Usage Tracking\\n\\n**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
    print(f"🔍 Context7 tracker creado: {context7_path}")
    
    artifacts_path = logs_dir / "artifacts_created.md"
    with open(artifacts_path, 'w', encoding='utf-8') as f:
        f.write(f"# Artifacts Created Log\\n\\n**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
    print(f"📦 Artifacts tracker creado: {artifacts_path}")
    
    print("\\n✅ Sistema de logging híbrido configurado correctamente!")
    print("\\n📋 Archivos creados:")
    print(f"   - {todo_path}")
    print(f"   - {progress_path}")
    print(f"   - {context7_path}")
    print(f"   - {artifacts_path}")
    
    print("\\n🎯 Siguiente paso: Ejecutar este script en la raíz del proyecto")

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/generate_todo.py
print_status "Script generador creado: scripts/generate_todo.py"

# Crear CURRENT_STATE.md
print_info "Creando CURRENT_STATE.md..."

cat > CURRENT_STATE.md << EOF
# Kairos BCP - Current Project State

## 🎯 Project Overview
**Name**: Kairos BCP - Personal Knowledge Management System  
**Status**: Pre-Phase 1 (Experiment Setup)  
**Objective**: Test development methodology (Roo Code + Context7 + Mission Map)  
**Priority**: Process validation > Functional app  

## 📍 Current Position
- **Phase**: Phase 0 ✅ Completed (Context7 setup)
- **Next Task**: Phase 1.1 - Backend Setup
- **Branch Strategy**: experiment-base → experiment-rewrite-v1
- **Development Mode**: Experimental/Testing methodology

## 🗂️ Key Files & Locations

### Core Configuration
- **Mission Map**: \`mission_map.json\` (root directory)
- **Current State**: \`CURRENT_STATE.md\` (this file)
- **Original Context**: Documents folder with initial planning

### Logging System (Hybrid)
- **TODO Tracker**: \`logs/todo.md\` (generated from mission_map.json)
- **Progress Log**: \`logs/progress_log.md\` (Claude Code writes here)
- **Context7 Usage**: \`logs/context7_usage.md\`
- **Artifacts Tracking**: \`logs/artifacts_created.md\`

### Setup Scripts
- **TODO Generator**: \`scripts/generate_todo.py\`

## 🔧 Technology Stack
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS
- **Development**: Python + Node.js
- **Documentation**: Context7 MCP Server
- **Methodology**: Roo Code mission map execution

## 🧪 Experimental Setup

### Context7 Status
- **Installation**: ✅ Completed (Claude Code + Claude Desktop)
- **Usage**: Include "use context7" in prompts for up-to-date docs
- **Testing**: Verify with FastAPI/Next.js documentation requests

### Branch Strategy
\`\`\`bash
main                    # Original project
experiment-base         # Clean state for experiments  
experiment-rewrite-v1   # Current experimental branch
\`\`\`

### Logging Protocol
1. **Before each task**: Read \`logs/todo.md\` for status
2. **During execution**: Log to \`logs/progress_log.md\`
3. **After completion**: Update TODO status markers
4. **Context7 tracking**: Log library documentation fetched

## 📋 Mission Map Structure

### Phase 1: Backend Foundation (Current Target)
- **1.1 backend_setup** ⏳ - FastAPI + environment setup
- **1.2 database_setup** ⏳ - SQLAlchemy + PostgreSQL + Alembic  
- **1.3 pydantic_schemas** ⏳ - Validation schemas

### Phase 2: Backend Implementation  
- **2.1 jwt_auth** ⏳ - Authentication system
- **2.2 crud_endpoints** ⏳ - API endpoints
- **2.3 api_testing** ⏳ - Test suite

### Phase 3: Frontend Implementation
- **3.1 frontend_setup** ⏳ - Next.js + TypeScript setup
- **3.2 auth_system** ⏳ - Frontend auth integration
- **3.3 dashboard_pkm** ⏳ - PKM interface
- **3.4 responsive_ui** ⏳ - UI/UX optimization

### Phase 4: Integration & Deployment
- **4.1 integration_testing** ⏳ - E2E testing
- **4.2 dockerization** ⏳ - Container setup
- **4.3 documentation** ⏳ - Complete docs

## 🤖 Instructions for Claude Code

### Startup Protocol
1. **Read this file** to understand current context
2. **Check \`logs/todo.md\`** for detailed task breakdown
3. **Review \`logs/progress_log.md\`** for previous session context
4. **Verify Context7**: Test with "use context7" in a prompt

### Task Execution Flow
1. **Start logging**: Write to \`logs/progress_log.md\`
2. **Read mission map**: Get task details from \`mission_map.json\`
3. **Use Context7**: Include "use context7" for each specified library
4. **Create artifacts**: Follow \`artifacts_output\` specifications
5. **Validate**: Check against \`validation_criteria\`
6. **Update TODO**: Change status markers (⏳ → 🚧 → ✅)

### Context7 Integration
Each task specifies \`context7_libraries\` - use these for up-to-date documentation:
- **Task 1.1**: \`["fastapi", "uvicorn", "python-dotenv", "pydantic-settings"]\`
- **Task 1.2**: \`["sqlalchemy", "asyncpg", "alembic", "psycopg2-binary"]\`
- **Task 1.3**: \`["pydantic", "pydantic-settings"]\`

### Logging Format
\`\`\`markdown
### YYYY-MM-DD HH:MM - Task: [task_id]
**Status**: [Started/In Progress/Completed/Blocked]
**Context7 Used**: [Libraries fetched documentation for]
**Artifacts Created**: [List of files/directories created]
**Issues Encountered**: [Any problems or blockers]
**Validation Status**: [Pass/Fail/Pending]
**Notes**: [Additional observations]
\`\`\`

### Emergency Procedures
- **Reset experiment**: \`git checkout experiment-base\`
- **Check mission map**: \`cat mission_map.json | jq '.phases[0].tasks[0]'\`
- **Regenerate TODO**: \`python scripts/generate_todo.py\`

## 🎯 Success Criteria (Experimental)

### Primary Goals
- [ ] Context7 integration works seamlessly
- [ ] Mission map execution is smooth
- [ ] Logging system provides useful debugging info
- [ ] Process is repeatable and improvable

### Secondary Goals  
- [ ] Backend foundation is functional
- [ ] FastAPI + SQLAlchemy setup works
- [ ] Frontend can connect to backend
- [ ] Docker containerization is successful

### Learning Objectives
- Validate Roo Code methodology effectiveness
- Test Context7 real-world usage patterns
- Identify friction points in mission map execution
- Document process improvements for future iterations

## 🚀 Ready to Execute

**Current Status**: ✅ All systems configured  
**Next Action**: Execute Phase 1.1 (backend_setup)  
**Command for Claude Code**: Start with reading \`logs/todo.md\` and begin Phase 1.1

---

**Last Updated**: $(date +"%Y-%m-%d %H:%M:%S")  
**Generated by**: Claude Projects planning session  
**For**: Claude Code execution context  
EOF

print_status "CURRENT_STATE.md creado"

# Ejecutar el generador de TODO
print_info "Generando archivos de logging..."

if command -v python3 &> /dev/null; then
    python3 scripts/generate_todo.py
elif command -v python &> /dev/null; then
    python scripts/generate_todo.py
else
    print_error "Python no encontrado. Instala Python 3.x para continuar."
    exit 1
fi

# Crear README para el sistema de logging
print_info "Creando documentación del sistema..."

cat > docs/LOGGING_SYSTEM.md << EOF
# Sistema de Logging Híbrido - Kairos BCP

## Descripción
Sistema de tracking y logging para el desarrollo experimental de Kairos BCP usando metodología Roo Code + Context7 + Mission Map.

## Estructura de Archivos

### Archivos Core
- **mission_map.json**: Configuración principal con todas las tareas
- **CURRENT_STATE.md**: Estado actual del proyecto para Claude Code
- **scripts/generate_todo.py**: Generador automático de TODO.md

### Archivos de Logging (logs/)
- **todo.md**: TODO generado automáticamente desde mission_map.json
- **progress_log.md**: Log de progreso que Claude Code actualiza
- **context7_usage.md**: Tracking de uso de Context7
- **artifacts_created.md**: Lista de archivos/componentes creados

## Flujo de Trabajo

### Para Claude Code
1. Leer CURRENT_STATE.md para contexto
2. Revisar logs/todo.md para tareas pendientes
3. Ejecutar tarea con Context7
4. Logear progreso en logs/progress_log.md
5. Actualizar status en logs/todo.md

### Para Desarrollador (Humano)
1. Ejecutar setup: ./scripts/setup_logging.sh
2. Crear rama experimental: git checkout -b experiment-rewrite-v1
3. Iniciar Claude Code con contexto
4. Revisar logs para debugging
5. Reset si es necesario: git checkout experiment-base

## Regeneración de TODO
\`\`\`bash
python scripts/generate_todo.py
\`\`\`

## Estructura de Logs
Los logs siguen formato markdown estructurado para fácil lectura y parsing.

## Emergency Reset
\`\`\`bash
git checkout experiment-base
rm -rf logs/
./scripts/setup_logging.sh
\`\`\`
EOF

print_status "Documentación creada: docs/LOGGING_SYSTEM.md"

# Crear script de reset experimental
cat > scripts/reset_experiment.sh << 'EOF'
#!/bin/bash

echo "🔄 Reseteando experimento..."

# Cambiar a rama base
git checkout experiment-base

# Limpiar logs
rm -rf logs/

# Regenerar sistema de logging
python scripts/generate_todo.py

# Crear nueva rama experimental
EXPERIMENT_NUM=$(git branch -a | grep -c "experiment-rewrite-" || echo "0")
NEW_BRANCH="experiment-rewrite-v$((EXPERIMENT_NUM + 1))"

git checkout -b $NEW_BRANCH

echo "✅ Experimento reseteado. Nueva rama: $NEW_BRANCH"
echo "📋 Listo para comenzar con Phase 1.1"
EOF

chmod +x scripts/reset_experiment.sh
print_status "Script de reset creado: scripts/reset_experiment.sh"

# Git setup para ramas experimentales
print_info "Configurando ramas experimentales..."

# Verificar si estamos en un repo git
if [ ! -d ".git" ]; then
    print_warning "No es un repositorio git. Inicializando..."
    git init
    git add .
    git commit -m "Initial commit with logging system"
fi

# Crear rama experiment-base si no existe
if ! git show-ref --verify --quiet refs/heads/experiment-base; then
    print_info "Creando rama experiment-base..."
    git checkout -b experiment-base
    git add .
    git commit -m "Setup logging system for experimental development"
    print_status "Rama experiment-base creada"
else
    print_status "Rama experiment-base ya existe"
fi

# Crear primera rama experimental
if ! git show-ref --verify --quiet refs/heads/experiment-rewrite-v1; then
    print_info "Creando rama experiment-rewrite-v1..."
    git checkout -b experiment-rewrite-v1
    print_status "Rama experiment-rewrite-v1 creada y activa"
else
    print_status "Rama experiment-rewrite-v1 ya existe"
    git checkout experiment-rewrite-v1
fi

# Resumen final
echo ""
echo "🎉 Setup completo del sistema de logging híbrido!"
echo ""
print_status "Estructura creada:"
echo "   📁 logs/ - Sistema de tracking"
echo "   📁 scripts/ - Herramientas de automatización" 
echo "   📁 docs/ - Documentación del sistema"
echo "   📄 CURRENT_STATE.md - Contexto para Claude Code"
echo ""
print_status "Ramas configuradas:"
echo "   🌿 experiment-base (estado limpio)"
echo "   🚧 experiment-rewrite-v1 (rama activa)"
echo ""
print_info "Siguiente paso:"
echo "   1. Verificar Context7: include 'use context7' en prompts"
echo "   2. Iniciar Claude Code con contexto de CURRENT_STATE.md"
echo "   3. Comenzar con Phase 1.1 (backend_setup)"
echo ""
print_warning "Para reset de emergencia: ./scripts/reset_experiment.sh"