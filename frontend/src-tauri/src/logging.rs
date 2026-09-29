use std::fs::{self, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::{Mutex, OnceLock};

const MAX_LOG_BYTES: u64 = 1_000_000;
const ROTATED_LOG_COUNT: usize = 5;
static LOG_PATH: OnceLock<Mutex<PathBuf>> = OnceLock::new();

pub(crate) fn initialize(path: PathBuf) -> io::Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let _ = LOG_PATH.set(Mutex::new(path));
    native_log("INFO", "application setup");
    Ok(())
}

fn rotate_logs(path: &Path) -> io::Result<()> {
    let oldest = path.with_extension(format!("log.{ROTATED_LOG_COUNT}"));
    match fs::remove_file(oldest) {
        Ok(()) => {}
        Err(error) if error.kind() == io::ErrorKind::NotFound => {}
        Err(error) => return Err(error),
    }
    for index in (1..ROTATED_LOG_COUNT).rev() {
        let from = path.with_extension(format!("log.{index}"));
        let to = path.with_extension(format!("log.{}", index + 1));
        match fs::rename(from, to) {
            Ok(()) => {}
            Err(error) if error.kind() == io::ErrorKind::NotFound => {}
            Err(error) => return Err(error),
        }
    }
    fs::rename(path, path.with_extension("log.1"))
}

pub(crate) fn native_log(level: &str, message: &str) {
    let Some(path) = LOG_PATH.get() else { return };
    let Ok(path) = path.lock() else { return };
    if fs::metadata(&*path)
        .map(|metadata| metadata.len() > MAX_LOG_BYTES)
        .unwrap_or(false)
    {
        if let Err(error) = rotate_logs(&path) {
            eprintln!("native log rotation failed: {error}");
            return;
        }
    }
    match OpenOptions::new().create(true).append(true).open(&*path) {
        Ok(mut file) => {
            let sanitized = message.replace('\r', " ").replace('\n', " ");
            if let Err(error) = writeln!(file, "{level} {sanitized}") {
                eprintln!("native log write failed: {error}");
            }
        }
        Err(error) => eprintln!("native log open failed: {error}"),
    }
}
