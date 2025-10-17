# Makefile at the root of your repo

.PHONY: dev

# Paths
RUST_DIR = rust
NPM_DIR = ferry-bus-display
PKG_DIR = $(RUST_DIR)/pkg

dev:
	@echo "🌀 Building Rust WASM..."
	cd $(RUST_DIR) && wasm-pack build --target web --release
	@echo "📦 Copying WASM pkg to npm project..."
	cp -r $(PKG_DIR)/* $(NPM_DIR)/pkg/
	@echo "🚀 Starting npm dev server..."
	cd $(NPM_DIR) && npm install && npm run dev
