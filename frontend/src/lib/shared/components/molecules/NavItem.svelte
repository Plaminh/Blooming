<script lang="ts">
  import { page } from "$app/state";

  type Props = {
    href: string;
    label: string;
  };

  let { href, label }: Props = $props();

  const active = $derived(page.url.pathname === href);
</script>

<a {href} class="nav-item" class:active aria-current={active ? "page" : undefined}>
  {label}
</a>

<style>
  .nav-item {
    display: inline-flex;
    text-decoration: none;
    border-radius: var(--radius);
    padding: var(--space-2) var(--space-3);
    color: var(--color-muted);
    font-size: 0.875rem;
    letter-spacing: 0.02em;
  }

  .nav-item.active {
    background: var(--color-surface);
    box-shadow: inset 0 0 0 1px var(--color-border);
  }
</style>
