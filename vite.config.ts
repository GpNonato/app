import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron/simple'

export default defineConfig({
  plugins: [
    react(),
    electron({
      main: {
        entry: 'src/electron/main.ts',
      },
      preload: {
        input: 'src/electron/preload.ts',
        vite: {
          build: {
            rollupOptions: {
              output: {
                format: 'cjs',
                entryFileNames: '[name].js',
              },
            },
          },
        },
      },
    }),
  ],
  base: './',
  build: {
    outDir: 'dist-react',
  },
  server: {
    port: 5123,
    strictPort: true,
  },
})