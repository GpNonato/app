import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('api', {
  runBot: () => ipcRenderer.invoke('run-bot'),
})