# Data Model: Goals Screen

## Entities

### Goal
- `id`: string
- `title`: string
- `description`: string
- `iconRef`: string (e.g., 'leaf', 'book', 'shoe')
- `targetDate`: string (e.g., 'Jun 30, 2024')
- `milestones`: Milestone[]

### Milestone
- `id`: string
- `title`: string
- `description`: string
- `date`: string (e.g., 'Apr 30, 2024')
- `status`: 'Completed' | 'In progress' | 'Not started'

### Progress
- `completedCount`: number
- `totalCount`: number
- `percentage`: string (e.g., '50%')

### NextMilestone
- `milestone`: Milestone
- `countdown`: string (e.g., 'In 17 days')

### GardenState
- `unlockedCount`: number
- `totalCount`: number
