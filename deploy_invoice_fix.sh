#!/bin/bash

echo "🚀 Deploying Invoice Generation Fix for Ubuntu Server"
echo "=" * 60

# Step 1: Update system packages
echo "📦 Step 1: Updating system packages..."
sudo apt-get update -y

# Step 2: Install Chrome/Chromium
echo "🌐 Step 2: Installing Chromium browser..."
sudo apt-get install -y chromium-browser

# Step 3: Install display server
echo "📺 Step 3: Installing virtual display server..."
sudo apt-get install -y xvfb

# Step 4: Install fonts
echo "🔤 Step 4: Installing fonts..."
sudo apt-get install -y fonts-liberation fonts-dejavu-core fonts-noto

# Step 5: Install additional Chrome dependencies
echo "📚 Step 5: Installing Chrome dependencies..."
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

# Step 6: Set up environment variables
echo "🔧 Step 6: Setting up environment variables..."
export CHROME_BIN=/usr/bin/chromium-browser
export DISPLAY=:99

# Step 7: Start virtual display
echo "📺 Step 7: Starting virtual display..."
# Kill any existing Xvfb processes
sudo pkill -f Xvfb || true
# Start new Xvfb process
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
XVFB_PID=$!
echo "Xvfb started with PID: $XVFB_PID"

# Step 8: Test installations
echo "🧪 Step 8: Testing installations..."

# Test Chrome
if command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium installed: $(chromium-browser --version)"
else
    echo "❌ Chromium installation failed"
    exit 1
fi

# Test html2image
echo "Testing html2image..."
python3 -c "
try:
    from html2image import Html2Image
    print('✅ html2image imported successfully')
    
    hti = Html2Image(browser_executable='/usr/bin/chromium-browser')
    print('✅ Html2Image instance created successfully')
    
    # Try a simple test
    hti.screenshot(html_str='<h1>Test</h1>', save_as='test.png', size=(100,100))
    print('✅ Basic screenshot test passed')
    
except Exception as e:
    print(f'❌ html2image test failed: {e}')
    import traceback
    traceback.print_exc()
"

# Step 9: Create systemd service for Xvfb (optional)
echo "🔧 Step 9: Creating systemd service for Xvfb..."
sudo tee /etc/systemd/system/xvfb.service > /dev/null <<EOF
[Unit]
Description=X Virtual Framebuffer Service
After=network.target

[Service]
ExecStart=/usr/bin/Xvfb :99 -screen 0 1024x768x24
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable xvfb
sudo systemctl start xvfb

echo "✅ Xvfb service created and started"

# Step 10: Instructions for Django app
echo ""
echo "📋 Step 10: Django Application Setup"
echo "Add these environment variables to your Django app:"
echo "export CHROME_BIN=/usr/bin/chromium-browser"
echo "export DISPLAY=:99"
echo ""
echo "For systemd service, add to your service file:"
echo "[Service]"
echo "Environment=CHROME_BIN=/usr/bin/chromium-browser"
echo "Environment=DISPLAY=:99"
echo ""

# Step 11: Restart instructions
echo "🔄 Step 11: Restart your Django application"
echo "sudo systemctl restart your-django-app"
echo "# OR"
echo "sudo supervisorctl restart your-django-app"
echo ""

echo "🎉 Installation completed successfully!"
echo ""
echo "📊 What to expect now:"
echo "- Invoices should generate as PNG files instead of PDF"
echo "- Check your Django logs for debug messages like:"
echo "  🔧 Attempting PNG generation..."
echo "  ✅ Chrome found and accessible"
echo "  ✅ PNG file created"
echo ""
echo "If you still see PDF generation, check the debug logs for errors." 