import { describe, expect, it, vi } from 'vitest';
import {
  createDesktopWindowService,
  desktop,
  desktopWindowService,
  reconcileNativeSettings,
  type DesktopWindowHandle,
  type DesktopWindowResolver,
} from './desktopWindow';
import { emitTo, listen } from '@tauri-apps/api/event';

vi.mock('@tauri-apps/api/event', () => ({
  emitTo: vi.fn().mockResolvedValue(undefined),
  listen: vi.fn().mockResolvedValue(() => {}),
}));

function windowHandle(overrides: Partial<DesktopWindowHandle> = {}): DesktopWindowHandle {
  return {
    isMaximized: vi.fn().mockResolvedValue(false),
    isMinimized: vi.fn().mockResolvedValue(false),
    isVisible: vi.fn().mockResolvedValue(true),
    minimize: vi.fn().mockResolvedValue(undefined),
    toggleMaximize: vi.fn().mockResolvedValue(undefined),
    unminimize: vi.fn().mockResolvedValue(undefined),
    show: vi.fn().mockResolvedValue(undefined),
    hide: vi.fn().mockResolvedValue(undefined),
    close: vi.fn().mockResolvedValue(undefined),
    setFocus: vi.fn().mockResolvedValue(undefined),
    startDragging: vi.fn().mockResolvedValue(undefined),
    ...overrides,
  };
}

function resolver(mainWindow: DesktopWindowHandle | null): DesktopWindowResolver {
  return {
    getMainWindow: vi.fn().mockResolvedValue(mainWindow),
    getCurrentWindow: vi.fn().mockResolvedValue(null),
  };
}

describe('desktopWindowService', () => {
  it('reconciles native autostart and widget always-on-top settings', async () => {
    let autostartEnabled = false;
    let alwaysOnTop = true;
    const autostart = {
      isEnabled: vi.fn(async () => autostartEnabled),
      enable: vi.fn(async () => { autostartEnabled = true; }),
      disable: vi.fn(async () => { autostartEnabled = false; }),
    };
    const widget = {
      isAlwaysOnTop: vi.fn(async () => alwaysOnTop),
      setAlwaysOnTop: vi.fn(async (value: boolean) => { alwaysOnTop = value; }),
    };

    await reconcileNativeSettings(
      { launch_on_startup: true, widget_always_on_top: false },
      autostart,
      widget,
    );

    expect(autostart.enable).toHaveBeenCalledTimes(1);
    expect(autostart.disable).not.toHaveBeenCalled();
    expect(widget.setAlwaysOnTop).toHaveBeenCalledWith(false);
  });

  it('notifies the companion widget after settings change', async () => {
    Object.defineProperty(window, '__TAURI_INTERNALS__', { value: {}, configurable: true });
    try {
      const callback = vi.fn();
      await desktop.settingsUpdated();
      await desktop.onSettingsUpdated(callback);
      expect(emitTo).toHaveBeenCalledWith('companion-widget', 'blooming:settings-updated', null);
      expect(listen).toHaveBeenCalledWith('blooming:settings-updated', callback);
    } finally {
      delete (window as Window & { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__;
    }
  });
  it('shows a hidden main window and focuses the existing instance', async () => {
    const mainWindow = windowHandle({ isVisible: vi.fn().mockResolvedValue(false) });
    const service = createDesktopWindowService(resolver(mainWindow));

    await service.openMainWindow();

    expect(mainWindow.show).toHaveBeenCalledTimes(1);
    expect(mainWindow.unminimize).not.toHaveBeenCalled();
    expect(mainWindow.setFocus).toHaveBeenCalledTimes(1);
  });

  it('unminimizes and focuses a minimized main window', async () => {
    const mainWindow = windowHandle({ isMinimized: vi.fn().mockResolvedValue(true) });
    const service = createDesktopWindowService(resolver(mainWindow));

    await service.openMainWindow();

    expect(mainWindow.unminimize).toHaveBeenCalledTimes(1);
    expect(mainWindow.show).not.toHaveBeenCalled();
    expect(mainWindow.setFocus).toHaveBeenCalledTimes(1);
  });

  it('coalesces rapid repeated opens into one in-flight operation', async () => {
    const mainWindow = windowHandle();
    let releaseMainWindow: ((window: DesktopWindowHandle) => void) | undefined;
    const pendingMainWindow = new Promise<DesktopWindowHandle>((resolve) => {
      releaseMainWindow = resolve;
    });
    const resolverMock: DesktopWindowResolver = {
      getMainWindow: vi.fn(() => pendingMainWindow),
      getCurrentWindow: vi.fn().mockResolvedValue(null),
    };
    const service = createDesktopWindowService(resolverMock);

    const firstOpen = service.openMainWindow();
    const secondOpen = service.openMainWindow();
    releaseMainWindow?.(mainWindow);
    await Promise.all([firstOpen, secondOpen]);

    expect(resolverMock.getMainWindow).toHaveBeenCalledTimes(1);
    expect(mainWindow.setFocus).toHaveBeenCalledTimes(1);
  });

  it('safely no-ops in browser mode', async () => {
    // Test desktopWindowService
    await expect(desktopWindowService.openMainWindow()).resolves.toBeUndefined();
    await expect(desktopWindowService.minimizeCurrent()).resolves.toBeUndefined();
    await expect(desktopWindowService.hideCurrent()).resolves.toBeUndefined();
    
    // Test desktop
    await expect(desktop.showWidget()).resolves.toBeUndefined();
    await expect(desktop.setTrayAlert(true)).resolves.toBeUndefined();
    await expect(desktop.scheduleUpdated()).resolves.toBeUndefined();
    
    // Event listeners should return empty functions
    const off = await desktop.onScheduleUpdated(() => {});
    expect(typeof off).toBe('function');
    off();
  });
});
