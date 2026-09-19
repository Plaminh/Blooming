import { writable } from 'svelte/store';
import { api } from '$lib/api';
import type { IconName } from '$lib/shared/components/atoms/AppIcon.svelte';

export type MessageRole = 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
}

export type Priority = 'Core' | 'Optional';
export type TimelineEntryType = 'task' | 'break' | 'buffer';

export interface Milestone {
  id: string;
  title: string;
  targetDate: string;
}

export interface RoadmapDraft {
  type: 'roadmap';
  goalTitle: string;
  goalDescription: string;
  targetDate: string;
  milestones: Milestone[];
}

export interface DraftTask {
  id: string;
  title: string;
  durationMin: number;
  priority: Priority;
  icon?: IconName;
}

export interface TodayDraft {
  type: 'today';
  availability: {
    start: string;
    end: string;
    totalHours: number;
  };
  tasks: DraftTask[];
}

export interface TimelineEntry {
  id: string;
  type: TimelineEntryType;
  title: string;
  startTime: string;
  endTime: string;
  durationLabel: string;
  taskId?: string;
  icon?: IconName;
}

export interface TimelineDraft {
  type: 'timeline';
  entries: TimelineEntry[];
}

type ApiDraft =
  | (Omit<RoadmapDraft, 'milestones'> & { milestones: Omit<Milestone, 'id'>[] })
  | (Omit<TodayDraft, 'tasks'> & { tasks: Omit<DraftTask, 'id'>[] });

export type ActiveDraft = RoadmapDraft | TodayDraft | TimelineDraft | null;

export type PreviewMode = 'placeholder' | 'roadmap' | 'today' | 'timeline';

export interface MrBloomState {
  chatHistory: ChatMessage[];
  isWaitingForResponse: boolean;
  activeDraft: ActiveDraft;
  previewMode: PreviewMode;
  error?: string | null;
}

function createMrBloomStore() {
  const { subscribe, set, update } = writable<MrBloomState>({
    chatHistory: [
      {
        id: '1',
        role: 'assistant',
        content: 'Good morning.\nWhat would you like to work on today?',
        timestamp: '09:00'
      }
    ],
    isWaitingForResponse: false,
    activeDraft: null,
    previewMode: 'placeholder',
    error: null
  });

  return {
    subscribe,
    set,
    update,
    submitMessage: async (content: string) => {
      const message = content.trim();
      if (!message) return;
      let history: { role: MessageRole; content: string }[] = [];
      let accepted = false;
      update(state => {
        if (state.isWaitingForResponse) return state;
        accepted = true;
        history = state.chatHistory.filter(turn => turn.id !== '1').slice(-12).map(({ role, content }) => ({ role, content }));
        return {
          ...state,
          error: null,
          isWaitingForResponse: true,
          chatHistory: [...state.chatHistory, {
            id: crypto.randomUUID(), role: 'user', content: message,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]
        };
      });
      if (!accepted) return;
      try {
        const result: { reply: string; draft: ApiDraft | null } = await api.post('/assistant/chat', { message, history });
        let draft: ActiveDraft = null;
        if (result.draft?.type === 'roadmap') {
          draft = { ...result.draft, milestones: result.draft.milestones.map(m => ({ ...m, id: crypto.randomUUID() })) };
        } else if (result.draft?.type === 'today') {
          draft = { ...result.draft, tasks: result.draft.tasks.map(t => ({ ...t, id: crypto.randomUUID() })) };
        }
        update(state => ({
          ...state,
          isWaitingForResponse: false,
          activeDraft: draft ?? state.activeDraft,
          previewMode: draft?.type ?? state.previewMode,
          chatHistory: [...state.chatHistory, {
            id: crypto.randomUUID(), role: 'assistant', content: result.reply,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]
        }));
      } catch (error) {
        update(state => ({
          ...state,
          isWaitingForResponse: false,
          error: error instanceof Error ? error.message : 'Unable to reach Mr. Bloom.'
        }));
      }
    },
    discardDraft: () => {
      update(state => ({ ...state, activeDraft: null, previewMode: 'placeholder' }));
    },
    acceptDraft: (message: string) => {
      const now = new Date();
      const aiTimeStr = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
      update(state => ({
        ...state,
        activeDraft: null,
        previewMode: 'placeholder',
        chatHistory: [
          ...state.chatHistory,
          { id: crypto.randomUUID(), role: 'assistant', content: message, timestamp: aiTimeStr }
        ]
      }));
    },
    updateTaskDuration: (taskId: string, durationMin: number) => {
      update(state => {
        if (state.activeDraft?.type !== 'today') return state;
        const tasks = state.activeDraft.tasks.map(t => 
          t.id === taskId ? { ...t, durationMin } : t
        );
        return {
          ...state,
          activeDraft: { ...state.activeDraft, tasks }
        };
      });
    },
    updateTaskPriority: (taskId: string, priority: Priority) => {
      update(state => {
        if (state.activeDraft?.type !== 'today') return state;
        return {
          ...state,
          activeDraft: {
            ...state.activeDraft,
            tasks: state.activeDraft.tasks.map(task => task.id === taskId ? { ...task, priority } : task)
          }
        };
      });
    },
    removeTask: (taskId: string) => {
      update(state => {
        if (state.activeDraft?.type !== 'today') return state;
        return {
          ...state,
          activeDraft: {
            ...state.activeDraft,
            tasks: state.activeDraft.tasks.filter(task => task.id !== taskId)
          }
        };
      });
    },
    generateTimeline: () => {
      const now = new Date();
      const aiTimeStr = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
      update(state => ({
        ...state,
        previewMode: 'timeline',
        chatHistory: [
          ...state.chatHistory,
          { id: crypto.randomUUID(), role: 'assistant', content: 'Your timeline is ready. It includes breaks and leaves 30 minutes of buffer.', timestamp: aiTimeStr }
        ]
      }));
    },
    backToTasks: () => {
      update(state => ({ ...state, previewMode: 'today' }));
    }
  };
}

export const mrBloomStore = createMrBloomStore();
