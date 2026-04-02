import { spawn } from "child_process";
import path from "path";

export function runBot() {
  const exePath = path.join(
    process.cwd(),
    "resources",
    "Rpa Gestao",
    "Rpa Gestao.exe"
  );

  const botProcess = spawn(exePath, [], {
    stdio: "inherit",
    cwd: path.dirname(exePath),
  });

  botProcess.on("exit", (code) => {
    console.log(`Bot finalizou com código ${code}`);
  });
}