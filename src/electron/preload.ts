import { contextBridge } from "electron";
import { runBot } from "./bot.js";

contextBridge.exposeInMainWorld("api", {
  runBot: () => runBot(),
});