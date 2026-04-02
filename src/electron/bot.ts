import { spawn } from "child_process";
import path from "path";

export function runBot() {
  const dir = path.join(process.cwd(), "resources", "Rpa Gestao");
  const exePath = path.join(dir, "Rpa Gestao.exe");

  spawn(
    "powershell.exe",
    ["-Command", `Start-Process '${exePath}' -WorkingDirectory '${dir}'`],
    { stdio: "ignore" }
  );
}