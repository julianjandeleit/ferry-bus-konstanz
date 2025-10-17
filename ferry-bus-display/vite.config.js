import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    emptyOutDir: false
  },
  root: ".",
  server: {
    fs: {
      allow: ['../rust/pkg', "."]
    }
  }
})
