// ./scripts/run-python.cjs
const { existsSync } = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const root = path.resolve(__dirname, "..");
const win = process.platform === "win32";

const candidates = [
  process.env.BLOOMING_PYTHON,
  path.join(root, ".venv", win ? "Scripts/python.exe" : "bin/python"),
].filter(Boolean);

const python = candidates.find(existsSync) ?? "python";

const args = process.argv.slice(2);

const child = spawn(python, args, {
  cwd: path.join(root, "backend"),
  stdio: "inherit",
  shell: win,
  env: {
    ...process.env,
    PYTHONPYCACHEPREFIX: path.join(root, ".cache", "python"),
  },
});

child.on("exit", (code) => process.exit(code ?? 0));
