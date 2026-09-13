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

type TauriWindowModule = typeof import('@tauri-apps/api/window');

function isTauriRuntime(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

let tauriWindowModule: Promise<TauriWindowModule | null> | null = null;

function loadTauriWindowModule(): Promise<TauriWindowModule | null> {
  if (!isTauriRuntime()) return Promise.resolve(null);

  tauriWindowModule ??= import('@tauri-apps/api/window').catch(() => null);
  return tauriWindowModule;
}

const tauriResolver: DesktopWindowResolver = {
  async getCurrentWindow() {
    const module = await loadTauriWindowModule();
    return module?.getCurrentWindow() ?? null;
  },
  async getMainWindow() {
    const module = await loadTauriWindowModule();
    return (await module?.Window.getByLabel('main')) ?? null;
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
      return withCurrentWindow((currentWindow) => currentWindow.startDragging());
    },
  };
}

export const desktopWindowService = createDesktopWindowService(tauriResolver);
