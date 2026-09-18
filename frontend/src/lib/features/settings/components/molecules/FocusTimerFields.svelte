<script lang="ts">
  import SelectField from '../atoms/SelectField.svelte';

  let {
    focusMinutes = $bindable(),
    breakMinutes = $bindable(),
    focusError,
    breakError,
    idPrefix = 'settings',
  }: {
    focusMinutes: number;
    breakMinutes: number;
    focusError?: string;
    breakError?: string;
    idPrefix?: string;
  } = $props();

  let focusOptions = $derived(
    [...new Set([5, 10, 15, 20, 25, 30, 45, 50, 60, focusMinutes])]
      .sort((a, b) => a - b)
      .map((value) => ({ value, label: `${value} minutes` })),
  );
  let breakOptions = $derived(
    [...new Set([5, 10, 15, 20, breakMinutes])]
      .sort((a, b) => a - b)
      .map((value) => ({ value, label: `${value} minutes` })),
  );
</script>

<SelectField
  id={`${idPrefix}-focus-duration`}
  label="Focus duration"
  bind:value={focusMinutes}
  options={focusOptions}
  error={focusError}
/>

<SelectField
  id={`${idPrefix}-break-duration`}
  label="Break duration"
  bind:value={breakMinutes}
  options={breakOptions}
  error={breakError}
/>
