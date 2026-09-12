<script lang="ts">
  type Props = {
    class?: string;
  };

  let { class: className = "" }: Props = $props();
</script>

<svg
  class={className}
  width="52"
  height="44"
  viewBox="0 0 52 44"
  aria-hidden="true"
  focusable="false"
>
  <path d="M7 5 H39 L47 13 V31 L39 39 H7 L1 31 V13 Z" fill="#fffdf5" />
  <path
    d="M11 19 Q26 5 41 19"
    fill="none"
    stroke="#526a78"
    stroke-width="4"
    stroke-linecap="square"
  />
  <path
    d="M17 25 Q26 17 35 25"
    fill="none"
    stroke="#526a78"
    stroke-width="4"
    stroke-linecap="square"
  />
  <rect x="24" y="29" width="5" height="5" fill="#526a78" />
  <path d="M36 28 L48 40 M48 28 L36 40" stroke="#ef4343" stroke-width="4" />
</svg>
