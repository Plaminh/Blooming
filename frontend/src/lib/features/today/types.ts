export type TaskStatus = "in-progress" | "completed" | "upcoming";
import type { Category } from "$lib/api/types";
export type TaskCategory = Category;

export interface Task {
  id: string; // the block id
  task_id?: string | null;
  title: string;
  startTime: string;
  endTime: string;
  durationString: string;
  estimatedDurationMinutes?: number;
  status: TaskStatus;
  category: TaskCategory | null;
  description?: string;
  notes?: string;
  iconRef: "book" | "break" | "document" | "shoe";
}

export type FocusPreset = "25/5" | "50/10" | "Custom";
