use tauri::{AppHandle, Manager};

pub(crate) fn open_main(app: &AppHandle) -> Result<(), String> {
    let window = app
        .get_webview_window("main")
        .ok_or("Main window is unavailable")?;
    window.show().map_err(|error| error.to_string())?;
    window.unminimize().map_err(|error| error.to_string())?;
    window.set_focus().map_err(|error| error.to_string())
}

pub(crate) fn show_widget(app: &AppHandle) -> Result<(), String> {
    let widget = app
        .get_webview_window("companion-widget")
        .ok_or("Companion window is unavailable")?;
    widget.show().map_err(|error| error.to_string())?;
    widget.unminimize().map_err(|error| error.to_string())
}
