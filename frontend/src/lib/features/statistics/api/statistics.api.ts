import { api } from '$lib/api';
import { deviceTimezone } from '$lib/shared/deviceLocation';
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
      timezone: deviceTimezone()
    });
    
    const response = (await api.get(`/statistics/summary?${params.toString()}`)) as RawSummaryMetrics;
    return {
      studyTimeHours: response?.study_time_hours ?? 0,
      studyTimeMinutes: response?.study_time_minutes ?? 0,
      studyDayCount: response?.study_day_count ?? 0,
      completedPlanCount: response?.completed_plan_count ?? 0,
      unfinishedPlanCount: response?.unfinished_plan_count ?? 0
    };
  },

  async getDaily(startDate: Date, endDate: Date): Promise<DailyStudyEntry[]> {
    const params = new URLSearchParams({
      start_date: formatLocalDate(startDate),
      end_date: formatLocalDate(endDate),
      timezone: deviceTimezone()
    });
    
    const response = (await api.get(`/statistics/daily?${params.toString()}`)) as RawDailyStudyEntry[];
    if (!Array.isArray(response)) return [];
    
    return response.map((item: RawDailyStudyEntry) => ({
      dayLabel: item.day_label ?? '',
      hours: item.hours ?? 0,
      date: item.date ?? ''
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
    
    const response = (await api.get(`/statistics/plan-history?${params.toString()}`)) as RawPlanHistoryResponse;
    const items = Array.isArray(response?.items) ? response.items : [];
    
    return {
      items: items.map((item: RawPlanHistoryItem) => ({
        id: item.id ?? '',
        dateLabel: item.date_label ?? '',
        planName: item.plan_name ?? '',
        completedTasks: item.completed_tasks ?? 0,
        totalTasks: item.total_tasks ?? 0,
        status: (item.status as 'Completed' | 'Unfinished') ?? 'Unfinished'
      })),
      totalItems: response?.total_items ?? 0,
      totalPages: response?.total_pages ?? 0,
      currentPage: response?.current_page ?? 0,
      itemsPerPage: response?.items_per_page ?? pageSize
    };
  }
};
