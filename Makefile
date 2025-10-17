# Makefile for ferry-bus-konstanz project

.PHONY: all build dev publish clean

# Build Rust WASM and copy results to npm project
build:
	@echo "🌀 Building Rust WASM..."
	cd rust && wasm-pack build --target web --release
	@echo "📦 Copying WASM pkg to npm project..."
	mkdir -p ferry-bus-display/pkg
	cp -r rust/pkg/* ferry-bus-display/pkg/
	@echo "✅ Rust WASM build complete."

# Start local development server
dev: build
	@echo "🚀 Starting development server..."
	cd ferry-bus-display && npm install && npm run dev

# Build for production (for GitHub Pages deployment)
publish: build
	@echo "🏗️ Building static site for production..."
	cd ferry-bus-display && npm install && npm run build
	@echo "✅ Static site ready in ferry-bus-display/dist"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf rust/pkg ferry-bus-display/pkg ferry-bus-display/dist
	cargo clean
	@echo "✅ Clean complete."
