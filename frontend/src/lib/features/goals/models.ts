export type MilestoneStatus = 'COMPLETED' | 'IN_PROGRESS' | 'PENDING' | 'SKIPPED' | 'CANCELLED';

export interface Milestone {
  id: string;
  title: string;
  description: string;
  summary?: string;
  due_at: string;
  status: MilestoneStatus;
}

export interface Goal {
  id: string;
  title: string;
  description: string;
  target_date: string;
  iconRef: string;
  milestones: Milestone[];
}

// Mocks removed
