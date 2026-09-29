use tauri::{AppHandle, Emitter};

use crate::logging::native_log;

pub(crate) fn is_autostart_launch<I, S>(args: I) -> bool
where
    I: IntoIterator<Item = S>,
    S: AsRef<str>,
{
    args.into_iter().any(|arg| arg.as_ref() == "--autostart")
}

pub(crate) fn handle_resume(app: &AppHandle) {
    native_log("INFO", "native lifecycle resumed");
    if let Err(error) = app.emit("blooming:resync-requested", ()) {
        native_log(
            "ERROR",
            &format!("unable to request frontend resync: {error}"),
        );
    }
}

#[cfg(test)]
mod tests {
    use super::is_autostart_launch;

    #[test]
    fn detects_only_explicit_autostart_mode() {
        assert!(is_autostart_launch(["blooming", "--autostart"]));
        assert!(!is_autostart_launch(["blooming"]));
        assert!(!is_autostart_launch(["blooming", "--other"]));
    }
}
