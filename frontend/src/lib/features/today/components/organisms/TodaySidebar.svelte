<script lang="ts">
  import PlantSprite from '$lib/features/companion-widget/components/atoms/PlantSprite.svelte';
  import TodayIcon from '../atoms/TodayIcon.svelte';
  import SidebarNavigationItem from '../molecules/SidebarNavigationItem.svelte';
</script>

<div class="sidebar">
  <nav class="sidebar-nav" aria-label="Primary navigation">
    <SidebarNavigationItem label="TODAY" icon="today" active />
    <SidebarNavigationItem label="GOALS" icon="goals" />
    <SidebarNavigationItem label="MR. BLOOM" icon="chat" />
    <SidebarNavigationItem label="SETTINGS" icon="settings" />
  </nav>

  <div class="sidebar-bottom">
    <div class="plant-container">
      <PlantSprite plant={{ species: 'monstera', frameIndex: 7 }} />
    </div>
    <div class="counters" aria-label="Garden currency">
      <div class="counter">
        <img class="leaf-counter" src="/assets/widget/icons/leaf-icon.png" alt="Leaves" />
        <span>24</span>
      </div>
      <div class="counter">
        <TodayIcon name="water" scale={0.72} label="Water" />
        <span>3</span>
      </div>
    </div>
  </div>
</div>

<style>
  .sidebar {
    display: flex;
    min-width: 0;
    height: 100%;
    flex-direction: column;
    justify-content: space-between;
    padding: 25px 9px 0;
    border-right: 1px solid #cfc9b9;
    background: rgba(255, 251, 240, 0.35);
  }

  .sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 13px;
  }

  .sidebar-bottom {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-bottom: 18px;
  }

  .plant-container {
    display: grid;
    width: 126px;
    height: 188px;
    place-items: end center;
    margin-bottom: 6px;
  }

  .plant-container :global(.plant) {
    transform: scale(1.5);
    transform-origin: bottom center;
  }

  .counters {
    display: flex;
    align-items: center;
    gap: 19px;
  }

  .counter {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #064798;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 700;
  }

  .leaf-counter {
    width: 25px;
    height: 29px;
    object-fit: contain;
    image-rendering: pixelated;
  }
</style>
