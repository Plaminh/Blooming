<script lang="ts">
  type Props = {
    class?: string;
  };

  let { class: className = "" }: Props = $props();
</script>

<svg
  class={className}
  width="12"
  height="12"
  viewBox="0 0 12 12"
  aria-hidden="true"
  focusable="false"
>
  <rect x="2" y="2" width="8" height="8" rx="0.5" fill="currentColor" />
</svg>
