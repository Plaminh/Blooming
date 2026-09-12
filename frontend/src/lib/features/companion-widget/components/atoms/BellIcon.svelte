<script lang="ts">
  type Props = {
    class?: string;
  };

  let { class: className = "" }: Props = $props();
</script>

<svg
  class={className}
  width="35"
  height="40"
  viewBox="0 0 35 40"
  aria-hidden="true"
  focusable="false"
>
  <path
    d="M15 3 H20 V7 C26 8 29 13 29 20 V27 H33 V32 H2 V27 H6 V20 C6 13 9 8 15 7 Z"
    fill="#ffcc59"
    stroke="#173754"
    stroke-width="2.5"
    stroke-linejoin="miter"
  />
  <path d="M2 27 H33 V32 H2 Z" fill="#e09a22" stroke="#173754" stroke-width="2.5" />
  <path d="M13 33 H22 V36 L19 39 H16 L13 36 Z" fill="#ffcc59" stroke="#173754" stroke-width="2" />
</svg>
