<script lang="ts">
  import type { ReminderItem } from "../../types/presentation";
  import BellIcon from "../atoms/BellIcon.svelte";

  type Props = {
    reminders: ReminderItem[];
  };

  let { reminders }: Props = $props();

  let heading = $derived(
    reminders.length === 1 ? "1 REMINDER" : `${reminders.length} REMINDERS`,
  );
  let visible = $derived(reminders.slice(0, 2));
  let extra = $derived(Math.max(0, reminders.length - 2));
</script>

<section class="panel" aria-label="Reminders">
  <header class="head">
    <BellIcon />
    <h2>{heading}</h2>
  </header>
  <ul>
    {#each visible as item (item.id)}
      <li title={item.label}>
        <span class="bullet" aria-hidden="true"></span>
        <span class="label">{item.label}</span>
      </li>
    {/each}
  </ul>
  {#if extra > 0}
    <p class="more">+{extra} more</p>
  {/if}
</section>

<style>
  .panel {
    position: relative;
    width: 100%;
    height: 100%;
    padding: 8px 18px 8px 30px;
    border: var(--widget-stroke, 4px) solid var(--widget-navy, #0e3052);
    border-radius: var(--widget-radius, 4px);
    background: var(--widget-cream, #faefd5);
  }

  .panel::before,
  .panel::after {
    content: "";
    position: absolute;
    clip-path: polygon(0 100%, 38% 0, 100% 0);
  }

  .panel::before {
    left: -12px;
    bottom: -24px;
    width: 40px;
    height: 29px;
    background: var(--widget-navy, #0e3052);
  }

  .panel::after {
    left: -5px;
    bottom: -15px;
    width: 29px;
    height: 21px;
    background: var(--widget-cream, #faefd5);
  }

  .head {
    display: flex;
    align-items: center;
    gap: 17px;
    min-height: 40px;
  }

  .head :global(svg) {
    width: 35px;
    height: 40px;
    flex: 0 0 35px;
  }

  h2 {
    margin: 0;
    color: var(--widget-heading, #213d59);
    font-size: 23px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 0.015em;
  }

  ul {
    display: grid;
    gap: 2px;
    margin: 2px 0 0 8px;
    padding: 0;
    list-style: none;
  }

  li {
    display: flex;
    align-items: center;
    gap: 22px;
    min-height: 24px;
  }

  .bullet {
    width: 8px;
    height: 8px;
    flex: 0 0 8px;
    border: 1px solid var(--widget-bullet-stroke, #708291);
    border-radius: 50%;
    background: var(--widget-bullet, #0e3052);
  }

  .label {
    overflow: hidden;
    color: var(--widget-item, #445d73);
    font-size: 20px;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.025em;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .more {
    position: absolute;
    right: 12px;
    bottom: 3px;
    margin: 0;
    color: var(--widget-item-alt, #435c72);
    font-size: 10px;
    font-weight: 700;
  }
</style>
