import { api } from '$lib/api';
import type { 
  SummaryMetrics, 
  DailyStudyEntry, 
  PlanHistoryEntry,
  HistoryFilter
} from '../types';

export interface PlanHistoryResponse {
  items: PlanHistoryEntry[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  itemsPerPage: number;
}

interface RawSummaryMetrics {
  study_time_hours: number;
  study_time_minutes: number;
  study_day_count: number;
  completed_plan_count: number;
  unfinished_plan_count: number;
}

interface RawDailyStudyEntry {
  day_label: string;
  hours: number;
  date: string;
}

interface RawPlanHistoryItem {
  id: string;
  date_label: string;
  plan_name: string;
  completed_tasks: number;
  total_tasks: number;
  status: string;
}

interface RawPlanHistoryResponse {
  items: RawPlanHistoryItem[];
  total_items: number;
  total_pages: number;
  current_page: number;
  items_per_page: number;
}

function formatLocalDate(date: Date): string {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export const statisticsApi = {
  async getSummary(startDate: Date, endDate: Date): Promise<SummaryMetrics> {
    const params = new URLSearchParams({
      start_date: formatLocalDate(startDate),
      end_date: formatLocalDate(endDate),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    });
    
    const response = (await api.get(`/v1/statistics/summary?${params.toString()}`)) as RawSummaryMetrics;
    return {
      studyTimeHours: response.study_time_hours,
      studyTimeMinutes: response.study_time_minutes,
      studyDayCount: response.study_day_count,
      completedPlanCount: response.completed_plan_count,
      unfinishedPlanCount: response.unfinished_plan_count
    };
  },

  async getDaily(startDate: Date, endDate: Date): Promise<DailyStudyEntry[]> {
    const params = new URLSearchParams({
      start_date: formatLocalDate(startDate),
      end_date: formatLocalDate(endDate),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    });
    
    const response = (await api.get(`/v1/statistics/daily?${params.toString()}`)) as RawDailyStudyEntry[];
    return response.map((item: RawDailyStudyEntry) => ({
      dayLabel: item.day_label,
      hours: item.hours,
      date: item.date
    }));
  },

  async getPlanHistory(
    startDate: Date,
    endDate: Date,
    status: HistoryFilter,
    page: number,
    pageSize: number
  ): Promise<PlanHistoryResponse> {
    const params = new URLSearchParams({
      start_date: formatLocalDate(startDate),
      end_date: formatLocalDate(endDate),
      status: status,
      page: page.toString(),
      page_size: pageSize.toString()
    });
    
    const response = (await api.get(`/v1/statistics/plan-history?${params.toString()}`)) as RawPlanHistoryResponse;
    return {
      items: response.items.map((item: RawPlanHistoryItem) => ({
        id: item.id,
        dateLabel: item.date_label,
        planName: item.plan_name,
        completedTasks: item.completed_tasks,
        totalTasks: item.total_tasks,
        status: item.status as 'Completed' | 'Unfinished'
      })),
      totalItems: response.total_items,
      totalPages: response.total_pages,
      currentPage: response.current_page,
      itemsPerPage: response.items_per_page
    };
  }
};
