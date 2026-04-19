import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Vite plugin to serve actual automation progress
function automationApiPlugin() {
  return {
    name: 'automation-api',
    configureServer(server) {
      server.middlewares.use('/api/progress', (req, res) => {
        // Root dir of the project Project0
        const rootDir = path.resolve(__dirname, '..')

        const checkExists = (p) => fs.existsSync(path.join(rootDir, p))

        // Check if parser ran
        const parsedExists = checkExists('data/parsed_testcases.json')
        // Check if planner ran
        const plannedExists = checkExists('data/planned_testcases.json')
        // Check if generator ran (check tests folder for generated files)
        const testsDirExists = checkExists('tests')
        let generatedTests = false
        if (testsDirExists) {
            const files = fs.readdirSync(path.join(rootDir, 'tests'))
            generatedTests = files.some(f => f.startsWith('test_'))
        }
        // Check if validation ran
        const validationExists = checkExists('validation_report.json')

        const tasks = [
          {
            id: '1',
            name: 'Parse CSV to JSON (Parser)',
            status: parsedExists ? 'Completed' : 'Pending',
            lastUpdated: parsedExists ? fs.statSync(path.join(rootDir, 'data/parsed_testcases.json')).mtime.toISOString() : new Date().toISOString()
          },
          {
            id: '2',
            name: 'Plan Canonical Actions (Planner)',
            status: plannedExists ? 'Completed' : (parsedExists ? 'In Progress' : 'Pending'),
            lastUpdated: plannedExists ? fs.statSync(path.join(rootDir, 'data/planned_testcases.json')).mtime.toISOString() : new Date().toISOString()
          },
          {
            id: '3',
            name: 'Generate POM Framework (Generator)',
            status: generatedTests ? 'Completed' : (plannedExists ? 'In Progress' : 'Pending'),
            lastUpdated: new Date().toISOString()
          },
          {
            id: '4',
            name: 'Validate Quality (Validator)',
            status: validationExists ? 'Completed' : (generatedTests ? 'In Progress' : 'Pending'),
            lastUpdated: validationExists ? fs.statSync(path.join(rootDir, 'validation_report.json')).mtime.toISOString() : new Date().toISOString()
          }
        ];

        let logs = [];
        if (parsedExists) logs.push({ id: 'l1', message: 'Parser successfully completed CSV format.', time: fs.statSync(path.join(rootDir, 'data/parsed_testcases.json')).mtime.toISOString() });
        if (plannedExists) logs.push({ id: 'l2', message: 'Planner generated canonical actions.', time: fs.statSync(path.join(rootDir, 'data/planned_testcases.json')).mtime.toISOString() });
        if (generatedTests) logs.push({ id: 'l3', message: 'Generator scaffolded test framework.', time: new Date().toISOString() });
        if (validationExists) logs.push({ id: 'l4', message: 'Validator generated quality report.', time: fs.statSync(path.join(rootDir, 'validation_report.json')).mtime.toISOString() });
        
        logs.sort((a,b) => new Date(b.time) - new Date(a.time));

        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ tasks, logs }))
      })
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), automationApiPlugin()],
})
