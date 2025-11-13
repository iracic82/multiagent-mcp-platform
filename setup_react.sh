#!/bin/bash

echo "🚀 Setting up React Frontend..."

# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
echo "📦 Installing dependencies..."
npm install

# Install Tailwind CSS
echo "🎨 Installing Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer

# Create PostCSS config
cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

echo "✅ Setup complete!"
echo ""
echo "To run the development server:"
echo "  cd frontend && npm start"
echo ""
echo "To build for production:"
echo "  cd frontend && npm run build"
