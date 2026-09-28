import base64
import hashlib
import hmac
import json
import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.daily_plans import PlanRevision


def generate_hmac_token(
    user_id: UUID, draft_json: str, plan_version: str | None = None
) -> str:
    secret = settings.SECRET_KEY.get_secret_value().encode()
    expiry = int(time.time()) + 3600 * 24  # 24 hours
    purpose = "today_preview"

    version = plan_version or "none"
    msg = f"{user_id}:{purpose}:{expiry}:{version}:{draft_json}".encode()
    signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()

    token_data = {"exp": expiry, "sig": signature, "plan_version": version}
    return base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()


def preview_token_claims(
    user_id: UUID, draft_json: str, token: str
) -> dict[str, str | int] | None:
    try:
        token_data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
        expiry = token_data["exp"]
        signature = token_data["sig"]
        version = str(token_data.get("plan_version", "none"))
    except Exception:
        return None

    if time.time() > expiry:
        return None

    secret = settings.SECRET_KEY.get_secret_value().encode()
    purpose = "today_preview"
    msg = f"{user_id}:{purpose}:{expiry}:{version}:{draft_json}".encode()
    expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    return {"exp": int(expiry), "plan_version": version}


def verify_hmac_token(user_id: UUID, draft_json: str, token: str) -> bool:
    return preview_token_claims(user_id, draft_json, token) is not None


async def plan_version(db: AsyncSession, plan_id: UUID | None) -> str:
    if plan_id is None:
        return "none"
    revision = await db.scalar(
        select(PlanRevision)
        .where(PlanRevision.daily_plan_id == plan_id)
        .order_by(PlanRevision.revision_number.desc())
        .limit(1)
    )
    return f"{plan_id}:{revision.revision_number if revision else 0}"
