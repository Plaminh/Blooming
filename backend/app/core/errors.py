from typing import Any, Dict

from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        headers: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message},
            headers=headers,
        )


class CyclicDependencyError(AppError):
    def __init__(self, message: str = "A cyclic dependency was detected."):
        super().__init__(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "CYCLIC_DEPENDENCY", message
        )


class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "The requested resource was not found."):
        super().__init__(status.HTTP_404_NOT_FOUND, "RESOURCE_NOT_FOUND", message)


class UnauthorizedOwnershipError(AppError):
    def __init__(
        self, message: str = "You do not have permission to access this resource."
    ):
        super().__init__(status.HTTP_403_FORBIDDEN, "UNAUTHORIZED_OWNERSHIP", message)


class InvalidTimeRangeError(AppError):
    def __init__(self, message: str = "The provided time range is invalid."):
        super().__init__(status.HTTP_400_BAD_REQUEST, "INVALID_TIME_RANGE", message)


class FixedTaskOverlapError(AppError):
    def __init__(self, message: str = "Fixed tasks cannot overlap."):
        super().__init__(status.HTTP_400_BAD_REQUEST, "FIXED_TASK_OVERLAP", message)


class StaleTimelineError(AppError):
    def __init__(
        self,
        message: str = "The timeline draft is stale due to changes in source tasks.",
    ):
        super().__init__(status.HTTP_400_BAD_REQUEST, "STALE_TIMELINE", message)


class PlanAlreadyExistsError(AppError):
    def __init__(self, message: str = "A plan already exists for this date."):
        super().__init__(status.HTTP_409_CONFLICT, "PLAN_ALREADY_EXISTS", message)


class InvalidStatusTransitionError(AppError):
    def __init__(self, message: str = "The requested status transition is invalid."):
        super().__init__(status.HTTP_409_CONFLICT, "INVALID_STATUS_TRANSITION", message)


class ValidationError(AppError):
    def __init__(self, message: str = "A validation error occurred."):
        super().__init__(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR", message
        )
