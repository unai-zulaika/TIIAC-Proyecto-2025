import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // permite acceder desde fuera del contenedor
    watch: {
      usePolling: true, // necesario para detectar cambios en Docker
      interval: 100,    // (opcional) frecuencia del polling
    },
  },
})
