import re
from typing import Optional, Dict, Any
from app.models.ai_schemas import AIRequestContext

class RuleParser:
    """
    Deterministically parses explicitly formatted task commands to bypass AI.
    Currently supported MVP formats:
    - task: <title>, <N>m
    - task: <title>
    """
    def parse(self, request_context: AIRequestContext) -> Optional[Dict[str, Any]]:
        if request_context.context_type != "today_planning":
            return None
            
        user_input = request_context.user_input.strip()
        
        # Match 'task: Clean desk, 30m' or 'task: Email client'
        task_match = re.match(r"(?i)^task:\s*(.+?)(?:,\s*(\d+)m)?$", user_input)
        if task_match:
            title = task_match.group(1).strip()
            duration_str = task_match.group(2)
            
            task_obj = {
                "title": title,
                "duration_min": None,
                "priority": None,
                "deadline": None,
                "is_core": None,
                "is_fixed": None,
                "dependencies": []
            }
            
            if duration_str:
                task_obj["duration_min"] = {
                    "value": int(duration_str),
                    "source": "USER",
                    "confidence": 1.0
                }
                
            return {
                "tasks": [task_obj]
            }

        return None
