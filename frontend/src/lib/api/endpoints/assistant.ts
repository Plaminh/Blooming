import type { AssistantEventPayload, AssistantEventResult } from '../types';
import { api } from '../client';

export const logAssistantEvent = async (payload: AssistantEventPayload): Promise<AssistantEventResult> => {
  return await api.post('/assistant/events', payload);
};
