# VS Code + WSL Integration Setup for Kairos BCP

Complete guide for setting up VS Code with Remote-WSL for optimal Kairos BCP development.

## Prerequisites

- VS Code installed in Windows
- WSL 2 with Ubuntu 22.04 LTS
- Kairos BCP project cloned in WSL (`~/projects/kairos-bcp/`)

## Initial Setup

### 1. Install Remote-WSL Extension

```bash
# Method 1: Install from VS Code
# 1. Open VS Code in Windows
# 2. Install "Remote - WSL" extension (ms-vscode-remote.remote-wsl)

# Method 2: Install via command line
code --install-extension ms-vscode-remote.remote-wsl
```

### 2. Open Project in WSL

```bash
# From WSL terminal, navigate to your project
cd ~/projects/kairos-bcp

# Open VS Code in WSL mode
code .

# Alternative: Open from Windows
# 1. Open VS Code
# 2. Ctrl+Shift+P → "Remote-WSL: Open Folder in WSL"
# 3. Navigate to ~/projects/kairos-bcp
```

## Workspace Configuration

### 1. Automatic Extension Installation

When you first open the project, VS Code will prompt to install recommended extensions. Click "Install All" to get:

- **Python Development**: Python, Black Formatter, MyPy
- **Frontend Development**: ESLint, Prettier, Tailwind CSS
- **Docker Support**: Docker extension
- **Productivity**: Path IntelliSense, Auto Rename Tag
- **Database**: PostgreSQL extension

### 2. Python Environment Setup

```bash
# Ensure Poetry virtual environment is created
cd backend
poetry install
poetry shell

# VS Code should automatically detect the virtual environment
# If not, use Ctrl+Shift+P → "Python: Select Interpreter"
# Select: ./backend/.venv/bin/python
```

### 3. Node.js Environment

```bash
# Install frontend dependencies
cd frontend
npm install

# VS Code should automatically use the project's Node.js version
# TypeScript IntelliSense will work automatically
```

## Debugging Configuration

### 1. Python Debugging

The workspace includes pre-configured debug configurations:

- **Python: FastAPI Backend** - Debug the backend server
- **Python: Debug Tests** - Debug pytest tests
- **Python: Debug Current File** - Debug the currently open Python file

```bash
# To debug the backend:
# 1. Set breakpoints in your code
# 2. Press F5 or go to Run and Debug
# 3. Select "Python: FastAPI Backend"
# 4. Server will start with debugger attached
```

### 2. Frontend Debugging

```bash
# For Next.js debugging:
# 1. Start the dev server with: npm run dev
# 2. Use "Node.js: Next.js Frontend" configuration
# 3. Or attach to running process with "Node.js: Debug Frontend"
```

### 3. Full Stack Debugging

Use the compound configuration "Full Stack: Backend + Frontend" to debug both simultaneously.

## Terminal Integration

### 1. Integrated Terminal

VS Code's integrated terminal will automatically open in WSL:

```bash
# All terminals will be WSL by default
# You can create specific terminal types:
# Ctrl+Shift+` → New Terminal
# Select bash, zsh, or other shells
```

### 2. Multiple Terminal Setup

```bash
# Recommended terminal layout:
# Terminal 1: Backend (cd backend && poetry shell)
# Terminal 2: Frontend (cd frontend && npm run dev)
# Terminal 3: Docker (docker-compose logs -f)
# Terminal 4: General purpose
```

## File Operations

### 1. File Explorer

- Files are directly accessible in the VS Code explorer
- All operations (create, delete, rename) work seamlessly
- Drag and drop works between Explorer and editor

### 2. Search and Replace

```bash
# Use VS Code's powerful search:
# Ctrl+Shift+F for global search
# Ctrl+H for find and replace
# Search works across the entire WSL file system
```

## Git Integration

### 1. Source Control

```bash
# Git integration works seamlessly:
# 1. Source Control tab shows all changes
# 2. Commit and push directly from VS Code
# 3. GitLens extension provides enhanced Git features
```

### 2. Git Configuration

```bash
# Ensure Git is configured in WSL
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Use VS Code as default Git editor
git config --global core.editor "code --wait"
```

## Performance Optimization

### 1. File Watching

VS Code automatically handles file watching in WSL. If you experience issues:

```bash
# Increase file watch limits (already in WSL_PERFORMANCE_TIPS.md)
echo 'fs.inotify.max_user_watches=1048576' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. Extension Management

```bash
# Extensions are installed in WSL context
# They run with better performance than Windows extensions
# No need to install extensions twice
```

## Development Workflow

### 1. Daily Startup

```bash
# 1. Open WSL terminal or VS Code terminal
cd ~/projects/kairos-bcp

# 2. Start development services
./scripts/dev-setup.sh

# 3. Open VS Code if not already open
code .

# 4. Start debugging or open integrated terminals as needed
```

### 2. Code Quality Workflow

```bash
# Backend quality checks (automatic on save):
# - Black formatting
# - MyPy type checking
# - ESLint/Prettier for frontend

# Manual quality checks:
# Ctrl+Shift+P → "Python: Run Linting"
# Ctrl+Shift+P → "ESLint: Fix all auto-fixable Problems"
```

### 3. Testing Workflow

```bash
# Python tests:
# 1. Use "Python: Debug Tests" configuration
# 2. Or run in terminal: poetry run pytest
# 3. Test Explorer shows all tests

# Frontend tests:
# 1. Run: npm test
# 2. Use Jest extension for debugging
```

## Database Integration

### 1. PostgreSQL Extension

```bash
# Connect to your database:
# 1. Install PostgreSQL extension
# 2. Add connection: localhost:5432
# 3. Username: postgres, Password: postgres
# 4. Database: kairos_bcp
```

### 2. Database Queries

```bash
# Create .sql files and run queries directly
# Right-click in .sql file → "Run Query"
# Results appear in VS Code output panel
```

## Docker Integration

### 1. Docker Extension

```bash
# Docker extension provides:
# 1. Container management in sidebar
# 2. Dockerfile IntelliSense
# 3. Docker Compose support
# 4. Image and container inspection
```

### 2. Remote Containers (Optional)

```bash
# For even more isolation:
# 1. Create .devcontainer configuration
# 2. Use "Remote-Containers: Reopen in Container"
# 3. Entire development environment runs in container
```

## Troubleshooting

### 1. Common Issues

```bash
# Issue: VS Code can't find Python interpreter
# Solution: Ctrl+Shift+P → "Python: Select Interpreter"
# Select: ./backend/.venv/bin/python

# Issue: Extensions not working
# Solution: Ensure you're in WSL mode (bottom left shows "WSL: Ubuntu")

# Issue: Slow file operations
# Solution: Ensure project is in WSL file system, not /mnt/c/

# Issue: Port forwarding not working  
# Solution: Check Windows firewall, use localhost not 127.0.0.1
```

### 2. Reset Configuration

```bash
# If configuration gets corrupted:
# 1. Close VS Code
# 2. Delete .vscode/settings.json
# 3. Restart VS Code in WSL
# 4. Reconfigure from scratch
```

## Advanced Features

### 1. Snippets and IntelliSense

```bash
# Python IntelliSense works with:
# - FastAPI decorators and dependencies
# - SQLAlchemy models and queries
# - Pydantic schemas and validation

# TypeScript IntelliSense works with:
# - Next.js API routes and components
# - Tailwind CSS classes
# - React hooks and components
```

### 2. Multi-root Workspaces

```bash
# For complex projects:
# File → Add Folder to Workspace
# Save as .code-workspace file
# Manage backend and frontend as separate roots
```

This setup provides the optimal VS Code development experience for Kairos BCP in WSL, with full debugging, IntelliSense, and productivity features.