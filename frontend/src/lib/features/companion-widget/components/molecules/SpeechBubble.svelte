<script lang="ts">
  import type { CompanionWidgetKind } from "../../types/presentation";

  type Props = {
    text: string;
    kind: Exclude<CompanionWidgetKind, "reminders">;
  };

  let { text, kind }: Props = $props();
</script>

<div class="speech {kind}">
  <p>{text}</p>
</div>

<style>
  .speech {
    position: relative;
    width: 100%;
    height: 100%;
    padding: 11px 20px;
    border: var(--widget-stroke, 4px) solid var(--widget-navy, #0e3052);
    border-radius: var(--widget-radius, 4px);
    background: var(--widget-cream, #faefd5);
    color: var(--widget-heading, #213d59);
  }

  p {
    margin: 0;
    overflow: hidden;
    font-size: 22px;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.035em;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    line-clamp: 3;
  }

  .behindSchedule p {
    font-size: 22px;
    line-height: 1.16;
  }

  .behindSchedule {
    padding-top: 13px;
    padding-bottom: 9px;
  }

  .offline p {
    font-size: 20px;
  }

  .speech::before,
  .speech::after {
    content: "";
    position: absolute;
    clip-path: polygon(0 100%, 38% 0, 100% 0);
  }

  .speech::before {
    left: 15px;
    bottom: -27px;
    width: 38px;
    height: 28px;
    background: var(--widget-navy, #0e3052);
  }

  .speech::after {
    left: 21px;
    bottom: -18px;
    width: 27px;
    height: 20px;
    background: var(--widget-cream, #faefd5);
  }

  .behindSchedule::before {
    left: -2px;
  }

  .behindSchedule::after {
    left: 5px;
  }

  .paused::before,
  .offline::before {
    bottom: -22px;
    height: 23px;
  }

  .paused::after,
  .offline::after {
    bottom: -14px;
    height: 16px;
  }
</style>
