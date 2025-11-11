import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api/process': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/process/, '/process_screenshot')
      },
      '/api/health': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/health/, '/health')
      }
    }
  }
})
