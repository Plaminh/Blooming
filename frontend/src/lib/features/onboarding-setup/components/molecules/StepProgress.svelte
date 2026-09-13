<script lang="ts">
  let { currentStep = 1 } = $props();

  const steps = [
    { num: 1, label: 'WELCOME' },
    { num: 2, label: 'TIME' },
    { num: 3, label: 'FOCUS' },
    { num: 4, label: 'WIDGET' },
  ];
</script>

<nav class="progress-container" aria-label="Onboarding progress">
  <div class="progress-line" aria-hidden="true"></div>
  <ol class="steps-wrapper">
    {#each steps as step}
      <li class="step-item" class:active={currentStep === step.num}>
        <span class="step-circle" aria-current={currentStep === step.num ? 'step' : undefined}>
          {step.num}
        </span>
        <span class="step-label">{step.label}</span>
      </li>
    {/each}
  </ol>
</nav>

<style>
  .progress-container {
    position: relative;
    width: 100%;
    height: 84px;
  }

  .progress-line {
    position: absolute;
    z-index: 1;
    top: 23px;
    right: 12.5%;
    left: 12.5%;
    height: 3px;
    background: var(--bloom-border-dark);
  }

  .steps-wrapper {
    position: relative;
    z-index: 2;
    display: block;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .step-item {
    position: absolute;
    top: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    transform: translateX(-50%);
  }

  .step-item:nth-child(1) {
    left: 105px;
  }

  .step-item:nth-child(2) {
    left: 302px;
  }

  .step-item:nth-child(3) {
    left: 513px;
  }

  .step-item:nth-child(4) {
    left: 728px;
  }

  .step-circle {
    display: grid;
    width: 48px;
    height: 48px;
    place-items: center;
    border: 3px solid var(--bloom-border-dark);
    border-radius: 50%;
    background: var(--bloom-surface-cream);
    color: var(--bloom-text-muted-blue);
    font-family: var(--bloom-body-font);
    font-size: 22px;
    font-weight: 700;
    line-height: 1;
  }

  .step-label {
    margin-top: 6px;
    color: var(--bloom-text-muted-blue);
    font-family: var(--bloom-display-font);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.025em;
    line-height: 1.2;
    white-space: nowrap;
  }

  .step-item.active .step-circle {
    border-color: var(--bloom-primary-green-border);
    background: var(--bloom-primary-green);
    color: #f2f6ec;
  }

  .step-item.active .step-label {
    color: var(--bloom-primary-green-border);
  }
</style>
