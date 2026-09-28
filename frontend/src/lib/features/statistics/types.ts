export interface StatisticsDateRange {
  id: string;
  startDate: Date;
  endDate: Date;
  displayLabel: string;
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



export interface PaginationState {
  currentPage: number;
  totalPages: number;
  itemsPerPage: number;
  totalItems: number;
}
