import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('api', {
  runBot: (routineCode: string) => ipcRenderer.invoke('run-bot', routineCode),
})