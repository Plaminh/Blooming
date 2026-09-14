<script lang="ts">
  import iconAtlasUrl from '../../../../../../../design-assets/app/references/today.png?url';

  type IconName =
    | 'today'
    | 'goals'
    | 'chat'
    | 'settings'
    | 'book'
    | 'break'
    | 'document'
    | 'shoe'
    | 'calendar'
    | 'event'
    | 'category'
    | 'notes'
    | 'pencil'
    | 'replan'
    | 'water'
    | 'sprout';

  const crops: Record<IconName, { x: number; y: number; width: number; height: number }> = {
    today: { x: 20, y: 96, width: 37, height: 37 },
    goals: { x: 21, y: 171, width: 38, height: 43 },
    chat: { x: 18, y: 254, width: 43, height: 43 },
    settings: { x: 19, y: 332, width: 42, height: 42 },
    book: { x: 376, y: 207, width: 53, height: 48 },
    break: { x: 379, y: 296, width: 48, height: 58 },
    document: { x: 379, y: 402, width: 45, height: 58 },
    shoe: { x: 375, y: 510, width: 66, height: 58 },
    calendar: { x: 1062, y: 344, width: 30, height: 31 },
    event: { x: 1096, y: 381, width: 34, height: 35 },
    category: { x: 1081, y: 224, width: 34, height: 33 },
    notes: { x: 1082, y: 269, width: 31, height: 35 },
    pencil: { x: 516, y: 891, width: 40, height: 39 },
    replan: { x: 756, y: 893, width: 43, height: 39 },
    water: { x: 109, y: 894, width: 31, height: 42 },
    sprout: { x: 1091, y: 905, width: 36, height: 42 }
  };

  let { name, scale = 0.9, label }: { name: IconName; scale?: number; label?: string } = $props();

  const crop = $derived(crops[name]);
  const style = $derived(
    `--crop-x:${crop.x * scale}px;--crop-y:${crop.y * scale}px;` +
      `--crop-w:${crop.width * scale}px;--crop-h:${crop.height * scale}px;` +
      `--atlas-w:${1534 * scale}px;--atlas-h:${968 * scale}px;--atlas-url:url("${iconAtlasUrl}");`
  );
</script>

<span class="today-icon" {style} role={label ? 'img' : undefined} aria-label={label}></span>

<style>
  .today-icon {
    display: inline-block;
    width: var(--crop-w);
    height: var(--crop-h);
    flex: 0 0 auto;
    overflow: hidden;
    background-image: var(--atlas-url);
    background-repeat: no-repeat;
    background-position: calc(-1 * var(--crop-x)) calc(-1 * var(--crop-y));
    background-size: var(--atlas-w) var(--atlas-h);
    image-rendering: pixelated;
  }
</style>
