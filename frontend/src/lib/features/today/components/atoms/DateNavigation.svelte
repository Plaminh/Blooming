<script lang="ts">
  let { onDateChange }: { onDateChange: (offset: number) => void } = $props();
</script>

<div class="date-navigator">
  <button class="nav-button" onclick={() => onDateChange(-1)} aria-label="Previous day">
    <span class="chevron previous" aria-hidden="true"></span>
  </button>
  <button class="today-button" onclick={() => onDateChange(0)}>Today</button>
  <button class="nav-button" onclick={() => onDateChange(1)} aria-label="Next day">
    <span class="chevron next" aria-hidden="true"></span>
  </button>
</div>

<style>
  .date-navigator {
    display: flex;
    align-items: center;
    gap: 9px;
  }

  button {
    display: grid;
    height: 46px;
    place-items: center;
    border: 1px solid #aaa79f;
    border-radius: 5px;
    background: var(--bloom-action-secondary-bg);
    box-shadow: inset 0 -1px 0 #d4cec0;
    color: #064a9c;
    cursor: pointer;
  }

  button:hover { background: #fffefa; }
  button:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
  .nav-button { width: 46px; padding: 0; }
  .today-button {
    width: 130px;
    font-family: var(--bloom-body-font);
    font-size: 18px;
    font-weight: 700;
  }

  .chevron {
    width: 13px;
    height: 13px;
    border-top: 3px solid currentColor;
    border-right: 3px solid currentColor;
  }

  .previous { transform: rotate(-135deg) translate(-1px, -1px); }
  .next { transform: rotate(45deg) translate(-1px, 1px); }
</style>
