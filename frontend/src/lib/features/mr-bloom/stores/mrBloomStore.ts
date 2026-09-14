import { writable } from 'svelte/store';
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

export type ActiveDraft = RoadmapDraft | TodayDraft | TimelineDraft | null;

export type PreviewMode = 'placeholder' | 'roadmap' | 'today' | 'timeline';

export interface MrBloomState {
  chatHistory: ChatMessage[];
  isWaitingForResponse: boolean;
  activeDraft: ActiveDraft;
  previewMode: PreviewMode;
}

function createMrBloomStore() {
  const { subscribe, set, update } = writable<MrBloomState>({
    chatHistory: [
      {
        id: '1',
        role: 'assistant',
        content: 'What would you like to work on?',
        timestamp: '09:00'
      }
    ],
    isWaitingForResponse: false,
    activeDraft: null,
    previewMode: 'placeholder'
  });

  return {
    subscribe,
    set,
    update,
    submitMessage: (content: string) => {
      if (!content.trim()) return;
      
      const now = new Date();
      const timeStr = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
      
      update(state => ({
        ...state,
        chatHistory: [
          ...state.chatHistory,
          { id: crypto.randomUUID(), role: 'user', content, timestamp: timeStr }
        ],
        isWaitingForResponse: true
      }));
      
      setTimeout(() => {
        const isRoadmap = content.toLowerCase().includes('mvp') || content.toLowerCase().includes('goal');
        const aiTimeStr = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        update(state => {
          let nextDraft: ActiveDraft = null;
          let nextMode: PreviewMode = 'placeholder';
          let aiResponse = "Here is a draft based on what you asked.";
          
          if (isRoadmap) {
            nextMode = 'roadmap';
            nextDraft = {
              type: 'roadmap',
              goalTitle: 'Complete MVP',
              goalDescription: 'Finish the first playable release.',
              targetDate: 'Jun 30, 2024',
              milestones: [
                { id: 'm1', title: 'Design core mechanics', targetDate: 'May 15, 2024' },
                { id: 'm2', title: 'Implement physics engine', targetDate: 'Jun 01, 2024' }
              ]
            } as RoadmapDraft;
          } else {
            nextMode = 'today';
            nextDraft = {
              type: 'today',
              availability: { start: '09:00', end: '15:00', totalHours: 6 },
              tasks: [
                { id: 't1', title: 'Review PRs', durationMin: 60, priority: 'Core', icon: 'check' },
                { id: 't2', title: 'Fix bug #42', durationMin: 120, priority: 'Core', icon: 'bug' }
              ]
            } as TodayDraft;
          }
          
          return {
            ...state,
            isWaitingForResponse: false,
            activeDraft: nextDraft,
            previewMode: nextMode,
            chatHistory: [
              ...state.chatHistory,
              { id: crypto.randomUUID(), role: 'assistant', content: aiResponse, timestamp: aiTimeStr }
            ]
          };
        });
      }, 800);
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
    generateTimeline: () => {
      update(state => ({ ...state, previewMode: 'timeline' }));
    },
    backToTasks: () => {
      update(state => ({ ...state, previewMode: 'today' }));
    }
  };
}

export const mrBloomStore = createMrBloomStore();
