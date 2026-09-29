import { isRetryableTransportFailure } from '$lib/shared/networkFailures';

export const FOCUS_FINISH_QUEUE_KEY = 'blooming_focus_finish_queue_v1';

export interface FocusFinishItem {
  run_id: string;
  outcome: string;
  should_replan: boolean;
  queued_at: string;
}

function readQueue(storage: Storage): FocusFinishItem[] {
  try {
    const value = JSON.parse(storage.getItem(FOCUS_FINISH_QUEUE_KEY) ?? '[]');
    return Array.isArray(value) ? value.filter(item => item && typeof item.run_id === 'string') : [];
  } catch {
    return [];
  }
}

function writeQueue(storage: Storage, queue: FocusFinishItem[]) {
  storage.setItem(FOCUS_FINISH_QUEUE_KEY, JSON.stringify(queue));
}

export function enqueueFocusFinish(storage: Storage, item: Omit<FocusFinishItem, 'queued_at'>) {
  const queue = readQueue(storage);
  if (!queue.some(existing => existing.run_id === item.run_id)) {
    queue.push({ ...item, queued_at: new Date().toISOString() });
    writeQueue(storage, queue);
  }
  return queue;
}

export async function flushFocusFinishQueue(
  storage: Storage,
  send: (item: FocusFinishItem) => Promise<unknown>,
  onPermanentFailure: (item: FocusFinishItem, error: unknown) => void = () => undefined,
) {
  const remaining: FocusFinishItem[] = [];
  for (const item of readQueue(storage)) {
    try {
      await send(item);
    } catch (error) {
      if (isRetryableTransportFailure(error)) remaining.push(item);
      else onPermanentFailure(item, error);
    }
  }
  writeQueue(storage, remaining);
  return remaining;
}
