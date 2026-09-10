<script lang="ts">
  import { NavItem } from "$lib/shared/components/molecules";
  import type { AppNavItem } from "$lib/shared/types";

  const items: AppNavItem[] = [
    { href: "/", label: "Today" },
    { href: "/goals", label: "Goals" },
    { href: "/settings", label: "Settings" },
  ];
</script>

<nav class="app-nav" aria-label="Main">
  {#each items as item (item.href)}
    <NavItem href={item.href} label={item.label} />
  {/each}
</nav>

<style>
  .app-nav {
    display: flex;
    gap: var(--space-2);
  }
</style>
