import { api } from '../client';
import type { RoadmapDraft } from '../types';

export const saveRoadmap = async (
  sessionId: string | null, draft: RoadmapDraft, idempotencyKey: string
): Promise<unknown> => {
  if (draft.goalId) {
    return await api.put(`/goals/${draft.goalId}/from-roadmap`, {
      session_id: sessionId,
      idempotency_key: idempotencyKey,
      draft
    });
  }
  return await api.post('/goals/from-roadmap', {
    session_id: sessionId,
    idempotency_key: idempotencyKey,
    draft
  });
};
