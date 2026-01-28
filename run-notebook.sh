#!/bin/bash
# Quick launcher for CARF Jupyter Notebook in Docker

echo "🐳 Starting CARF Framework Jupyter Notebook in Docker..."
echo ""

# Build the Docker image
echo "Building Docker image..."
docker build -f Dockerfile.jupyter -t carf-jupyter .

echo ""
echo "Starting Jupyter server..."
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd):/workspace \
  --name carf-notebook \
  carf-jupyter

echo ""
echo "✅ Jupyter notebook is now running!"
echo "📓 Open in browser: http://localhost:8888"
echo ""
echo "To stop: Press Ctrl+C or run 'docker stop carf-notebook'"
