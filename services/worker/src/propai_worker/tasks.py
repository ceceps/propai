"""Job handlers.

Each task takes a jobs.id and owns the status transitions for that row, so a
crashed worker leaves an explainable record rather than a silently stuck job.
The content pipeline stages land here in the content phase; for now this proves
the queue round-trip end to end.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from propai_core.db import session_scope
from propai_core.models.jobs import Job, JobStatus


def _transition(job_id: uuid.UUID, status: JobStatus, **fields) -> None:
    with session_scope() as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        job.status = status
        for key, value in fields.items():
            setattr(job, key, value)


def ping(job_id: str) -> dict[str, str]:
    """Smoke-test job: proves api -> redis -> worker -> postgres works."""
    jid = uuid.UUID(job_id)
    _transition(jid, JobStatus.RUNNING, started_at=datetime.now(UTC))
    result = {"pong": True, "job_id": job_id}
    _transition(
        jid, JobStatus.SUCCEEDED, finished_at=datetime.now(UTC), result=result
    )
    return result
