import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import { tick } from 'svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import WeatherLocationPicker from './WeatherLocationPicker.svelte';
import { api } from '$lib/api';
import { requestApproximateDeviceLocation } from '$lib/shared/deviceLocation';

vi.mock('$lib/api', () => ({ api: { get: vi.fn() } }));
vi.mock('$lib/shared/deviceLocation', () => ({
  requestApproximateDeviceLocation: vi.fn(),
}));

afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });
beforeEach(() => { vi.clearAllMocks(); });

describe('WeatherLocationPicker', () => {
  it('debounces search, selects a candidate, then invalidates it on edit', async () => {
    vi.useFakeTimers();
    vi.mocked(api.get).mockResolvedValue({ candidates: [{ name: 'London, UK', lat: 51.51, lon: -0.13 }] });
    const onSelect = vi.fn();
    const onInvalidate = vi.fn();
    render(WeatherLocationPicker, { props: { onSelect, onInvalidate } });
    const input = screen.getByRole('textbox');
    await fireEvent.input(input, { target: { value: 'Lon' } });
    await vi.advanceTimersByTimeAsync(499);
    expect(api.get).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1);
    await tick();
    expect(api.get).toHaveBeenCalledTimes(1);
    await fireEvent.click(screen.getByRole('button', { name: 'London, UK' }));
    expect(onSelect).toHaveBeenCalledWith({ locationName: 'London, UK', lat: 51.51, lon: -0.13 });
    await fireEvent.input(input, { target: { value: 'Lond' } });
    expect(onInvalidate).toHaveBeenCalledTimes(2);
  });

  it('ignores an older search response and shows empty results', async () => {
    vi.useFakeTimers();
    let finishOld!: (value: unknown) => void;
    vi.mocked(api.get).mockImplementationOnce(() => new Promise((resolve) => { finishOld = resolve; }))
      .mockResolvedValueOnce({ candidates: [] });
    render(WeatherLocationPicker);
    const input = screen.getByRole('textbox');
    await fireEvent.input(input, { target: { value: 'Old' } });
    await vi.advanceTimersByTimeAsync(500);
    await fireEvent.input(input, { target: { value: 'New' } });
    await vi.advanceTimersByTimeAsync(500);
    await tick();
    expect(screen.getByText('No places found.')).toBeInTheDocument();
    finishOld({ candidates: [{ name: 'Old City', lat: 1, lon: 2 }] });
    await tick();
    expect(screen.queryByText('Old City')).toBeNull();
  });

  it('shows provider failure and never searches after destruction', async () => {
    vi.useFakeTimers();
    vi.mocked(api.get).mockRejectedValue(new Error('offline'));
    const view = render(WeatherLocationPicker);
    await fireEvent.input(screen.getByRole('textbox'), { target: { value: 'Paris' } });
    await vi.advanceTimersByTimeAsync(500);
    await tick();
    expect(screen.getByRole('alert')).toHaveTextContent('temporarily unavailable');
    await fireEvent.input(screen.getByRole('textbox'), { target: { value: 'Berlin' } });
    view.unmount();
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('passes AbortSignal to the API client during a search and aborts on overlap', async () => {
    vi.useFakeTimers();
    let abortSignal!: AbortSignal;
    vi.mocked(api.get).mockImplementationOnce((url, options) => {
      abortSignal = (options as RequestInit).signal as AbortSignal;
      return new Promise(() => {}); // hang
    });
    render(WeatherLocationPicker);
    const input = screen.getByRole('textbox');
    await fireEvent.input(input, { target: { value: 'First' } });
    await vi.advanceTimersByTimeAsync(500);
    expect(api.get).toHaveBeenCalledTimes(1);
    expect(abortSignal).toBeDefined();
    expect(abortSignal.aborted).toBe(false);
    
    await fireEvent.input(input, { target: { value: 'Second' } });
    await vi.advanceTimersByTimeAsync(500);
    expect(abortSignal.aborted).toBe(true);
  });
});

describe('WeatherLocationPicker - Device Location', () => {
  it('does not call geolocation on render', () => {
    render(WeatherLocationPicker);
    expect(requestApproximateDeviceLocation).not.toHaveBeenCalled();
  });

  it('calls geolocation exactly once on click, prevents duplicate calls while pending, and passes rounded coords', async () => {
    let finishGeo!: (value: { locationName: string, lat: number, lon: number }) => void;
    vi.mocked(requestApproximateDeviceLocation).mockImplementationOnce(() => new Promise((resolve) => { finishGeo = resolve; }));
    const onSelect = vi.fn();
    
    render(WeatherLocationPicker, { props: { onSelect } });
    const button = screen.getByRole('button', { name: 'Use approximate device location' });
    
    await fireEvent.click(button);
    expect(requestApproximateDeviceLocation).toHaveBeenCalledTimes(1);
    expect(button).toBeDisabled();
    
    await fireEvent.click(button); // second click
    expect(requestApproximateDeviceLocation).toHaveBeenCalledTimes(1); // still 1
    
    finishGeo({ locationName: 'Approximate device location', lat: 12.34, lon: 56.78 });
    await tick();
    await tick();
    
    expect(onSelect).toHaveBeenCalledWith({ locationName: 'Approximate device location', lat: 12.34, lon: 56.78 });
  });

  it('shows permission denied in an alert', async () => {
    vi.mocked(requestApproximateDeviceLocation).mockRejectedValueOnce(new Error('Location permission was denied.'));
    render(WeatherLocationPicker);
    const button = screen.getByRole('button', { name: 'Use approximate device location' });
    await fireEvent.click(button);
    await tick();
    await tick();
    expect(screen.getByRole('alert')).toHaveTextContent('Location permission was denied.');
  });

  it('shows timeout in an alert', async () => {
    vi.mocked(requestApproximateDeviceLocation).mockRejectedValueOnce(new Error('Device location timed out.'));
    render(WeatherLocationPicker);
    const button = screen.getByRole('button', { name: 'Use approximate device location' });
    await fireEvent.click(button);
    await tick();
    await tick();
    expect(screen.getByRole('alert')).toHaveTextContent('Device location timed out.');
  });

  it('shows unavailable in an alert', async () => {
    vi.mocked(requestApproximateDeviceLocation).mockRejectedValueOnce(new Error('Device location is unavailable.'));
    render(WeatherLocationPicker);
    const button = screen.getByRole('button', { name: 'Use approximate device location' });
    await fireEvent.click(button);
    await tick();
    await tick();
    expect(screen.getByRole('alert')).toHaveTextContent('Device location is unavailable.');
  });

  it('cancels pending place search and clears candidates on successful device selection', async () => {
    vi.useFakeTimers();
    let finishSearch!: (value: { candidates: Array<{name: string, lat: number, lon: number}> }) => void;
    vi.mocked(api.get).mockImplementationOnce(() => new Promise((resolve) => { finishSearch = resolve; }));
    
    render(WeatherLocationPicker);
    const input = screen.getByRole('textbox');
    await fireEvent.input(input, { target: { value: 'City' } });
    await vi.advanceTimersByTimeAsync(500);
    expect(api.get).toHaveBeenCalledTimes(1);
    
    // Now trigger device location
    vi.mocked(requestApproximateDeviceLocation).mockResolvedValueOnce({ locationName: 'Approx', lat: 1, lon: 1 });
    const button = screen.getByRole('button', { name: 'Use approximate device location' });
    await fireEvent.click(button);
    await tick();
    await tick();
    
    // Search resolves but candidates shouldn't show because device selection cancelled it
    finishSearch({ candidates: [{ name: 'City', lat: 10, lon: 10 }] });
    await tick();
    
    expect(screen.queryByText('City')).toBeNull();
  });

  it('requires a new explicit click for another permission request', async () => {
    vi.mocked(requestApproximateDeviceLocation).mockRejectedValueOnce(new Error('denied'));
    render(WeatherLocationPicker);
    const button = screen.getByRole('button', { name: 'Use approximate device location' });
    
    await fireEvent.click(button);
    await tick();
    await tick();
    expect(screen.getByRole('alert')).toBeInTheDocument();
    
    vi.mocked(requestApproximateDeviceLocation).mockResolvedValueOnce({ locationName: 'Approx', lat: 1, lon: 1 });
    expect(requestApproximateDeviceLocation).toHaveBeenCalledTimes(1);
    
    await fireEvent.click(button);
    expect(requestApproximateDeviceLocation).toHaveBeenCalledTimes(2);
  });
});
