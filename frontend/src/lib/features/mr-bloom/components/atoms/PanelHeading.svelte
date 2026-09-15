<script lang="ts">
  let { children, variant = 'default' }: { children: import('svelte').Snippet; variant?: 'default' | 'draft' } = $props();
</script>

<h2 class="panel-heading" class:draft={variant === 'draft'}>{@render children()}</h2>

<style>
  .panel-heading {
    color: #071f66;
    font-family: var(--bloom-display-font);
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.055em;
    line-height: 1.15;
  }

  .panel-heading.draft {
    font-size: 38px;
    line-height: 1;
  }
</style>
