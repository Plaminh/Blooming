<script lang="ts">
  import AuthenticationIcon from './AuthenticationIcon.svelte';

  let { visible, onToggle }: { visible: boolean, onToggle: () => void } = $props();
</script>

<button 
  type="button" 
  class="visibility-toggle" 
  aria-label={visible ? "Hide password" : "Show password"}
  onclick={onToggle}
>
  <AuthenticationIcon name={visible ? 'eye-off' : 'eye'} size={20} color="var(--auth-text-muted-blue-alt)" />
</button>
