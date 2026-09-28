<script lang="ts">
  import { deviceTimezone } from '$lib/shared/deviceLocation';
  import { normalizeTimezone, supportedTimezones } from '$lib/shared/timezones';
  let { id, value = $bindable(), disabled = false, describedby, error }: { id: string; value: string; disabled?: boolean; describedby?: string; error?: string | null } = $props();
  const zones = supportedTimezones();
  let query = $state(value);
  let open = $state(false);
  let activeIndex = $state(0);
  const normalizedQuery = $derived(query.trim().toLowerCase().replace(/[\s_-]+/g, ''));
  const filterQuery = $derived(open && query === value ? '' : normalizedQuery);
  const matches = $derived(zones.filter((zone) => zone.toLowerCase().replace(/[\s_-]+/g, '').includes(filterQuery)));
  function select(zone: string) { value = zone; query = zone; open = false; }
  function useSystemTimezone() { select(normalizeTimezone(deviceTimezone())); }
  function handleInput(event: Event) { query = (event.target as HTMLInputElement).value; open = true; activeIndex = 0; }
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') { event.preventDefault(); event.stopPropagation(); if (open && matches[activeIndex]) select(matches[activeIndex]); }
    else if (event.key === 'ArrowDown') { event.preventDefault(); open = true; activeIndex = Math.min(activeIndex + 1, matches.length - 1); }
    else if (event.key === 'ArrowUp') { event.preventDefault(); activeIndex = Math.max(activeIndex - 1, 0); }
    else if (event.key === 'Escape') { open = false; query = value; }
  }
  function handleBlur() { setTimeout(() => { open = false; query = value; }, 100); }
</script>

<div class="timezone-picker">
  <input {id} class="timezone-input" type="text" role="combobox" value={query} aria-expanded={open}
    aria-controls={`${id}-options`} aria-autocomplete="list"
    aria-activedescendant={open && matches[activeIndex] ? `${id}-option-${activeIndex}` : undefined}
    {disabled} aria-describedby={describedby} aria-invalid={error ? 'true' : undefined}
    autocomplete="off" onfocus={() => (open = true)} onblur={handleBlur} oninput={handleInput} onkeydown={handleKeydown} />
  {#if open && matches.length > 0}
    <ul id={`${id}-options`} class="timezone-options" role="listbox" data-scrollable="true">
      {#each matches as zone, index}
        <li id={`${id}-option-${index}`} role="option" aria-selected={zone === value} class:active={index === activeIndex}>
          <button type="button" onmousedown={(event) => event.preventDefault()} onclick={() => select(zone)}>{zone}</button>
        </li>
      {/each}
    </ul>
  {/if}
  <button class="system-timezone" type="button" onclick={useSystemTimezone} {disabled}>Use system timezone</button>
</div>

<style>
  .timezone-picker { position: relative; }
  .timezone-input { box-sizing: border-box; width: 100%; min-height: 42px; padding: 0 14px; border: 1px solid var(--bloom-border-subtle); border-radius: var(--bloom-radius); background: var(--bloom-surface-cream-alt); color: var(--bloom-text-control-blue); font: 19px var(--bloom-body-font); }
  .timezone-input:focus-visible, button:focus-visible { outline: 2px solid #2d7c59; outline-offset: 2px; }
  .timezone-options { position: absolute; z-index: 20; top: 43px; right: 0; left: 0; max-height: min(280px, 45vh); margin: 0; padding: 4px; overflow-y: auto; overscroll-behavior: contain; scrollbar-color: var(--bloom-border-dark) var(--bloom-surface-cream-alt); scrollbar-width: thin; border: 1px solid var(--bloom-border-dark); border-radius: var(--bloom-radius); background: var(--bloom-surface-cream-alt); box-shadow: 0 4px 10px rgb(0 0 0 / 18%); list-style: none; }
  .timezone-options::-webkit-scrollbar { width: 9px; }
  .timezone-options::-webkit-scrollbar-thumb { border: 2px solid var(--bloom-surface-cream-alt); border-radius: 8px; background: var(--bloom-border-dark); }
  .timezone-options button { width: 100%; padding: 7px 10px; border: 0; background: transparent; color: var(--bloom-text-control-blue); text-align: left; cursor: pointer; }
  .timezone-options li.active button, .timezone-options button:hover { background: rgb(101 168 113 / 20%); }
  .system-timezone { margin-top: 6px; padding: 5px 10px; border: 1px solid var(--bloom-border-dark); border-radius: var(--bloom-radius); background: var(--bloom-surface-dark-cream); color: var(--bloom-text-control-blue); cursor: pointer; font-weight: 600; }
</style>
