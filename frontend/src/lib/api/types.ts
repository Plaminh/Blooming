export type Category = "Learning" | "Work" | "Personal" | null;

export interface PlantCatalogItem {
  id: string;
  species: string;
  name: string;
  description: string;
  unlock_cost: number;
  is_unlocked: boolean;
  is_selected: boolean;
}

export interface GardenState {
  water_balance: number;
  leaves_balance: number;
  selected_plant_id: string | null;
  growth_points: number;
  growth_stage: GrowthStage;
  vitality: number;
  catalog: PlantCatalogItem[];
}

export type GrowthStage = "SPROUTING" | "GROWING" | "BLOOMING" | "FLOURISHING";




export interface UserSettingsResponse {
  timezone: string;
  default_focus_minutes: number;
  default_break_minutes: number;
  launch_on_startup: boolean;
  widget_always_on_top: boolean;
  widget_visibility: boolean;
  milestone_reminder_lead_time_minutes: number;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  weather_enabled: boolean;
  weather_location: string | null;
  weather_location_name: string | null;
  weather_lat: number | null;
  weather_lon: number | null;
  scene_season: string;
  weather_animation_enabled: boolean;
}



export interface AvailabilityWindowDraft {
  start: string;
  end: string;
}

export interface TaskDraft {
  id: string;
  title: string;
  durationMin: number;
  priority: 'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW';
  schedulingType: 'FLEXIBLE' | 'FIXED';
  importance: 'CORE' | 'OPTIONAL';
  estimateSource: 'USER' | 'RULE' | 'AI' | 'HISTORY';
  category?: string | null;
  fixedStart?: string | null;
  fixedEnd?: string | null;
  deadline?: string | null;
  dependencies: string[];
  splittable: boolean;
  breakAfterMin?: number | null;
  /** Saving creates a repeating template for this task. */
  recurrence?: RecurrenceDraft | null;
  /** Server-issued: the repeating template this task is an occurrence of. */
  recurringTaskId?: string | null;
  /** Server-issued: an existing unscheduled task carried into this day. */
  sourceTaskId?: string | null;
}

export interface RecurrenceDraft {
  freq: 'DAILY' | 'WEEKLY';
  /** 0 = Monday ... 6 = Sunday. */
  weekdays?: number[];
  until?: string | null;
}

export interface DeferredTaskDraft {
  task: TaskDraft;
  targetDate: string;
}

export interface TodayDraft {
  type: 'today';
  planDate: string;
  timezone: string;
  windows: { start: string; end: string }[];
  tasks: TaskDraft[];
  deferred_tasks?: DeferredTaskDraft[];
}

export interface MilestoneDraft {
  id?: string | null;
  title: string;
  targetDate: string;
  expectedOutcome?: string | null;
}

export interface RoadmapDraft {
  type: 'roadmap';
  goalId?: string | null;
  goalTitle: string;
  goalDescription: string;
  targetDate: string;
  milestones: MilestoneDraft[];
}

export type AssistantDraft = TodayDraft | RoadmapDraft;

export type PatchOp = 
  | { op: "remove_task"; task_id: string }
  | { op: "remove_deferred_task"; task_id: string }
  | { op: "move_task_to_date"; task_id: string; target_date: string; timezone?: string | null }
  | { op: "update_window"; window_index: number; start?: string | null; end?: string | null }
  | { op: "update_task"; task_id: string; duration_min?: number | null; title?: string | null; importance?: "CORE" | "OPTIONAL" | null; priority?: "LOW" | "MEDIUM" | "HIGH" | "URGENT" | null; category?: "Learning" | "Work" | "Personal" | null; break_after_min?: number | null; splittable?: boolean | null; fixed_start?: string | null; fixed_end?: string | null; deadline?: string | null; scheduling_type?: "FLEXIBLE" | "FIXED" | null }
  | { op: "split_task"; task_id: string; split_minutes: number }
  | { op: "add_task"; task: TaskDraft }
  | { op: "scale_durations"; factor: number; task_id?: string | null }
  | { op: "set_windows"; windows: AvailabilityWindowDraft[] }
  | { op: "set_plan_date"; plan_date: string };

export interface RepairSuggestion {
  label: string;
  patch: PatchOp[];
}

export interface AssistantSuggestion {
  label: string;
  action?: string | null;
  send_text?: string | null;
  patch?: PatchOp[] | null;
}

export interface AssistantAssumption {
  id: string;
  kind: string;
  text: string;
  task_id: string | null;
}

export interface AssistantSessionMessage {
  role: 'user' | 'assistant';
  content: string;
  structured_payload: {
    draft?: AssistantDraft | null;
    preview?: TodayPreviewResponse | null;
    degraded?: string | null;
    suggestions?: AssistantSuggestion[];
    assumptions?: AssistantAssumption[];
  } | null;
  created_at: string;
}

export interface AssistantSession {
  session_id: string;
  status: string;
  messages: AssistantSessionMessage[];
}


export interface TodayBlock {
  id: string;
  block_type: string;
  task_id: string | null;
  draft_task_id: string | null;
  title: string | null;
  description: string | null;
  category: string | null;
  estimated_duration_minutes: number | null;
  importance: 'CORE' | 'OPTIONAL' | null;
  preferred_break_duration_minutes: number | null;
  source: string | null;
  planned_start_at: string;
  planned_end_at: string;
  position: number;
  status: string;
  is_locked: boolean;
}

export interface UnscheduledTaskInfo {
  task_id?: string | null;
  draft_task_id?: string | null;
  title?: string | null;
  reason?: string | null;
}

export interface UnscheduledReason {
  code: string;
  task_id: string;
  dependency_id?: string;
}

export interface TodayResponse {
  plan_date: string;
  status: 'DRAFT' | 'CONFIRMED' | 'ACTIVE' | 'COMPLETED' | 'ARCHIVED';
  timezone: string;
  unscheduled_tasks: UnscheduledTaskInfo[] | string[];
  reasons: UnscheduledReason[];
  reality_check: string | null;
  blocks: TodayBlock[];
  suggestions?: RepairSuggestion[];
}

export interface TodayNoPlanResponse {
  timezone: string;
  plan_date: string;
  status: 'NO_PLAN';
  pending_tasks: UnscheduledTaskInfo[];
}

export interface TodayPreviewResponse {
  plan_date: string;
  status: 'PREVIEW';
  timezone: string;
  preview_token: string;
  reality_check: string | null;
  blocks: TodayBlock[];
  unscheduled_tasks: UnscheduledTaskInfo[];
  reasons: UnscheduledReason[];
  suggestions?: RepairSuggestion[];
}

export interface ChatResponse {
  reply: string;
  session_id: string | null;
  intent: string | null;
  tier: string;
  degraded: string | null;
  draft: AssistantDraft | null;
  preview: TodayPreviewResponse | null;
  goal_created: Record<string, unknown> | null;
  suggestions: AssistantSuggestion[];
  assumptions: AssistantAssumption[];
  question: string | null;
}

export interface AssistantEventPayload {
  event_id: string;
  event_name: string;
  [key: string]: unknown;
}

export interface AssistantEventResult {
  nudge?: { id: string; message: string; action: string } | null;
}

export interface FocusSessionPayload {
  task_id: string | null;
  planned_focus_seconds: number;
  planned_break_seconds: number;
}
