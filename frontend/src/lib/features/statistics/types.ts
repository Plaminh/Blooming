export interface StatisticsDateRange {
  id: string;
  startDate: Date;
  endDate: Date;
  displayLabel: string;
}

export interface SummaryMetrics {
  studyTimeHours: number;
  studyTimeMinutes: number;
  studyDayCount: number;
  completedPlanCount: number;
  unfinishedPlanCount: number;
}

export type StudyStatus = 'studied' | 'no-record' | 'inactive' | 'empty';

export interface CalendarDayState {
  day: number;
  status: StudyStatus;
}

export interface CalendarMonth {
  year: number;
  month: number;
  studiedDays: CalendarDayState[];
}

export interface DailyStudyEntry {
  dayLabel: string;
  hours: number;
}

export type PlanStatus = 'Completed' | 'Unfinished';

export interface PlanHistoryEntry {
  id: string;
  dateLabel: string;
  planName: string;
  completedTasks: number;
  totalTasks: number;
  status: PlanStatus;
}

export type HistoryFilter = 'All' | 'Completed' | 'Unfinished';

export interface PaginationState {
  currentPage: number;
  totalPages: number;
  itemsPerPage: number;
  totalItems: number;
}
