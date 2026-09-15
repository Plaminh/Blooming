<script lang="ts">
  import type { HTMLInputAttributes } from 'svelte/elements';
  import AuthenticationIcon from '../atoms/AuthenticationIcon.svelte';
  import PasswordVisibilityButton from '../atoms/PasswordVisibilityButton.svelte';

  let { 
    id,
    label,
    value = $bindable(),
    placeholder = "Your password",
    visible = false,
    onToggleVisibility,
    errorId = undefined,
    invalid = false,
    autocomplete = "current-password",
    oninput,
  }: { 
    id: string;
    label: string;
    value: string;
    placeholder?: string;
    visible: boolean;
    onToggleVisibility: () => void;
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
      <div class="input-icon">
        <AuthenticationIcon name="lock" size={22} color="var(--bloom-text-muted-blue)" />
      </div>
      <input 
        {id}
        type={visible ? "text" : "password"}
        bind:value
        {placeholder}
        {autocomplete}
        {oninput}
        class="auth-input"
        aria-invalid={invalid ? 'true' : undefined}
        aria-errormessage={invalid ? errorId : undefined}
        aria-describedby={invalid ? errorId : undefined}
      />
      <div class="visibility-control">
        <PasswordVisibilityButton {visible} onToggle={onToggleVisibility} />
      </div>
    </div>
  </div>
</div>
