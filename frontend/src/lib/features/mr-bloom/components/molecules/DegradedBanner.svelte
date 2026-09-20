<script lang="ts">
  let { mode }: { mode: string } = $props();
</script>
<div class="banner" role="status">
  {mode === 'RULES_ONLY'
    ? 'Mr. Bloom is using offline planning rules. Preview and save are still available.'
    : 'Mr. Bloom is conserving AI capacity. Some complex requests may use simpler planning.'}
</div>
<style>
  .banner { margin: 4px 14px; padding: 8px 10px; border: 1px solid #d1a83c; border-radius: 5px; background: #fff6d7; color: #624b10; font-size: 13px; }
</style>
