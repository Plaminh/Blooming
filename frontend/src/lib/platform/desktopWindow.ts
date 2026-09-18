export interface DesktopWindowHandle {
  isMaximized(): Promise<boolean>;
  isMinimized(): Promise<boolean>;
  isVisible(): Promise<boolean>;
  minimize(): Promise<void>;
  toggleMaximize(): Promise<void>;
  unminimize(): Promise<void>;
  show(): Promise<void>;
  hide(): Promise<void>;
  close(): Promise<void>;
  setFocus(): Promise<void>;
  startDragging(): Promise<void>;
}

export interface DesktopWindowResolver {
  getCurrentWindow(): Promise<DesktopWindowHandle | null>;
  getMainWindow(): Promise<DesktopWindowHandle | null>;
}

export interface DesktopWindowService {
  openMainWindow(): Promise<void>;
  minimizeCurrent(): Promise<void>;
  toggleMaximizeCurrent(): Promise<boolean>;
  isCurrentMaximized(): Promise<boolean>;
  hideCurrent(): Promise<void>;
  closeCurrent(): Promise<void>;
  startDraggingCurrent(): Promise<void>;
}

type TauriWindowModule = typeof import("@tauri-apps/api/window");

export function isTauriRuntime(): boolean {
  return typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
}

let tauriWindowModule: Promise<TauriWindowModule | null> | null = null;

function loadTauriWindowModule(): Promise<TauriWindowModule | null> {
  if (!isTauriRuntime()) return Promise.resolve(null);

  tauriWindowModule ??= import("@tauri-apps/api/window").catch(() => null);
  return tauriWindowModule;
}

const tauriResolver: DesktopWindowResolver = {
  async getCurrentWindow() {
    const module = await loadTauriWindowModule();
    return module?.getCurrentWindow() ?? null;
  },
  async getMainWindow() {
    const module = await loadTauriWindowModule();
    return (await module?.Window.getByLabel("main")) ?? null;
  },
};

export function createDesktopWindowService(
  resolver: DesktopWindowResolver,
): DesktopWindowService {
  let openingMainWindow: Promise<void> | null = null;

  async function withCurrentWindow(
    action: (currentWindow: DesktopWindowHandle) => Promise<void>,
  ): Promise<void> {
    try {
      const currentWindow = await resolver.getCurrentWindow();
      if (currentWindow) await action(currentWindow);
    } catch {
      // Browser previews and unsupported host operations intentionally do nothing.
    }
  }

  return {
    openMainWindow() {
      if (openingMainWindow) return openingMainWindow;

      openingMainWindow = (async () => {
        try {
          const mainWindow = await resolver.getMainWindow();
          if (!mainWindow) return;

          if (await mainWindow.isMinimized()) await mainWindow.unminimize();
          if (!(await mainWindow.isVisible())) await mainWindow.show();
          await mainWindow.setFocus();
        } catch {
          // Missing Tauri APIs and rejected desktop operations are safe no-ops.
        }
      })().finally(() => {
        openingMainWindow = null;
      });

      return openingMainWindow;
    },
    minimizeCurrent() {
      return withCurrentWindow((currentWindow) => currentWindow.minimize());
    },
    async toggleMaximizeCurrent() {
      let maximized = false;
      await withCurrentWindow(async (currentWindow) => {
        await currentWindow.toggleMaximize();
        maximized = await currentWindow.isMaximized();
      });
      return maximized;
    },
    async isCurrentMaximized() {
      let maximized = false;
      await withCurrentWindow(async (currentWindow) => {
        maximized = await currentWindow.isMaximized();
      });
      return maximized;
    },
    hideCurrent() {
      return withCurrentWindow((currentWindow) => currentWindow.hide());
    },
    closeCurrent() {
      return withCurrentWindow((currentWindow) => currentWindow.close());
    },
    startDraggingCurrent() {
      return withCurrentWindow((currentWindow) =>
        currentWindow.startDragging(),
      );
    },
  };
}

export const desktopWindowService = createDesktopWindowService(tauriResolver);

export interface NativeSettings {
  launch_on_startup: boolean;
  widget_always_on_top: boolean;
}

export const desktop = {
  ...desktopWindowService,
  async readSettings(): Promise<NativeSettings | null> {
    if (!isTauriRuntime()) return null;
    const autostart = await import("@tauri-apps/plugin-autostart");
    const module = await loadTauriWindowModule();
    const widget = await module?.Window.getByLabel("companion-widget");
    if (!widget) throw new Error("Companion window is unavailable.");
    return {
      launch_on_startup: await autostart.isEnabled(),
      widget_always_on_top: await widget.isAlwaysOnTop(),
    };
  },
  async reconcileSettings(settings: NativeSettings) {
    if (!isTauriRuntime()) return;
    const autostart = await import("@tauri-apps/plugin-autostart");
    const module = await loadTauriWindowModule();
    const widget = await module?.Window.getByLabel("companion-widget");
    if (!widget) throw new Error("Companion window is unavailable.");
    // Attempt both settings, including when compensating for a failed save.
    const results = await Promise.allSettled([
      (async () => {
        if ((await autostart.isEnabled()) !== settings.launch_on_startup) {
          if (settings.launch_on_startup) await autostart.enable();
          else await autostart.disable();
        }
        if ((await autostart.isEnabled()) !== settings.launch_on_startup)
          throw new Error("Start at login could not be applied.");
      })(),
      (async () => {
        if ((await widget.isAlwaysOnTop()) !== settings.widget_always_on_top)
          await widget.setAlwaysOnTop(settings.widget_always_on_top);
        if ((await widget.isAlwaysOnTop()) !== settings.widget_always_on_top)
          throw new Error("Always-on-top could not be applied.");
      })(),
    ]);
    for (const result of results) {
      if (result.status === "rejected") throw result.reason;
    }
  },
  async showWidget() {
    if (!isTauriRuntime()) return;
    const module = await loadTauriWindowModule();
    const widget = await module?.Window.getByLabel("companion-widget");
    if (!widget) throw new Error("Companion window is unavailable.");
    await widget.show();
    await widget.unminimize();
    await widget.setFocus();
  },
  async scheduleUpdated() {
    if (!isTauriRuntime()) return;
    const module = await loadTauriWindowModule();
    const target =
      module?.getCurrentWindow().label === "companion-widget"
        ? "main"
        : "companion-widget";
    const { emitTo } = await import("@tauri-apps/api/event");
    await emitTo<null>(target, "blooming:schedule-updated", null);
  },
  async onScheduleUpdated(callback: () => void): Promise<() => void> {
    if (!isTauriRuntime()) return () => {};
    const { listen } = await import("@tauri-apps/api/event");
    return listen<null>("blooming:schedule-updated", callback);
  },
  async settingsUpdated(): Promise<void> {
    if (!isTauriRuntime()) return;
    const { emitTo } = await import("@tauri-apps/api/event");
    await emitTo<null>("companion-widget", "blooming:settings-updated", null);
  },
  async onSettingsUpdated(callback: () => void): Promise<() => void> {
    if (!isTauriRuntime()) return () => {};
    const { listen } = await import("@tauri-apps/api/event");
    return listen<null>("blooming:settings-updated", callback);
  },
  async setTrayAlert(alert: boolean) {
    if (!isTauriRuntime()) return;
    const { invoke } = await import("@tauri-apps/api/core");
    await invoke<void>("set_tray_icon", { alert });
  },
  async isReminderOwner(): Promise<boolean> {
    if (!isTauriRuntime()) return false;
    const module = await loadTauriWindowModule();
    return module?.getCurrentWindow().label === "companion-widget";
  },
};
