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

export interface TodayTaskEdit {
  title?: string;
  estimated_duration_minutes?: number;
  category?: Category;
  description?: string | null;
}
export interface TodayBlock {
  id: string;
  task_id: string | null;
  title: string | null;
  description: string | null;
  category: Category;
  estimated_duration_minutes: number | null;
  planned_start_at: string;
  planned_end_at: string;
  status: "PLANNED" | "ACTIVE" | "COMPLETED" | "SKIPPED" | "CANCELLED";
  block_type: "TASK" | "BREAK" | "BUFFER" | "FIXED_EVENT";
}
export interface UnscheduledReason {
  code: string;
  task_id: string;
  dependency_id?: string | null;
}
export interface TodayResponse {
  timezone?: string;
  unscheduled_tasks?: string[];
  reasons?: UnscheduledReason[];
  plan_date: string;
  status: string;
  blocks?: TodayBlock[];
}
export interface UserSettingsResponse {
  mr_bloom_display_name: string;
  timezone: string;
  default_focus_minutes: number;
  default_break_minutes: number;
  launch_on_startup: boolean;
  widget_always_on_top: boolean;
  milestone_reminder_lead_time_minutes: number;
  weather_enabled: boolean;
  weather_location: string | null;
  weather_location_name: string | null;
  weather_lat: number | null;
  weather_lon: number | null;
  scene_season: string;
  weather_animation_enabled: boolean;
  widget_visibility?: boolean;
}
export interface WaterPlantResponse {
  water_balance: number;
  vitality: number;
  last_watered_at: string;
}
