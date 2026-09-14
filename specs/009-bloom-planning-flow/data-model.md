# Data Model: Mr. Bloom Planning and Draft Review Flow

This document defines the TypeScript interfaces that act as the shared view-model for the feature. These represent local, transient frontend state and are not intended for immediate persistence to the backend.

```typescript
// frontend/src/lib/features/mr-bloom/types.ts

export type MessageRole = 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string; // ISO string or formatted time like '09:00'
}

export type Priority = 'Core' | 'Optional';
export type TimelineEntryType = 'task' | 'break' | 'buffer';

export interface Milestone {
  id: string;
  title: string;
  targetDate: string; // e.g., 'Jun 30, 2024'
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
  icon?: string;
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
  startTime: string; // e.g., '09:00'
  endTime: string;   // e.g., '10:30'
  durationLabel: string; // e.g., '1 h 30 min'
  taskId?: string; // Reference to original DraftTask if applicable
  icon?: string;
}

export interface TimelineDraft {
  type: 'timeline';
  entries: TimelineEntry[];
}

export type ActiveDraft = RoadmapDraft | TodayDraft | TimelineDraft | null;

export type PreviewMode = 'placeholder' | 'roadmap' | 'today' | 'timeline';

// The store state
export interface MrBloomState {
  chatHistory: ChatMessage[];
  isWaitingForResponse: boolean;
  activeDraft: ActiveDraft;
  previewMode: PreviewMode;
}
```

## Validation Rules
- `ChatMessage.content` must not be empty or contain only whitespace.
- `DraftTask.durationMin` must be greater than 0 and less than or equal to 1440.

## State Transitions
1. `null` -> `RoadmapDraft` upon receiving a roadmap planning response.
2. `null` -> `TodayDraft` upon receiving a daily planning response.
3. `TodayDraft` -> `TimelineDraft` upon user action "Generate Timeline".
4. `TimelineDraft` -> `TodayDraft` upon user action "Back to Tasks".
5. Any draft -> `null` upon "Discard", "Save to Goals", or "Save to Today".
