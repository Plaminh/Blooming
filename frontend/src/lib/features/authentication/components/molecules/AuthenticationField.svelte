<script lang="ts">
  import type { HTMLInputAttributes } from 'svelte/elements';
  import AuthenticationIcon from '../atoms/AuthenticationIcon.svelte';

  let { 
    id,
    label,
    value = $bindable(),
    type = "text",
    placeholder = "",
    iconName,
    errorId = undefined,
    invalid = false,
    autocomplete = "off",
    oninput,
  }: { 
    id: string;
    label: string;
    value: string;
    type?: HTMLInputAttributes['type'];
    placeholder?: string;
    iconName?: 'email';
    errorId?: string;
    invalid?: boolean;
    autocomplete?: HTMLInputAttributes['autocomplete'];
    oninput?: (e: Event) => void;
  } = $props();
</script>

<div class="field-container">
  <label for={id} class="field-label">{label}</label>
  <div class="input-wrapper" class:invalid>
    <div class="input-inner">
      {#if iconName}
        <div class="input-icon">
          <AuthenticationIcon name={iconName} size={25} color="var(--bloom-text-muted-blue)" />
        </div>
      {/if}
      <input 
        {id}
        {type}
        bind:value
        {placeholder}
        {autocomplete}
        {oninput}
        class="auth-input"
        aria-invalid={invalid ? 'true' : undefined}
        aria-errormessage={invalid ? errorId : undefined}
        aria-describedby={invalid ? errorId : undefined}
      />
    </div>
  </div>
</div>
