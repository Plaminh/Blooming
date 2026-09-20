export function deviceTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
}

export interface ApproximateLocation { locationName: string; lat: number; lon: number }

export function requestApproximateDeviceLocation(): Promise<ApproximateLocation> {
  if (typeof navigator === 'undefined' || !navigator.geolocation) {
    return Promise.reject(new Error('Device location is unavailable. Search for a city instead.'));
  }
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const lat = Math.round(coords.latitude * 100) / 100;
        const lon = Math.round(coords.longitude * 100) / 100;
        resolve({ locationName: 'Approximate device location', lat, lon });
      },
      (error) => reject(new Error(error.code === 1
        ? 'Location permission was denied. Enable it in system settings or search for a city.'
        : error.code === 3
          ? 'Device location timed out. Try again or search for a city.'
          : 'Device location is unavailable. Search for a city instead.')),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 15 * 60 * 1000 },
    );
  });
}
