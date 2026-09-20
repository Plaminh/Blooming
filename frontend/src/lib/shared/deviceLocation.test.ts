import { afterEach, expect, test, vi } from 'vitest';
import { deviceTimezone, requestApproximateDeviceLocation } from './deviceLocation';

afterEach(() => vi.unstubAllGlobals());

test('reads the device timezone', () => {
  expect(deviceTimezone()).toBe(Intl.DateTimeFormat().resolvedOptions().timeZone);
});

test('only rounded coordinates leave the geolocation callback', async () => {
  const getCurrentPosition = vi.fn((success: (position: GeolocationPosition) => void) => {
    success({ coords: { latitude: 10.823099, longitude: 106.629701 } } as GeolocationPosition);
  });
  vi.stubGlobal('navigator', { geolocation: { getCurrentPosition } });
  const outbound = vi.fn();
  const location = await requestApproximateDeviceLocation();
  outbound(location);
  expect(getCurrentPosition).toHaveBeenCalledTimes(1);
  expect(outbound).toHaveBeenCalledWith({ locationName: 'Approximate device location', lat: 10.82, lon: 106.63 });
  expect(JSON.stringify(outbound.mock.calls)).not.toContain('10.823099');
  expect(JSON.stringify(outbound.mock.calls)).not.toContain('106.629701');
});

test.each([[1, 'permission was denied'], [3, 'timed out'], [2, 'unavailable']] as const)(
  'reports geolocation error %i', async (code, message) => {
    vi.stubGlobal('navigator', { geolocation: { getCurrentPosition: (_: unknown, failure: (error: GeolocationPositionError) => void) => failure({ code } as GeolocationPositionError) } });
    await expect(requestApproximateDeviceLocation()).rejects.toThrow(message);
  },
);

test('reports unavailable browser geolocation', async () => {
  vi.stubGlobal('navigator', {});
  await expect(requestApproximateDeviceLocation()).rejects.toThrow('unavailable');
});
