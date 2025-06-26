#!/bin/bash

echo "🚀 Installing wkhtmltoimage for PNG invoice generation"
echo "This is much simpler than Chrome/Chromium setup!"
echo "=" * 50

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install wkhtmltopdf (includes wkhtmltoimage)
echo "🖼️ Installing wkhtmltopdf (includes wkhtmltoimage)..."
sudo apt-get install -y wkhtmltopdf

# Test installation
echo "🧪 Testing installation..."
if command -v wkhtmltoimage &> /dev/null; then
    echo "✅ wkhtmltoimage installed successfully!"
    wkhtmltoimage --version
    
    # Test basic functionality
    echo "<h1>Test</h1>" > test.html
    wkhtmltoimage --format png --width 400 --height 300 test.html test.png
    
    if [ -f "test.png" ]; then
        echo "✅ Basic PNG generation test passed!"
        rm test.html test.png
    else
        echo "❌ Basic test failed"
    fi
else
    echo "❌ Installation failed"
    exit 1
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "📋 What this gives you:"
echo "- ✅ No Chrome/Chromium dependencies"
echo "- ✅ No virtual display server needed"
echo "- ✅ Much smaller installation"
echo "- ✅ Works out of the box on Ubuntu"
echo ""
echo "🔄 Now restart your Django app:"
echo "sudo systemctl restart your-django-app"
echo ""
echo "📊 Expected behavior:"
echo "🔧 Trying wkhtmltoimage for invoice INV-00001..."
echo "✅ PNG created with wkhtmltoimage: /path/to/file.png" 