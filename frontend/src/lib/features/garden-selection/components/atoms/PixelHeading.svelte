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
    color: #1e3a5f;
    margin-bottom: 2rem;
  }
  h1 {
    font-family: var(--bloom-display-font);
    font-size: 40px;
    margin: 0;
    text-transform: uppercase;
  }
  p {
    font-family: var(--bloom-body-font);
    font-size: 18px;
    margin: 8px 0 0 0;
  }
</style>
