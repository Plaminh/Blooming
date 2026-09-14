<script lang="ts">
  import type { Snippet } from 'svelte';
  import CarouselArrowIcon from '../atoms/CarouselArrowIcon.svelte';
  
  let { hasPrevious, hasNext, onPrevious, onNext, children }: { 
    hasPrevious: boolean; 
    hasNext: boolean; 
    onPrevious: () => void; 
    onNext: () => void;
    children?: Snippet;
  } = $props();
</script>

<div class="carousel-controls">
  <button 
    class="arrow-btn" 
    disabled={!hasPrevious} 
    onclick={onPrevious}
    aria-label="Previous plant"
  >
    <CarouselArrowIcon direction="previous" />
  </button>
  
  <div class="content">
    {@render children?.()}
  </div>
  
  <button 
    class="arrow-btn" 
    disabled={!hasNext} 
    onclick={onNext}
    aria-label="Next plant"
  >
    <CarouselArrowIcon direction="next" />
  </button>
</div>

<style>
  .carousel-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 64px;
    width: 100%;
  }
  .content {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .arrow-btn {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    outline: none;
    transition: transform 0.1s;
  }
  .arrow-btn:focus-visible {
    outline: 2px dashed #1e3a5f;
    outline-offset: 4px;
  }
  .arrow-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .arrow-btn:active:not(:disabled) {
    transform: scale(0.95);
  }
</style>
