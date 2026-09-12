<script lang="ts">
  import { WIDGET_SCENE } from "../../model/atlas";

  type Props = {
    class?: string;
  };

  let { class: className = "" }: Props = $props();
</script>

<div
  class="scene {className}"
  aria-hidden="true"
  style:--frame-w="{WIDGET_SCENE.frameWidth}px"
  style:--frame-h="{WIDGET_SCENE.frameHeight}px"
  style:--bushes-w="{WIDGET_SCENE.bushesWidth}px"
  style:--bushes-h="{WIDGET_SCENE.bushesHeight}px"
>
  <div class="frame">
    <img class="sky" src={WIDGET_SCENE.skySrc} alt="" width={WIDGET_SCENE.frameWidth} height={WIDGET_SCENE.frameHeight} />
    <img
      class="bushes"
      src={WIDGET_SCENE.bushesSrc}
      alt=""
      width={WIDGET_SCENE.bushesWidth}
      height={WIDGET_SCENE.bushesHeight}
    />
  </div>
</div>

<style>
  .scene {
    position: absolute;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
  }

  .scene::after {
    content: "";
    position: absolute;
    right: 0;
    bottom: 3px;
    left: 0;
    height: 13px;
    border-top: 3px solid #b59b71;
    background: #f0d9ac;
  }

  .frame {
    position: absolute;
    left: 0;
    bottom: -40px;
    width: var(--frame-w);
    height: var(--frame-h);
    overflow: hidden;
    transform-origin: left bottom;
    /* Keep both source layers on one coordinate system and shift the
       shared crop down to match the low foreground in the references. */
    transform: scale(0.361702128);
  }

  .sky,
  .bushes {
    position: absolute;
    left: 0;
    bottom: 0;
    max-width: none;
    image-rendering: crisp-edges;
    image-rendering: pixelated;
  }

  .sky {
    width: var(--frame-w);
    height: var(--frame-h);
  }

  .bushes {
    width: var(--bushes-w);
    height: var(--bushes-h);
  }
</style>
