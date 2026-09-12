<script lang="ts">
  import { onMount } from "svelte";
  import WindowControlButton from "../atoms/WindowControlButton.svelte";

  type WindowHandle = {
    minimize: () => Promise<void>;
    toggleMaximize: () => Promise<void>;
    close: () => Promise<void>;
  };

  let windowHandle: WindowHandle | null = $state(null);

  onMount(() => {
    let cancelled = false;
    void import("@tauri-apps/api/window")
      .then(({ getCurrentWindow }) => {
        if (!cancelled) {
          windowHandle = getCurrentWindow();
        }
      })
      .catch(() => {
        windowHandle = null;
      });
    return () => {
      cancelled = true;
    };
  });

  async function runWindowAction(action: keyof WindowHandle) {
    try {
      await windowHandle?.[action]();
    } catch {
      // Browser preview and unsupported host APIs intentionally no-op.
    }
  }

  function minimize() {
    void runWindowAction("minimize");
  }

  function toggleMaximize() {
    void runWindowAction("toggleMaximize");
  }

  function closeWindow() {
    void runWindowAction("close");
  }
</script>

<header class="title-bar">
  <div class="drag" data-tauri-drag-region>
    <span class="logo" data-tauri-drag-region>
      <img
        src="/assets/widget/icons/leaf-icon.png"
        alt=""
        width="40"
        height="40"
        data-tauri-drag-region
      />
    </span>
    <p class="brand" data-tauri-drag-region>BLOOMING</p>
  </div>
  <div class="controls">
    <WindowControlButton kind="minimize" label="Minimize" onclick={minimize} />
    <WindowControlButton kind="maximize" label="Maximize or restore" onclick={toggleMaximize} />
    <WindowControlButton kind="close" label="Close" onclick={closeWindow} />
  </div>
</header>

<style>
  .title-bar {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    z-index: 3;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: var(--widget-title-height, 61px);
    padding: 0;
    border-bottom: 3px solid var(--widget-navy, #0e3052);
    background: var(--widget-title-bar, #387b99);
  }

  .drag {
    display: flex;
    flex: 1;
    align-items: center;
    min-width: 0;
    height: 100%;
  }

  .logo {
    position: absolute;
    top: 1px;
    left: 9px;
    display: grid;
    place-items: center;
    width: 28px;
    height: 31px;
    padding: 0;
  }

  .logo img {
    display: block;
    width: 40px;
    height: 40px;
    object-fit: contain;
    image-rendering: crisp-edges;
    image-rendering: pixelated;
  }

  .brand {
    margin: 0 0 0 60px;
    color: var(--widget-title, #d5e2e9);
    font-family: var(--widget-font, monospace);
    font-size: 23px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 0.07em;
    text-shadow: 1px 1px 0 #1c5873;
  }

  .controls {
    position: absolute;
    top: 12px;
    left: 548px;
    display: flex;
    align-items: center;
    gap: 7px;
    margin: 0;
  }
</style>
