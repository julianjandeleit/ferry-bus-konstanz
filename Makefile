.PHONY: dev build publish

# Local development: build Rust WASM, copy pkg, start Vite dev server
dev:
	@echo "🌀 Building Rust WASM..."
	cd rust && wasm-pack build --target web
	@echo "📦 Copying WASM pkg to npm project..."
	cp -r rust/pkg/* ferry-bus-display/pkg/
	@echo "🚀 Starting Vite dev server..."
	cd ferry-bus-display && npm install && npm run dev

# Build only: Rust WASM + copy pkg (no dev server)
build:
	@echo "🌀 Building Rust WASM..."
	cd rust && wasm-pack build --target web --release
	@echo "📦 Copying WASM pkg to npm project..."
	cp -r rust/pkg/* ferry-bus-display/pkg/
	@echo "✅ Build complete."

# Publish for GitHub Pages: build + copy pkg + npm build
publish: build
	@echo "📦 Installing npm dependencies..."
	cd ferry-bus-display && npm install
	@echo "📦 Building static site..."
	cd ferry-bus-display && npm run build
	@echo "✅ Ready to deploy: ferry-bus-display/dist contains static site"
