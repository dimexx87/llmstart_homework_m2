# PowerShell Build Script for LLM Assistant Telegram Bot

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:"
    Write-Host "  help        - Show this help message"
    Write-Host "  install     - Install dependencies"
    Write-Host "  run         - Run bot locally"
    Write-Host "  build       - Build Docker image"
    Write-Host "  up          - Start with docker-compose"
    Write-Host "  down        - Stop docker-compose"
    Write-Host "  test        - Run tests"
    Write-Host "  lint        - Run linting"
    Write-Host "  clean       - Clean up containers"
}

function Install-Dependencies {
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
}

function Start-Bot {
    Write-Host "Starting bot locally..."
    python main.py
}

function Build-Image {
    Write-Host "Building Docker image..."
    docker build -t llm-telegram-bot .
}

function Start-Compose {
    Write-Host "Starting with docker-compose..."
    docker-compose up -d
}

function Stop-Compose {
    Write-Host "Stopping docker-compose..."
    docker-compose down
}

function Run-Tests {
    Write-Host "Running tests..."
    python -m pytest tests/ -v
}

function Run-Lint {
    Write-Host "Running linting..."
    python -m py_compile *.py modules/*.py
    Write-Host "Basic syntax check completed"
}

function Clean-Docker {
    Write-Host "Cleaning up Docker..."
    docker-compose down --volumes --remove-orphans
    docker rmi llm-telegram-bot -f
}

switch ($Command) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "run" { Start-Bot }
    "build" { Build-Image }
    "up" { Start-Compose }
    "down" { Stop-Compose }
    "test" { Run-Tests }
    "lint" { Run-Lint }
    "clean" { Clean-Docker }
    default { 
        Write-Host "Unknown command: $Command"
        Show-Help 
    }
}


