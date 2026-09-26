import { describe, it, expect } from 'vitest';
import jsonFixtures from '../../../../contracts/chat_response_fixture.json';
import type { ChatResponse } from '../api';

// By explicitly typing this array, we guarantee at compile-time 
// that these objects perfectly match the ChatResponse frontend contract
// without any unsafe casts or widenings.
const typedFixtures: ChatResponse[] = [
  {
    reply: 'Minimal reply',
    session_id: null,
    intent: null,
    tier: 'PARSER',
    degraded: null,
    draft: null,
    preview: null,
    goal_created: null,
    suggestions: [],
    assumptions: [],
    question: null
  },
  {
    reply: 'Test reply',
    session_id: '12345',
    intent: 'TEST',
    tier: 'RULES',
    degraded: null,
    draft: null,
    preview: null,
    goal_created: null,
    suggestions: [
      {
        label: 'Click me',
        action: 'TEST_ACTION',
        send_text: null,
        patch: null
      }
    ],
    assumptions: [
      {
        id: 'a1',
        kind: 'time',
        text: 'Tomorrow',
        task_id: null
      }
    ],
    question: null
  },
  {
    reply: 'Today draft',
    session_id: '12345',
    intent: 'PLAN',
    tier: 'RULES',
    degraded: null,
    draft: {
      type: 'today',
      planDate: '2026-09-21',
      timezone: 'UTC',
      windows: [{ start: '09:00', end: '17:00' }],
      tasks: [
        {
          id: 't1',
          title: 'Task 1',
          durationMin: 30,
          priority: 'MEDIUM',
          importance: 'CORE',
          category: null,
          estimateSource: 'USER',
          breakAfterMin: null,
          deadline: null,
          schedulingType: 'FLEXIBLE',
          fixedStart: null,
          fixedEnd: null,
          dependencies: [],
          splittable: false
        }
      ]
    },
    preview: {
      plan_date: '2026-09-21',
      status: 'PREVIEW',
      timezone: 'UTC',
      unscheduled_tasks: [],
      reasons: [],
      reality_check: null,
      blocks: [],
      preview_token: 'token123'
    },
    goal_created: null,
    suggestions: [],
    assumptions: [],
    question: null
  },
  {
    reply: 'Roadmap draft',
    session_id: '12345',
    intent: 'GOAL',
    tier: 'LLM',
    degraded: 'Reason',
    draft: {
      type: 'roadmap',
      goalId: 'g1',
      goalTitle: 'Learn Python',
      goalDescription: 'From scratch',
      targetDate: '2026-12-31',
      milestones: [
        {
          id: 'm1',
          title: 'Learn basics',
          targetDate: '2026-10-31',
          expectedOutcome: null
        }
      ]
    },
    preview: null,
    goal_created: { id: 'g1' },
    suggestions: [],
    assumptions: [],
    question: 'Are you sure?'
  }
];

describe('Chat API Contract CT-015', () => {
  it('should perfectly match the JSON backend fixture', () => {
    // This asserts at runtime that the backend-generated JSON fixture 
    // exactly matches our compile-time strictly typed objects.
    // Proving end-to-end type safety across the boundary.
    expect(jsonFixtures).toEqual(typedFixtures);
    
    // Explicit checks for the cases
    expect(typedFixtures[0].reply).toBe('Minimal reply');
    expect(typedFixtures[1].suggestions[0].label).toBe('Click me');
    expect(typedFixtures[2].draft?.type).toBe('today');
    expect(typedFixtures[3].draft?.type).toBe('roadmap');
  });
});
