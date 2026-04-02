import { app, BrowserWindow } from 'electron';
import path from 'path';
import { isDev } from './util.js';

app.on("ready", () => {
    const win = new BrowserWindow({
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
        },
    });
    if (isDev()) {
        win.loadURL('http://localhost:5123'); 
    } else {
        win.loadFile(path.join(app.getAppPath(), 'dist-react/index.html'));
    }

});