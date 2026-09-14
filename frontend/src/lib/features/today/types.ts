export type TaskStatus = "in-progress" | "completed" | "upcoming";
export type TaskCategory = "Learning" | "Work" | "Personal";

export interface Task {
  id: string;
  title: string;
  startTime: string;
  endTime: string;
  durationString: string;
  status: TaskStatus;
  category: TaskCategory;
  description?: string;
  notes?: string;
  iconRef: "book" | "break" | "document" | "shoe";
}

export type FocusPreset = "25/5" | "50/10" | "Custom";
