<script lang="ts">
  import type { FocusPreset } from '$lib/features/today/types';
  let {
    preset, label, focusTime, breakTime, selected, onSelect
  }: {
    preset: FocusPreset;
    label: string;
    focusTime: string;
    breakTime: string;
    selected: boolean;
    onSelect: (preset: FocusPreset) => void;
  } = $props();
</script>

<button class="preset" class:selected onclick={() => onSelect(preset)} aria-pressed={selected}>
  <span class="preset-box">{label}</span>
  <span class="detail">{focusTime}</span>
  <span class="detail">{breakTime}</span>
</button>

<style>
  .preset {
    display: flex;
    min-width: 0;
    flex: 1;
    flex-direction: column;
    align-items: center;
    padding: 0;
    border: 0;
    background: transparent;
    color: #0750a1;
    font-family: var(--bloom-body-font);
    cursor: pointer;
  }
  .preset:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
  .preset-box {
    display: grid;
    width: 100%;
    height: 40px;
    place-items: center;
    margin-bottom: 5px;
    border: 1px solid #aaa69d;
    border-radius: 4px;
    background: linear-gradient(#fffdf7, #f1ebdd);
    box-shadow: inset 0 -1px 0 #d9d1c1;
    font-size: 17px;
    font-weight: 700;
  }
  .selected .preset-box {
    border-color: #177f4b;
    background: linear-gradient(#4cac6a, #269551);
    color: #f0f8ed;
  }
  .detail { font-size: 13px; line-height: 1.35; white-space: nowrap; }
</style>
