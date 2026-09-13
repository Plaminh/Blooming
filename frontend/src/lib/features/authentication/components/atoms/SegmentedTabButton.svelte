<script lang="ts">
  let { active, label, onClick }: { active: boolean, label: string, onClick: () => void } = $props();
</script>

<button 
  type="button" 
  class="segmented-tab" 
  class:active 
  aria-pressed={active}
  onclick={onClick}
>
  <span class="inner-tab">
    {label}
  </span>
</button>
