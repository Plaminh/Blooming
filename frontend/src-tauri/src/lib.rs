use tauri::menu::{Menu, MenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::{AppHandle, Manager};

#[tauri::command]
fn set_tray_icon(app: AppHandle, alert: bool) -> Result<(), String> {
    let tray = app.tray_by_id("main").ok_or("Tray is unavailable")?;
    let icon_path = if alert {
        "icons/32x32_alert.png"
    } else {
        "icons/32x32.png"
    };
    let path = app
        .path()
        .resolve(icon_path, tauri::path::BaseDirectory::Resource)
        .map_err(|e| e.to_string())?;
    let icon = tauri::image::Image::from_path(path).map_err(|e| e.to_string())?;
    tray.set_icon(Some(icon)).map_err(|e| e.to_string())
}

fn open_main(app: &AppHandle) -> Result<(), String> {
    let window = app
        .get_webview_window("main")
        .ok_or("Main window is unavailable")?;
    window.show().map_err(|e| e.to_string())?;
    window.unminimize().map_err(|e| e.to_string())?;
    window.set_focus().map_err(|e| e.to_string())?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .setup(|app| {
            let path = app
                .path()
                .resolve("icons/32x32.png", tauri::path::BaseDirectory::Resource)?;
            let icon = tauri::image::Image::from_path(path)?;
            let open = MenuItem::with_id(app, "open", "Open Blooming", true, None::<&str>)?;
            let widget = MenuItem::with_id(app, "widget", "Show companion", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&open, &widget, &quit])?;
            TrayIconBuilder::with_id("main")
                .icon(icon)
                .tooltip("Blooming")
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "open" => {
                        if let Err(error) = open_main(app) {
                            eprintln!("Unable to open Blooming: {error}");
                        }
                    }
                    "widget" => {
                        if let Some(window) = app.get_webview_window("companion-widget") {
                            if let Err(error) = window
                                .show()
                                .and_then(|()| window.unminimize())
                                .and_then(|()| window.set_focus())
                            {
                                eprintln!("Unable to show companion: {error}");
                            }
                        }
                    }
                    "quit" => app.exit(0),
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        if let Err(error) = open_main(tray.app_handle()) {
                            eprintln!("Unable to open Blooming: {error}");
                        }
                    }
                })
                .build(app)?;
            Ok(())
        })
        .on_window_event(|window, event| {
            // Keep the application-level reminder owner alive while windows are hidden.
            if !matches!(window.label(), "main" | "companion-widget") {
                return;
            }
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                if let Err(error) = window.hide() {
                    eprintln!("Unable to hide window: {error}");
                }
            }
        })
        .invoke_handler(tauri::generate_handler![set_tray_icon])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
