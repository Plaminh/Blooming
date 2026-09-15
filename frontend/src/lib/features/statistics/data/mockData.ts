import type { StatisticsDateRange, SummaryMetrics, CalendarDayState, DailyStudyEntry, PlanHistoryEntry } from '../types';

export const dateRanges: StatisticsDateRange[] = [
  {
    id: 'jun-1-14-2026',
    startDate: new Date(2026, 5, 1),
    endDate: new Date(2026, 5, 14),
    displayLabel: 'Jun 1 - 14, 2026'
  },
  {
    id: 'jun-15-28-2026',
    startDate: new Date(2026, 5, 15),
    endDate: new Date(2026, 5, 28),
    displayLabel: 'Jun 15 - 28, 2026'
  },
  {
    id: 'may-2026',
    startDate: new Date(2026, 4, 1),
    endDate: new Date(2026, 4, 31),
    displayLabel: 'May 2026'
  }
];

export const summaryMetrics: Record<string, SummaryMetrics> = {
  'jun-1-14-2026': {
    studyTimeHours: 24,
    studyTimeMinutes: 30,
    studyDayCount: 10,
    completedPlanCount: 8,
    unfinishedPlanCount: 3
  },
  'jun-15-28-2026': {
    studyTimeHours: 18,
    studyTimeMinutes: 15,
    studyDayCount: 7,
    completedPlanCount: 5,
    unfinishedPlanCount: 2
  },
  'may-2026': {
    studyTimeHours: 40,
    studyTimeMinutes: 0,
    studyDayCount: 20,
    completedPlanCount: 15,
    unfinishedPlanCount: 5
  }
};

export const calendarStudiedDays: Record<string, CalendarDayState[]> = {
  'jun-1-14-2026': [
    ...[1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14].map(day => ({ day, status: 'studied' as const }))
  ],
  'jun-15-28-2026': [
    ...[16, 17, 19, 21, 22, 23, 25, 27].map(day => ({ day, status: 'studied' as const }))
  ],
  'may-2026': [
    ...[2, 3, 5, 6, 8, 9, 10, 13, 14, 15, 17, 19, 20, 22, 24, 25, 27, 28, 30, 31].map(day => ({ day, status: 'studied' as const }))
  ]
};

export const dailyStudyEntries: Record<string, DailyStudyEntry[]> = {
  'jun-1-14-2026': [
    { dayLabel: 'Mon', hours: 2 },
    { dayLabel: 'Tue', hours: 3 },
    { dayLabel: 'Wed', hours: 0 },
    { dayLabel: 'Thu', hours: 2.5 },
    { dayLabel: 'Fri', hours: 4 },
    { dayLabel: 'Sat', hours: 0 },
    { dayLabel: 'Sun', hours: 3 }
  ],
  'jun-15-28-2026': [
    { dayLabel: 'Mon', hours: 1 },
    { dayLabel: 'Tue', hours: 2 },
    { dayLabel: 'Wed', hours: 3 },
    { dayLabel: 'Thu', hours: 0 },
    { dayLabel: 'Fri', hours: 1.5 },
    { dayLabel: 'Sat', hours: 4 },
    { dayLabel: 'Sun', hours: 0 }
  ],
  'may-2026': [
    { dayLabel: 'Mon', hours: 3 },
    { dayLabel: 'Tue', hours: 3 },
    { dayLabel: 'Wed', hours: 2 },
    { dayLabel: 'Thu', hours: 4 },
    { dayLabel: 'Fri', hours: 1 },
    { dayLabel: 'Sat', hours: 0 },
    { dayLabel: 'Sun', hours: 5 }
  ]
};

const allPlanEntries: PlanHistoryEntry[] = [
  { id: '1', dateLabel: 'Jun 14', planName: 'Learn machine learning', completedTasks: 3, totalTasks: 3, status: 'Completed' },
  { id: '2', dateLabel: 'Jun 12', planName: 'Build backend API', completedTasks: 2, totalTasks: 3, status: 'Unfinished' },
  { id: '3', dateLabel: 'Jun 11', planName: 'Study databases', completedTasks: 3, totalTasks: 3, status: 'Completed' },
  { id: '4', dateLabel: 'Jun 9', planName: 'Refine Blooming UI', completedTasks: 1, totalTasks: 3, status: 'Unfinished' },
  { id: '5', dateLabel: 'Jun 8', planName: 'Write tests', completedTasks: 4, totalTasks: 4, status: 'Completed' },
  { id: '6', dateLabel: 'Jun 6', planName: 'Design user flow', completedTasks: 2, totalTasks: 2, status: 'Completed' },
  { id: '7', dateLabel: 'Jun 5', planName: 'Implement authentication', completedTasks: 1, totalTasks: 2, status: 'Unfinished' },
  { id: '8', dateLabel: 'Jun 3', planName: 'Set up CI/CD', completedTasks: 5, totalTasks: 5, status: 'Completed' },
  { id: '9', dateLabel: 'Jun 2', planName: 'Create project structure', completedTasks: 3, totalTasks: 3, status: 'Completed' },
  { id: '10', dateLabel: 'Jun 1', planName: 'Read initial spec', completedTasks: 1, totalTasks: 1, status: 'Completed' },
  { id: '11', dateLabel: 'May 30', planName: 'Prepare workspace', completedTasks: 0, totalTasks: 2, status: 'Unfinished' }
];

export const planHistoryEntries: Record<string, PlanHistoryEntry[]> = {
  'jun-1-14-2026': allPlanEntries,
  'jun-15-28-2026': [
    { id: '12', dateLabel: 'Jun 25', planName: 'Refactor components', completedTasks: 4, totalTasks: 4, status: 'Completed' },
    { id: '13', dateLabel: 'Jun 22', planName: 'Optimize queries', completedTasks: 1, totalTasks: 3, status: 'Unfinished' },
    { id: '14', dateLabel: 'Jun 20', planName: 'Update documentation', completedTasks: 2, totalTasks: 2, status: 'Completed' },
  ],
  'may-2026': [
    { id: '15', dateLabel: 'May 28', planName: 'Finalize design', completedTasks: 5, totalTasks: 5, status: 'Completed' },
    { id: '16', dateLabel: 'May 15', planName: 'User research', completedTasks: 3, totalTasks: 4, status: 'Unfinished' }
  ]
};

export const getStatisticsData = (rangeId: string) => {
  return {
    metrics: summaryMetrics[rangeId],
    calendarDays: calendarStudiedDays[rangeId],
    dailyEntries: dailyStudyEntries[rangeId],
    planEntries: planHistoryEntries[rangeId]
  };
};
