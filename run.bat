@echo off
REM RAIA Docker Runner - Windows
REM Easy script to run RAIA in Docker

echo ======================================
echo RAIA Docker Runner
echo ======================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo X Docker is not running. Please start Docker Desktop and try again.
    exit /b 1
)

echo √ Docker is running
echo.

REM Parse command
if "%1"=="" goto help
if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="examples" goto examples
if "%1"=="shell" goto shell
if "%1"=="clean" goto clean
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help

echo X Unknown command: %1
echo.
goto help

:build
    echo Building Docker image...
    docker-compose build raia-tests
    echo.
    echo √ Build complete!
    goto end

:test
    echo Running tests...
    docker-compose up raia-tests
    echo.
    echo √ Tests complete!
    goto end

:examples
    echo Running examples...
    docker-compose up raia-examples
    echo.
    echo √ Examples complete!
    goto end

:shell
    echo Starting interactive shell...
    echo    Type 'exit' to leave the shell
    echo.
    docker-compose run --rm raia-shell bash
    goto end

:clean
    echo Cleaning up Docker resources...
    docker-compose down -v
    docker system prune -f
    echo.
    echo √ Cleanup complete!
    goto end

:help
    echo Usage: run.bat [command]
    echo.
    echo Commands:
    echo   build       - Build the Docker image
    echo   test        - Run all tests
    echo   examples    - Run example scripts
    echo   shell       - Open interactive shell
    echo   clean       - Clean up Docker resources
    echo   help        - Show this help message
    echo.
    echo Examples:
    echo   run.bat build      # Build the image
    echo   run.bat test       # Run tests
    echo   run.bat examples   # Run examples
    echo   run.bat shell      # Interactive shell
    echo.
    goto end

:end
