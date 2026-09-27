import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/svelte';
import WidgetPage from './+page.svelte';
import { api, APIError } from '$lib/api';
import { desktop } from '$lib/platform/desktopWindow';
import { environmentStore } from '$lib/shared/stores/environmentStore';

vi.mock('$lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
  },
  APIError: class extends Error {
    status: number;
    constructor(status: number, message: string) {
      super(message);
      this.status = status;
    }
  }
}));

vi.mock('$lib/platform/desktopWindow', () => ({
  desktop: {
    showWidget: vi.fn(),
    hideCurrent: vi.fn(),
    openMainWindow: vi.fn(),
    setTrayAlert: vi.fn(),
    scheduleUpdated: vi.fn(),
    onScheduleUpdated: vi.fn().mockResolvedValue(() => {}),
    onSettingsUpdated: vi.fn().mockResolvedValue(() => {}),
  },
  desktopWindowService: {
    openMainWindow: vi.fn(),
  }
}));



vi.mock('$lib/shared/stores/authStore', () => ({
  authStore: {
    initialize: vi.fn().mockResolvedValue(undefined),
    subscribe: vi.fn((cb) => { cb({ isAuthenticated: true }); return () => {}; })
  }
}));


describe('Widget Page Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    environmentStore.resetForTests();
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [];
      if (url === '/garden') return { plants: [] };
      return null;
    });
    vi.mocked(api.put).mockResolvedValue({});
  });
  
  afterEach(() => {
    environmentStore.resetForTests();
  });

  it('1. active focus + due reminder -> FOCUSING', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') return { id: 'f1', status: 'RUNNING', started_at: new Date().toISOString(), total_paused_seconds: 0, planned_focus_seconds: 1500 };
      if (url === '/reminders/due') return [{ id: 'r1', message: 'Due', due_at: new Date().toISOString() }];
      return null;
    });
    
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('PAUSE')).toBeTruthy();
      expect(screen.queryByText('1 REMINDER')).toBeNull();
    });
  });

  it('2. session result + due reminder -> SESSION_RESULT (ending)', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      const past = new Date(Date.now() - 2000 * 1000).toISOString();
      if (url === '/focus/active') return { id: 'f2', status: 'RUNNING', started_at: past, total_paused_seconds: 0, planned_focus_seconds: 1500 };
      if (url === '/reminders/due') return [{ id: 'r1', message: 'Due', due_at: new Date().toISOString() }];
      return null;
    });
    
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('Session ended. What was the outcome?')).toBeTruthy();
      expect(screen.queryByText('1 REMINDER')).toBeNull();
    });
  });

  it('3. due reminder only -> REMINDER', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'Read a book', due_at: new Date().toISOString() }];
      return null;
    });
    
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('1 REMINDER')).toBeTruthy();
      expect(screen.queryByText('Read a book')).toBeTruthy();
    });
  });

  it('4. nothing active/due -> DEFAULT', async () => {
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('Waiting for a focus session...')).toBeTruthy();
    });
  });

  it('5. widget_visibility false -> HIDDEN', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: false, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [];
      if (url === '/garden') return { plants: [] };
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('Widget hidden in settings.')).toBeTruthy();
    });
  });

  it('6. widget loads due reminders', async () => {
    render(WidgetPage);
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/reminders/due');
    });
  });
  
  it('7. one due reminder appears', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'Read a book', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('1 REMINDER')).toBeTruthy();
      expect(screen.queryByText('Read a book')).toBeTruthy();
    });
  });

  it('8. multiple reminders use deterministic first reminder', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [
        { id: 'r1', message: 'First', due_at: new Date().toISOString() },
        { id: 'r2', message: 'Second', due_at: new Date().toISOString() }
      ];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('1 REMINDER')).toBeTruthy();
      expect(screen.queryByText('First')).toBeTruthy();
      expect(screen.queryByText('Second')).toBeNull(); // it only displays the first one based on our code
    });
  });

  it('9. successful action refreshes reminders', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    
    await waitFor(() => {
      expect(screen.queryByText('MARK COMPLETED')).toBeTruthy();
    });
    
    vi.mocked(api.post).mockResolvedValue({});
    
    await fireEvent.click(screen.getByText('MARK COMPLETED'));
    
    expect(api.post).toHaveBeenCalledWith('/reminders/r1/actions', { action_type: 'MARK_COMPLETED' });
    
    // It should refresh reminders
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/reminders/due');
    });
  });

  it('10. final reminder handled -> state returns DEFAULT', async () => {
    let callCount = 0;
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') {
        callCount++;
        if (callCount === 1) return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
        return []; // Second call returns empty
      }
      return null;
    });
    
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('MARK COMPLETED')).toBeTruthy();
    });
    
    vi.mocked(api.post).mockResolvedValue({});
    await fireEvent.click(screen.getByText('MARK COMPLETED'));
    
    await waitFor(() => {
      expect(screen.queryByText('Waiting for a focus session...')).toBeTruthy();
    });
  });

  it('11. action failure keeps REMINDER visible', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('MARK COMPLETED')).toBeTruthy();
    });
    
    vi.mocked(api.post).mockRejectedValue(new Error('Backend error'));
    await fireEvent.click(screen.getByText('MARK COMPLETED'));
    
    await waitFor(() => {
      expect(screen.queryByText('Backend error')).toBeTruthy();
      expect(screen.queryByText('1 REMINDER')).toBeTruthy();
    });
  });

  it('12. duplicate clicks send one request', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('MARK COMPLETED')).toBeTruthy();
    });
    
    let resolvePost: any;
    const postPromise = new Promise(r => { resolvePost = r; });
    vi.mocked(api.post).mockReturnValue(postPromise);
    
    const btn = screen.getByText('MARK COMPLETED');
    fireEvent.click(btn);
    fireEvent.click(btn);
    
    expect(api.post).toHaveBeenCalledTimes(1);
    resolvePost();
  });

  it('13. only the four allowed reminder actions are exposed', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    
    render(WidgetPage);
    await waitFor(() => {
      expect(screen.queryByText('CREATE PLAN')).toBeTruthy();
      expect(screen.queryByText('MARK COMPLETED')).toBeTruthy();
      expect(screen.queryByText('MOVE MILESTONE')).toBeTruthy();
      expect(screen.queryByText('REMIND LATER')).toBeTruthy();
      expect(screen.queryByText('VIEW')).toBeNull();
      expect(screen.queryByText('DISMISS')).toBeNull();
    });
  });

  it('14. MARK_COMPLETED calls reminder action API', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => screen.queryByText('MARK COMPLETED'));
    vi.mocked(api.post).mockResolvedValue({});
    await fireEvent.click(screen.getByText('MARK COMPLETED'));
    expect(api.post).toHaveBeenCalledWith('/reminders/r1/actions', { action_type: 'MARK_COMPLETED' });
  });

  it('15. MOVE_MILESTONE sends required new due date', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => screen.queryByText('MOVE MILESTONE'));
    
    vi.spyOn(window, 'prompt').mockReturnValue('2026-10-01');
    vi.mocked(api.post).mockResolvedValue({});
    
    await fireEvent.click(screen.getByText('MOVE MILESTONE'));
    expect(api.post).toHaveBeenCalledWith('/reminders/r1/actions', { action_type: 'MOVE_MILESTONE', new_due_at: '2026-10-01T00:00:00.000Z' });
  });

  it('16. REMIND_LATER sends required new due date', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => screen.queryByText('REMIND LATER'));
    
    vi.spyOn(window, 'prompt').mockReturnValue('2026-10-02');
    vi.mocked(api.post).mockResolvedValue({});
    
    await fireEvent.click(screen.getByText('REMIND LATER'));
    expect(api.post).toHaveBeenCalledWith('/reminders/r1/actions', { action_type: 'REMIND_LATER', new_due_at: '2026-10-02T00:00:00.000Z' });
  });

  it('17. CREATE_PLAN follows existing handoff/navigation', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => screen.queryByText('CREATE PLAN'));
    vi.mocked(api.post).mockResolvedValue({});
    await fireEvent.click(screen.getByText('CREATE PLAN'));
    
    await waitFor(() => {
      expect(desktop.openMainWindow).toHaveBeenCalled();
    });
  });

  it('18. due reminder -> red dot enabled', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(desktop.setTrayAlert).toHaveBeenCalledWith(true);
    });
  });

  it('19. no due reminder -> red dot disabled', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(desktop.setTrayAlert).toHaveBeenCalledWith(false);
    });
  });

  it('20. successful final action clears red dot', async () => {
    let callCount = 0;
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') {
        callCount++;
        if (callCount === 1) return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
        return [];
      }
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(desktop.setTrayAlert).toHaveBeenCalledWith(true);
    });
    
    vi.mocked(api.post).mockResolvedValue({});
    await fireEvent.click(screen.getByText('MARK COMPLETED'));
    
    await waitFor(() => {
      expect(desktop.setTrayAlert).toHaveBeenCalledWith(false);
    });
  });

  it('21. opening widget alone does not clear red dot', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: true, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [{ id: 'r1', message: 'First', due_at: new Date().toISOString() }];
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(desktop.setTrayAlert).toHaveBeenCalledWith(true);
    });
    
    // Simulate window focus (opening widget)
    window.dispatchEvent(new Event('focus'));
    
    // Should fetch again, still one reminder, setTrayAlert(true) again, not false
    await waitFor(() => {
      expect(desktop.setTrayAlert).not.toHaveBeenCalledWith(false);
    });
  });

  it('22. widget_visibility=false calls desktop hide', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: false, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [];
      if (url === '/garden') return { plants: [] };
      return null;
    });
    render(WidgetPage);
    await waitFor(() => {
      expect(desktop.hideCurrent).toHaveBeenCalled();
    });
  });

  it('23. widget_visibility=true calls desktop show', async () => {
    render(WidgetPage);
    await waitFor(() => {
      expect(desktop.showWidget).toHaveBeenCalled();
    });
  });
  
  it('24. persisted hidden setting is applied during startup reconciliation', async () => {
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (url === '/me/settings') return { widget_visibility: false, weather_enabled: false };
      if (url === '/weather/current') return { status: 'DISABLED' };
      if (url === '/focus/active') throw new APIError(404, 'Not Found');
      if (url === '/reminders/due') return [];
      if (url === '/garden') return { plants: [] };
      return null;
    });
    
    // Simulate initial load without the widget page to initialize environmentStore
    const release = environmentStore.init();
    
    // Wait for the fetch
    await new Promise(r => setTimeout(r, 10));
    
    // Now render the widget page
    render(WidgetPage);
    
    await waitFor(() => {
      expect(desktop.hideCurrent).toHaveBeenCalled();
    });
    
    release();
  });
});
