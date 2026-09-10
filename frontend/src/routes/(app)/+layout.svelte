<script lang="ts">
  import { AppNav } from "$lib/shared/components/organisms";

  let { children } = $props();
</script>

<div class="shell">
  <header class="top">
    <p class="brand">Blooming</p>
    <AppNav />
  </header>
  <main class="content">
    {@render children()}
  </main>
</div>

<style>
  .shell {
    min-height: 100vh;
    display: grid;
    grid-template-rows: auto 1fr;
  }

  .top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    padding: var(--space-3) var(--space-5);
    border-bottom: 1px solid var(--color-border);
    background: var(--color-surface);
  }

  .brand {
    font-weight: 600;
  }

  .content {
    padding: var(--space-5);
  }
</style>
