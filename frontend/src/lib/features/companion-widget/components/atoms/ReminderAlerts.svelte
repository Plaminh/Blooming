<script lang="ts">
  type Props = {
    class?: string;
  };

  let { class: className = "" }: Props = $props();
</script>

<svg
  class={className}
  width="22"
  height="26"
  viewBox="0 0 22 26"
  aria-hidden="true"
  focusable="false"
>
  <path
    d="M7 22 L9.5 4"
    fill="none"
    stroke="#f08ab4"
    stroke-width="3"
    stroke-linecap="round"
  />
  <path
    d="M15 23 L18.5 3"
    fill="none"
    stroke="#f08ab4"
    stroke-width="3.2"
    stroke-linecap="round"
  />
</svg>
