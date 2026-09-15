<script lang="ts">
  let { title }: { title: string } = $props();
</script>

<h2 class="section-heading">{title}</h2>

<style>
  .section-heading {
    font-family: var(--bloom-display-font);
    font-size: 46px;
    font-weight: 900;
    letter-spacing: -0.06em;
    line-height: 1;
    text-shadow: 1px 0 currentColor;
    color: var(--bloom-text-dark-blue);
    margin: 0;
    margin-bottom: 24px;
    text-transform: uppercase;
  }
</style>
