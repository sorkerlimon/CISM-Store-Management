#!/bin/bash

echo "🚀 Installing html2image dependencies for Ubuntu server..."

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install Chrome/Chromium
echo "🌐 Installing Chromium browser..."
sudo apt-get install -y chromium-browser

# Install virtual display server (for headless operation)
echo "📺 Installing virtual display server..."
sudo apt-get install -y xvfb

# Install font packages (improves rendering)
echo "🔤 Installing fonts..."
sudo apt-get install -y fonts-liberation fonts-dejavu-core fonts-noto

# Install additional dependencies
echo "📚 Installing additional dependencies..."
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

# Set environment variables
echo "🔧 Setting environment variables..."
export CHROME_BIN=/usr/bin/chromium-browser
export DISPLAY=:99

# Start virtual display
echo "📺 Starting virtual display..."
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Test Chrome installation
echo "🧪 Testing Chrome installation..."
if command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium installed: $(chromium-browser --version)"
else
    echo "❌ Chromium installation failed"
    exit 1
fi

# Test html2image
echo "🧪 Testing html2image..."
python3 -c "
try:
    from html2image import Html2Image
    print('✅ html2image imported successfully')
    hti = Html2Image()
    print('✅ Html2Image instance created successfully')
except Exception as e:
    print(f'❌ html2image test failed: {e}')
"

echo "🎉 Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add these environment variables to your Django app:"
echo "   export CHROME_BIN=/usr/bin/chromium-browser"
echo "   export DISPLAY=:99"
echo ""
echo "2. Restart your Django application"
echo "3. Test invoice generation" 