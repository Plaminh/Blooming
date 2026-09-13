import { describe, expect, it, vi } from 'vitest';
import {
  createDesktopWindowService,
  desktopWindowService,
  type DesktopWindowHandle,
  type DesktopWindowResolver,
} from './desktopWindow';

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
    await expect(desktopWindowService.openMainWindow()).resolves.toBeUndefined();
    await expect(desktopWindowService.minimizeCurrent()).resolves.toBeUndefined();
    await expect(desktopWindowService.hideCurrent()).resolves.toBeUndefined();
  });
});
