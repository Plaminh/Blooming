<script lang="ts">
  let { title }: { title: string } = $props();
</script>

<h2 class="section-heading">{title}</h2>

<style>
  .section-heading {
    font-family: var(--bloom-title-font);
    font-size: 24px;
    font-weight: 700;
    color: var(--bloom-text-dark-blue);
    margin: 0;
    margin-bottom: 20px;
    text-transform: uppercase;
  }
</style>
