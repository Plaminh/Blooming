<script lang="ts">
  import { onDestroy } from 'svelte';
  import { api } from '$lib/api';
  import { requestApproximateDeviceLocation } from '$lib/shared/deviceLocation';
  import type { PlaceCandidate, PlaceSearchResponse } from '$lib/types/weather';

  let { disabled = false, onSelect = () => {}, onInvalidate = () => {} }: {
    disabled?: boolean;
    onSelect?: (place: { locationName: string; lat: number; lon: number }) => void;
    onInvalidate?: () => void;
  } = $props();
  let query = $state('');
  let candidates = $state<PlaceCandidate[]>([]);
  let isSearching = $state(false);
  let searched = $state(false);
  let error = $state('');
  let locationPending = $state(false);
  let timer: ReturnType<typeof setTimeout> | null = null;
  let requestId = 0;
  let active: AbortController | null = null;

  async function search(q: string, id: number) {
    active?.abort();
    const controller = new AbortController();
    active = controller;
    isSearching = true;
    error = '';
    try {
      const result = await api.get('/weather/search?q=' + encodeURIComponent(q), { signal: controller.signal }) as PlaceSearchResponse;
      if (id !== requestId) return;
      candidates = result.candidates;
      searched = true;
    } catch {
      if (id !== requestId || controller.signal.aborted) return;
      candidates = [];
      error = 'Place search is temporarily unavailable. Try again.';
    } finally {
      if (id === requestId) isSearching = false;
    }
  }

  function handleInput(event: Event) {
    query = (event.target as HTMLInputElement).value;
    onInvalidate();
    candidates = [];
    searched = false;
    error = '';
    requestId += 1;
    active?.abort();
    if (timer) clearTimeout(timer);
    if (query.trim().length >= 2) {
      const id = requestId;
      timer = setTimeout(() => void search(query.trim(), id), 500);
    } else {
      isSearching = false;
    }
  }

  function choose(candidate: PlaceCandidate) {
    requestId += 1;
    active?.abort();
    query = candidate.name;
    candidates = [];
    searched = false;
    onSelect({ locationName: candidate.name, lat: candidate.lat, lon: candidate.lon });
  }

  async function useDeviceLocation() {
    if (locationPending) return;
    locationPending = true;
    error = '';
    try {
      const place = await requestApproximateDeviceLocation();
      requestId += 1;
      active?.abort();
      if (timer) clearTimeout(timer);
      query = place.locationName;
      candidates = [];
      onSelect(place);
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Device location is unavailable.';
    } finally {
      locationPending = false;
    }
  }

  onDestroy(() => {
    requestId += 1;
    if (timer) clearTimeout(timer);
    active?.abort();
  });
</script>

<div class="weather-location-picker">
  <input aria-label="Search weather location" type="text" placeholder="Search for a city..." value={query} oninput={handleInput} {disabled} />
  <button type="button" onclick={useDeviceLocation} disabled={disabled || locationPending}>
    {locationPending ? 'Finding location...' : 'Use approximate device location'}
  </button>
  {#if isSearching}<span role="status">Searching...</span>{/if}
  {#if error}<span role="alert">{error}</span>{/if}
  {#if searched && !isSearching && !error && candidates.length === 0}<span role="status">No places found.</span>{/if}
  {#if candidates.length > 0}
    <ul>
      {#each candidates as candidate}
        <li><button type="button" onclick={() => choose(candidate)}>{candidate.name}</button></li>
      {/each}
    </ul>
  {/if}
</div>
