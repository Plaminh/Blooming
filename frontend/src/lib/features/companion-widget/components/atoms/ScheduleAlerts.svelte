<script lang="ts">
  type Props = {
    class?: string;
  };

  let { class: className = "" }: Props = $props();
</script>

<svg
  class={className}
  width="38"
  height="31"
  viewBox="0 0 38 31"
  aria-hidden="true"
  focusable="false"
>
  <path
    d="M19 16 V3"
    fill="none"
    stroke="#f5b942"
    stroke-width="5"
    stroke-linecap="square"
  />
  <path
    d="M10 24 L3 17"
    fill="none"
    stroke="#f5b942"
    stroke-width="4"
    stroke-linecap="square"
  />
  <path
    d="M28 24 L35 17"
    fill="none"
    stroke="#f5b942"
    stroke-width="4"
    stroke-linecap="square"
  />
</svg>
