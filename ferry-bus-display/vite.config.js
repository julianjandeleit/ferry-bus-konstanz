import { defineConfig } from 'vite'

export default defineConfig({
  base: '/ferry-bus-konstanz/',  // adjust to your repo name
  server: {
    fs: {
      allow: ['../rust/pkg'] // allow access to WASM pkg
    }
  }
})
