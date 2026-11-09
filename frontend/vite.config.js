import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

const root = path.dirname(fileURLToPath(import.meta.url))
const sources = {
  team: 'src/duel/team', ai: 'src/duel/ai',
  fixed: 'src/duel/fixed', solutions: 'teacher/solutions',
}

export default defineConfig(({ mode }) => {
  const requested = path.join(root, sources[mode] ?? sources.team)
  const source = fs.existsSync(requested) ? requested : path.join(root, sources.team)
  return {
    plugins: [react()],
    resolve: { alias: { '@cartelera': source } },
    server: { host: 'localhost', port: 5173, strictPort: true },
    test: {
      environment: 'jsdom', globals: true,
      setupFiles: './src/setupTests.js',
    },
  }
})
