import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import { isDev } from './util.js'
import { runBot } from './bot.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)         

app.on('ready', () => {
  const win = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
    },
  })
  if (isDev()) {
    win.loadURL('http://localhost:5123')
  } else {
    win.loadFile(path.join(app.getAppPath(), 'dist-react/index.html'))
  }
})

ipcMain.handle('run-bot', async () => {
  return await runBot()
})