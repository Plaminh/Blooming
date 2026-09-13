<script lang="ts">
  let { id, message }: { id: string; message: string | undefined } = $props();
</script>

{#if message}
  <div {id} class="validation-message" role="alert">
    {message}
  </div>
{/if}
