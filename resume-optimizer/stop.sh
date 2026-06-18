#!/bin/bash
set -e

echo "🛑 Stopping Resume Optimizer..."

docker-compose down

echo "✅ All services stopped"
echo ""
echo "💡 To remove all data (database, uploads, exports):"
echo "   docker-compose down -v"
