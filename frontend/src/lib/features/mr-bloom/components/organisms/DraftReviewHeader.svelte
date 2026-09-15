<script lang="ts">
  import PanelHeading from '../atoms/PanelHeading.svelte';

  let {
    title,
    subtitle,
    type
  }: {
    title: string;
    subtitle?: string;
    type?: string;
  } = $props();
</script>

<header class="draft-review-header">
  {#if type}<div class="type-label">LIVE DRAFT · {type}</div>{/if}
  <PanelHeading variant="draft">{title}</PanelHeading>
  {#if subtitle}<p class="subtitle">{subtitle}</p>{/if}
</header>

<style>
  .draft-review-header {
    flex: 0 0 auto;
    padding: 10px 14px 4px;
  }

  .type-label {
    margin-bottom: 5px;
    color: #78a4bd;
    font-family: var(--bloom-body-font);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.05em;
  }

  .subtitle {
    margin: 3px 0 0;
    color: #146a9b;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    line-height: 1.25;
  }
</style>
