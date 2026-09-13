<script lang="ts">
  let { checked, label, onChange }: { checked: boolean, label: string, onChange: (val: boolean) => void } = $props();
</script>

<label class="auth-checkbox-wrapper">
  <input
    class="auth-checkbox-input"
    type="checkbox"
    {checked}
    onchange={(event) => onChange(event.currentTarget.checked)}
  />
  <span class="auth-checkbox" aria-hidden="true"></span>
  <span class="auth-checkbox-label">{label}</span>
</label>
