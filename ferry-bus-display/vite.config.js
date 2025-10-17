import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    emptyOutDir: false
  },
  server: {
    fs: {
      allow: ['../rust/pkg']
    }
  }
})
