#!/bin/bash

# RAIA Docker Runner - Mac/Linux
# Easy script to run RAIA in Docker

set -e

echo "======================================"
echo "RAIA Docker Runner"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build       - Build the Docker image"
    echo "  test        - Run all tests"
    echo "  examples    - Run example scripts"
    echo "  shell       - Open interactive shell"
    echo "  clean       - Clean up Docker resources"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh build      # Build the image"
    echo "  ./run.sh test       # Run tests"
    echo "  ./run.sh examples   # Run examples"
    echo "  ./run.sh shell      # Interactive shell"
    echo ""
}

# Parse command
COMMAND=${1:-help}

case $COMMAND in
    build)
        echo "🏗️  Building Docker image..."
        docker-compose build raia-tests
        echo ""
        echo "✅ Build complete!"
        ;;

    test)
        echo "🧪 Running tests..."
        docker-compose up raia-tests
        echo ""
        echo "✅ Tests complete!"
        ;;

    examples)
        echo "📚 Running examples..."
        docker-compose up raia-examples
        echo ""
        echo "✅ Examples complete!"
        ;;

    shell)
        echo "🐚 Starting interactive shell..."
        echo "   Type 'exit' to leave the shell"
        echo ""
        docker-compose run --rm raia-shell bash
        ;;

    clean)
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        echo ""
        echo "✅ Cleanup complete!"
        ;;

    help|--help|-h)
        show_usage
        ;;

    *)
        echo "❌ Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac
