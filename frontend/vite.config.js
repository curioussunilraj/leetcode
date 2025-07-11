import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // As specified in docker-compose for local dev
    proxy: {
      // Proxy API requests to the backend to avoid CORS issues during development
      // Any request to /api on the frontend dev server will be forwarded to http://localhost:8000/api
      // This assumes your backend FastAPI routes are NOT prefixed with /api.
      // If they are, then this is fine. If not, you might proxy '/problems', '/submissions' etc. directly
      // or adjust FastAPI to serve under /api.
      // Current backend (main.py) has routes like /problems/, /submissions/.
      // So, if frontend makes requests to /api/problems, we need to rewrite the path.
      '/api': {
        // This target is for when the Vite dev server runs on the host machine,
        // and the backend is running in Docker, exposed on localhost:8000.
        target: 'http://localhost:8000',
        changeOrigin: true, // Needed for virtual hosted sites
        secure: false,      // Optional: if backend is http
        rewrite: (path) => path.replace(/^\/api/, ''), // Remove /api prefix when forwarding
      }
    }
  },
  build: {
    outDir: 'dist', // Output directory for build files
  }
})
