<script lang="ts">
</script>

<div class="comfort-indicator">
  <div class="indicator-inner">
    <span class="comfort-label">COMFORTABLE</span>
    <span class="comfort-text">A balanced day ahead.</span>
  </div>
</div>

<style>
  .comfort-indicator {
    width: 196px;
    height: 81px;
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .indicator-inner {
    border: 2px solid #a4caab;
    background: #ebf3e2;
    border-radius: 3px;
    padding: 10px 15px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .comfort-label {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 700;
    color: #607784;
  }

  .comfort-text {
    font-family: var(--bloom-body-font);
    font-size: 13px;
    color: #88a1a5;
  }
</style>
