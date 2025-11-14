#!/bin/bash

echo "Starting RAIA Enterprise API..."
echo "API Documentation: http://localhost:8000/api/docs"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
