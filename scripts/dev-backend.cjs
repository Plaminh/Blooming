// ./scripts/dev-backend.cjs
const { existsSync } = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const root = path.resolve(__dirname, "..");
const win = process.platform === "win32";

const candidates = [
  process.env.BLOOMING_PYTHON, // override thủ công nếu venv ở chỗ khác
  path.join(root, ".venv", win ? "Scripts/python.exe" : "bin/python"),
].filter(Boolean);

const python = candidates.find(existsSync) ?? "python"; // fallback: python trên PATH

if (python === "python") {
  console.warn(
    "[dev-backend] Không tìm thấy .venv ở root, dùng 'python' mặc định trên PATH. " +
    "Set biến BLOOMING_PYTHON nếu venv nằm chỗ khác."
  );
}

const child = spawn(python, ["-m", "uvicorn", "app.main:app", "--reload"], {
  cwd: path.join(root, "backend"),
  stdio: "inherit",
  shell: win, // Windows cần shell:true để resolve .exe đúng
});

child.on("exit", (code) => process.exit(code ?? 0));
