from typing import Tuple, Optional, Any
from app.models.ai_schemas import TodayDraftProposal, RoadmapDraftProposal, AIRequestContext

class BusinessValidator:
    def validate(self, proposal: Any, request_context: AIRequestContext) -> Tuple[bool, Optional[str]]:
        if isinstance(proposal, TodayDraftProposal):
            total_duration = 0
            task_titles = set()
            
            if len(proposal.tasks) > 50:
                return False, "Too many tasks proposed (limit 50)."
                
            for task in proposal.tasks:
                if not task.title.strip():
                    return False, "Task title cannot be empty."
                if task.title in task_titles:
                    return False, f"Duplicate task title '{task.title}' not allowed."
                task_titles.add(task.title)
                
            for task in proposal.tasks:
                if task.duration_min:
                    val = task.duration_min.value
                    if val <= 0:
                        return False, f"Task '{task.title}' has non-positive duration."
                    if val > 720:
                        return False, f"Task '{task.title}' duration exceeds 12 hours."
                    total_duration += val
                    
                if task.deadline and task.deadline.value:
                    if task.deadline.value < request_context.current_time:
                        return False, f"Task '{task.title}' has deadline in the past."
                
                # Check dependencies
                dep_set = set()
                for dep in task.dependencies:
                    if dep == task.title:
                        return False, f"Task '{task.title}' depends on itself."
                    if dep in dep_set:
                        return False, f"Task '{task.title}' has duplicate dependency '{dep}'."
                    if dep not in task_titles:
                        return False, f"Task '{task.title}' depends on non-existent task '{dep}'."
                    dep_set.add(dep)
                    
                # Check fixed/flexible consistency
                if task.is_fixed and task.is_fixed.value and not task.deadline:
                    return False, f"Fixed task '{task.title}' requires a deadline."

            if total_duration > 1440:
                return False, "Total duration exceeds 24 hours."

        elif isinstance(proposal, RoadmapDraftProposal):
            if not proposal.goal_title.strip():
                return False, "Goal title cannot be empty."
                
            if len(proposal.milestones) > 100:
                return False, "Too many milestones (limit 100)."
                
            milestone_titles = set()
            last_date = None
            for m in proposal.milestones:
                if not m.title.strip():
                    return False, "Milestone title cannot be empty."
                if m.title in milestone_titles:
                    return False, f"Duplicate milestone title '{m.title}' not allowed."
                milestone_titles.add(m.title)
                    
                if m.target_date and m.target_date.value:
                    if m.target_date.value < request_context.current_time:
                        return False, f"Milestone '{m.title}' target date is in the past."
                    if last_date and m.target_date.value < last_date:
                        return False, "Milestones are not chronologically ordered."
                    last_date = m.target_date.value
                
        return True, None
