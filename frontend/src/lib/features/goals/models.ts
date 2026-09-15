export type MilestoneStatus = 'Completed' | 'In progress' | 'Not started';

export interface Milestone {
  id: string;
  title: string;
  description: string;
  summary?: string;
  date: string;
  status: MilestoneStatus;
}

export interface Goal {
  id: string;
  title: string;
  description: string;
  targetDate: string;
  iconRef: string;
  milestones: Milestone[];
}

export const FIXTURE_GOALS: Goal[] = [
  {
    id: 'g1',
    title: 'Complete Blooming MVP',
    description: 'Build and launch a delightful desktop app.',
    targetDate: 'Jun 30, 2024',
    iconRef: 'leaf',
    milestones: [
      {
        id: 'm1',
        title: 'Freeze product concept',
        description: 'Define core problem, target users, key features and design direction.',
        date: 'Apr 30, 2024',
        status: 'Completed'
      },
      {
        id: 'm2',
        title: 'Build planning core',
        description: 'Build Today, Goals and Settings with local data storage and basic functionality.',
        summary: 'Build Today, Goals and Settings with local data storage.',
        date: 'May 31, 2024',
        status: 'In progress'
      },
      {
        id: 'm3',
        title: 'Implement desktop widget',
        description: 'Create a focused desktop widget for quick access to today\'s plan.',
        date: 'Jun 15, 2024',
        status: 'Not started'
      },
      {
        id: 'm4',
        title: 'Validate MVP',
        description: 'Test with early users, gather feedback and prepare for public launch.',
        date: 'Jun 30, 2024',
        status: 'Not started'
      }
    ]
  },
  {
    id: 'g2',
    title: 'Read 12 books',
    description: 'Explore new ideas and perspectives this year.',
    targetDate: 'Dec 31, 2024',
    iconRef: 'book',
    milestones: []
  },
  {
    id: 'g3',
    title: 'Stay healthy',
    description: 'Feel better with regular movement.',
    targetDate: 'Dec 31, 2024',
    iconRef: 'shoe',
    milestones: []
  }
];
