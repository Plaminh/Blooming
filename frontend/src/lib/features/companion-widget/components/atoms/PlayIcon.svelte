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
  <path d="M3 2 L10 6 L3 10 Z" fill="currentColor" />
</svg>
