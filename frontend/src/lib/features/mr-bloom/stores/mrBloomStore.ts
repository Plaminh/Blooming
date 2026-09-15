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
        content: 'Good morning.\nWhat would you like to work on today?',
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
          let aiResponse: string;
          
          if (isRoadmap) {
            nextMode = 'roadmap';
            aiResponse = "I've broken that goal into four outcome-based milestones. Review the roadmap on the right.";
            nextDraft = {
              type: 'roadmap',
              goalTitle: 'Complete Blooming MVP',
              goalDescription: 'Build and launch a delightful desktop app.',
              targetDate: 'Jun 30, 2024',
              milestones: [
                { id: 'm1', title: 'Freeze product concept', targetDate: 'Apr 30, 2024' },
                { id: 'm2', title: 'Build planning core', targetDate: 'May 31, 2024' },
                { id: 'm3', title: 'Implement desktop widget', targetDate: 'Jun 15, 2024' },
                { id: 'm4', title: 'Validate MVP', targetDate: 'Jun 30, 2024' }
              ]
            } as RoadmapDraft;
          } else {
            nextMode = 'today';
            aiResponse = "I've prepared a draft for you to review.";
            nextDraft = {
              type: 'today',
              availability: { start: '09:00', end: '15:00', totalHours: 6 },
              tasks: [
                { id: 't1', title: 'Study databases', durationMin: 90, priority: 'Core', icon: 'book' },
                { id: 't2', title: 'Finish proposal', durationMin: 120, priority: 'Core', icon: 'document' },
                { id: 't3', title: 'Go for a walk', durationMin: 30, priority: 'Optional', icon: 'shoe' }
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
