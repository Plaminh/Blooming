<script lang="ts">
  import { onDestroy, untrack } from 'svelte';
  import { api } from '$lib/api';
  import { requestApproximateDeviceLocation } from '$lib/shared/deviceLocation';
  import type { PlaceCandidate, PlaceSearchResponse } from '$lib/types/weather';

  let { disabled = false, initialValue = '', onSelect = () => {}, onInvalidate = () => {} }: {
    disabled?: boolean;
    initialValue?: string;
    onSelect?: (place: { locationName: string; lat: number; lon: number }) => void;
    onInvalidate?: () => void;
  } = $props();
  let query = $state(untrack(() => initialValue));
  let candidates = $state<PlaceCandidate[]>([]);
  let isSearching = $state(false);
  let searched = $state(false);
  let error = $state('');
  let locationPending = $state(false);
  let selectedLocation = $state(untrack(() => initialValue));
  let activeIndex = $state(0);
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
      activeIndex = 0;
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
    selectedLocation = '';
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
    selectedLocation = candidate.name;
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
      selectedLocation = place.locationName;
      candidates = [];
      onSelect(place);
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Device location is unavailable.';
    } finally {
      locationPending = false;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault(); event.stopPropagation();
      if (candidates[activeIndex]) choose(candidates[activeIndex]);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault(); activeIndex = Math.min(activeIndex + 1, candidates.length - 1);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault(); activeIndex = Math.max(activeIndex - 1, 0);
    }
  }

  onDestroy(() => {
    requestId += 1;
    if (timer) clearTimeout(timer);
    active?.abort();
  });
</script>

<div class="weather-location-picker">
  <input aria-label="Search weather location" type="text" role="combobox" aria-expanded={candidates.length > 0}
    aria-controls="weather-location-options" aria-autocomplete="list" placeholder="Search for a city..."
    value={query} oninput={handleInput} onkeydown={handleKeydown} {disabled} />
  <button type="button" onclick={useDeviceLocation} disabled={disabled || locationPending}>
    {locationPending ? 'Finding location...' : 'Use approximate device location'}
  </button>
  {#if isSearching}<span role="status">Searching...</span>{/if}
  {#if error}<span role="alert">{error}</span>{/if}
  {#if searched && !isSearching && !error && candidates.length === 0}<span role="status">No places found.</span>{/if}
  {#if selectedLocation}<span class="selected-location" role="status">✓ Selected location: {selectedLocation}</span>{/if}
  {#if candidates.length > 0}
    <ul id="weather-location-options" role="listbox">
      {#each candidates as candidate, index}
        <li role="option" aria-selected={index === activeIndex} class:active={index === activeIndex}><button type="button" onclick={() => choose(candidate)}>{candidate.name}</button></li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .weather-location-picker { position: relative; display: flex; flex-direction: column; align-items: flex-start; gap: 7px; width: 100%; }
  input { box-sizing: border-box; width: 100%; height: 42px; padding: 0 14px; border: 1px solid var(--bloom-border-subtle); border-radius: var(--bloom-radius); background: var(--bloom-surface-cream-alt); color: var(--bloom-text-control-blue); font: 17px var(--bloom-body-font); }
  .weather-location-picker > button { padding: 7px 12px; border: 1px solid var(--bloom-border-dark); border-radius: var(--bloom-radius); background: var(--bloom-surface-dark-cream); color: var(--bloom-text-control-blue); cursor: pointer; font-weight: 600; }
  button:disabled { cursor: wait; opacity: .7; }
  input:focus-visible, button:focus-visible { outline: 2px solid #2d7c59; outline-offset: 2px; }
  ul { position: absolute; z-index: 20; top: 43px; right: 0; left: 0; max-height: 170px; margin: 0; padding: 4px; overflow-y: auto; border: 1px solid var(--bloom-border-dark); border-radius: var(--bloom-radius); background: var(--bloom-surface-cream-alt); box-shadow: 0 4px 10px rgb(0 0 0 / 18%); list-style: none; }
  li button { width: 100%; padding: 7px 10px; border: 0; background: transparent; color: var(--bloom-text-control-blue); text-align: left; cursor: pointer; }
  li.active button, li button:hover { background: rgb(101 168 113 / 20%); }
  [role='alert'] { color: var(--bloom-error); font-size: 14px; }
  .selected-location { color: var(--bloom-primary-green-border); font-size: 14px; font-weight: 600; }
</style>
