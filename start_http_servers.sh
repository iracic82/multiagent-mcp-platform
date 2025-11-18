#!/bin/bash
# Startup script for HTTP MCP servers (spec-compliant migration)
# This script runs all HTTP versions in parallel for testing the migration

echo "🚀 Starting HTTP MCP Servers (Spec-Compliant Migration)"
echo "=========================================================="
echo ""
echo "This runs all HTTP servers in parallel on ports 4001-4004"
echo "SSE backup servers should be running on ports 3001-3004"
echo ""

# Activate virtual environment
source venv/bin/activate

# Kill any existing HTTP servers on these ports
echo "🧹 Cleaning up existing HTTP servers..."
lsof -ti:4001 | xargs kill -9 2>/dev/null || true
lsof -ti:4002 | xargs kill -9 2>/dev/null || true
lsof -ti:4003 | xargs kill -9 2>/dev/null || true
lsof -ti:4004 | xargs kill -9 2>/dev/null || true

echo ""
echo "📍 Starting HTTP MCP Servers..."
echo ""

# Start all HTTP servers in background
python mcp_infoblox_http.py > logs/infoblox_http.log 2>&1 &
INFOBLOX_PID=$!
echo "✅ Infoblox DDI HTTP Server (port 4001) - PID: $INFOBLOX_PID"

python mcp_server_http.py > logs/subnet_http.log 2>&1 &
SUBNET_PID=$!
echo "✅ Subnet Calculator HTTP Server (port 4002) - PID: $SUBNET_PID"

python mcp_aws_http.py > logs/aws_http.log 2>&1 &
AWS_PID=$!
echo "✅ AWS Tools HTTP Server (port 4003) - PID: $AWS_PID"

python mcp_aws_cloudcontrol_http.py > logs/cloudcontrol_http.log 2>&1 &
CLOUDCONTROL_PID=$!
echo "✅ AWS CloudControl HTTP Server (port 4004) - PID: $CLOUDCONTROL_PID"

echo ""
echo "⏳ Waiting 3 seconds for servers to start..."
sleep 3

echo ""
echo "🔍 Checking server health..."
echo ""

# Check each HTTP endpoint
check_endpoint() {
    local url=$1
    local name=$2

    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ $name is responding"
    else
        echo "❌ $name is NOT responding"
    fi
}

check_endpoint "http://127.0.0.1:4001/mcp" "Infoblox DDI (4001)"
check_endpoint "http://127.0.0.1:4002/mcp" "Subnet Calculator (4002)"
check_endpoint "http://127.0.0.1:4003/mcp" "AWS Tools (4003)"
check_endpoint "http://127.0.0.1:4004/mcp" "AWS CloudControl (4004)"

echo ""
echo "=========================================================="
echo "✅ All HTTP MCP servers started!"
echo ""
echo "Server PIDs:"
echo "  - Infoblox DDI:       $INFOBLOX_PID"
echo "  - Subnet Calculator:  $SUBNET_PID"
echo "  - AWS Tools:          $AWS_PID"
echo "  - AWS CloudControl:   $CLOUDCONTROL_PID"
echo ""
echo "Logs location: logs/*_http.log"
echo ""
echo "To stop all HTTP servers:"
echo "  kill $INFOBLOX_PID $SUBNET_PID $AWS_PID $CLOUDCONTROL_PID"
echo ""
echo "Migration status:"
echo "  🆕 HTTP servers (spec-compliant): Ports 4001-4004"
echo "  🔄 SSE servers (backup):          Ports 3001-3004"
echo ""
echo "Press Ctrl+C to stop monitoring. Servers will continue running."
echo "=========================================================="

# Keep script running and monitor servers
trap "echo ''; echo '⚠️  Stopping all HTTP servers...'; kill $INFOBLOX_PID $SUBNET_PID $AWS_PID $CLOUDCONTROL_PID 2>/dev/null; echo '✅ All HTTP servers stopped'; exit 0" INT TERM

# Monitor in background
while true; do
    sleep 30
    # Check if all processes are still running
    if ! ps -p $INFOBLOX_PID > /dev/null 2>&1; then
        echo "⚠️  WARNING: Infoblox HTTP server (PID $INFOBLOX_PID) has stopped!"
    fi
    if ! ps -p $SUBNET_PID > /dev/null 2>&1; then
        echo "⚠️  WARNING: Subnet Calculator HTTP server (PID $SUBNET_PID) has stopped!"
    fi
    if ! ps -p $AWS_PID > /dev/null 2>&1; then
        echo "⚠️  WARNING: AWS Tools HTTP server (PID $AWS_PID) has stopped!"
    fi
    if ! ps -p $CLOUDCONTROL_PID > /dev/null 2>&1; then
        echo "⚠️  WARNING: AWS CloudControl HTTP server (PID $CLOUDCONTROL_PID) has stopped!"
    fi
done
