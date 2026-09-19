export function deviceTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
}

export function isDeviceCoordinates(location: string): boolean {
  return /^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$/.test(location.trim());
}

export function requestDeviceLocation(): Promise<string> {
  if (typeof navigator === 'undefined' || !navigator.geolocation) {
    return Promise.reject(new Error('Device location is unavailable. Enter a city instead.'));
  }
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => resolve(`${coords.latitude.toFixed(4)},${coords.longitude.toFixed(4)}`),
      (error) => reject(new Error(error.code === 1
        ? 'Location permission was denied. Enable it in your system settings or enter a city.'
        : 'Could not get device location. Enter a city instead.')),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 15 * 60 * 1000 },
    );
  });
}
