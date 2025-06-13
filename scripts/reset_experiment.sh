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
