<script lang="ts">
  let { title, subtitle }: { title: string; subtitle: string } = $props();
</script>

<div class="pixel-heading">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>

<style>
  .pixel-heading {
    text-align: center;
    color: var(--bloom-text-dark-blue);
    margin-bottom: 8px;
  }
  h1 {
    font-family: var(--bloom-display-font);
    font-size: 40px;
    margin: 0;
    text-transform: uppercase;
  }
  p {
    font-family: var(--bloom-body-font);
    font-size: 20px;
    margin: 0;
  }
</style>
