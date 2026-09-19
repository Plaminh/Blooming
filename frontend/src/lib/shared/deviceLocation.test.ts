import { afterEach, expect, test, vi } from 'vitest';
import { deviceTimezone, isDeviceCoordinates, requestDeviceLocation } from './deviceLocation';

afterEach(() => vi.unstubAllGlobals());

test('reads the device timezone and formats permitted coordinates', async () => {
  expect(deviceTimezone()).toBe(Intl.DateTimeFormat().resolvedOptions().timeZone);
  vi.stubGlobal('navigator', {
    geolocation: {
      getCurrentPosition(success: (position: GeolocationPosition) => void) {
        success({ coords: { latitude: 10.823099, longitude: 106.629701 } } as GeolocationPosition);
      },
    },
  });
  const location = await requestDeviceLocation();
  expect(location).toBe('10.8231,106.6297');
  expect(isDeviceCoordinates(location)).toBe(true);
});

test('reports denied device location without enabling weather', async () => {
  vi.stubGlobal('navigator', {
    geolocation: {
      getCurrentPosition(_success: unknown, failure: (error: GeolocationPositionError) => void) {
        failure({ code: 1 } as GeolocationPositionError);
      },
    },
  });
  await expect(requestDeviceLocation()).rejects.toThrow('permission was denied');
});
