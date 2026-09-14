<script lang="ts">
  let {
    id,
    label,
    checked = $bindable()
  }: {
    id: string;
    label: string;
    checked: boolean;
  } = $props();
</script>

<div class="toggle-group">
  <label for={id}>{label}</label>
  <div class="toggle-switch-wrapper">
    <input type="checkbox" {id} bind:checked role="switch" aria-checked={checked} />
    <div class="toggle-track" aria-hidden="true">
      <div class="toggle-thumb"></div>
    </div>
  </div>
</div>

<style>
  .toggle-group {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  label {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    font-weight: 600;
    cursor: pointer;
  }

  .toggle-switch-wrapper {
    position: relative;
    display: inline-block;
    width: 44px;
    height: 24px;
  }

  input[type="checkbox"] {
    opacity: 0;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    cursor: pointer;
    margin: 0;
  }

  .toggle-track {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #cfc9b9;
    border-radius: 12px;
    transition: background-color 0.2s ease;
  }

  .toggle-thumb {
    position: absolute;
    content: "";
    height: 20px;
    width: 20px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    border-radius: 50%;
    transition: transform 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }

  input:checked + .toggle-track {
    background-color: var(--bloom-primary-green);
  }

  input:checked + .toggle-track .toggle-thumb {
    transform: translateX(20px);
  }

  input:focus-visible + .toggle-track {
    outline: 2px solid var(--bloom-text-control-blue);
    outline-offset: 2px;
  }

  @media (prefers-reduced-motion: reduce) {
    .toggle-track, .toggle-thumb {
      transition: none;
    }
  }
</style>
