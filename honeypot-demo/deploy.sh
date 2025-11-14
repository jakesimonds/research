#!/bin/bash
# Quick deployment script for EC2

set -e

echo "🍯 Honeypot Deployment Script"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing..."

    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    fi

    if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ]; then
        # Amazon Linux / RHEL
        sudo yum update -y
        sudo yum install docker -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Ubuntu / Debian
        sudo apt update
        sudo apt install docker.io -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    else
        echo "❌ Unsupported OS. Please install Docker manually."
        exit 1
    fi

    echo "✅ Docker installed. Please log out and back in, then re-run this script."
    exit 0
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "🏗️  Building and starting honeypot..."
docker-compose up -d --build

echo ""
echo "✅ Honeypot is running!"
echo ""
echo "📊 View logs in real-time:"
echo "   docker-compose logs -f"
echo ""
echo "📈 Analyze results after some time:"
echo "   python3 analyze_logs.py"
echo ""
echo "🛑 Stop the honeypot:"
echo "   docker-compose down"
echo ""
echo "🌐 Your server is now exposed on port 80"
echo "   Test it: curl http://localhost/"
echo ""
echo "⏰ Recommended: Run for 30-60 minutes, then analyze results"
echo ""
