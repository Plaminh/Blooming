export type MilestoneStatus = 'COMPLETED' | 'IN_PROGRESS' | 'PENDING' | 'SKIPPED' | 'CANCELLED';

export interface Milestone {
  id: string;
  title: string;
  description: string | null;
  expected_outcome: string | null;
  due_at: string | null;
  target_date: string | null;
  status: MilestoneStatus;
}

export interface Goal {
  id: string;
  title: string;
  description: string | null;
  roadmap_summary: string | null;
  target_date: string | null;
  status: string;
  iconRef?: string;
  milestones: Milestone[];
}

// Mocks removed
