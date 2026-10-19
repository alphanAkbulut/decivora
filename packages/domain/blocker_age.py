"""Read-only elapsed wall time. Never part of an approval/context digest."""
import math
import time

THRESHOLD_SECONDS = 7 * 24 * 60 * 60


def assess(assessment, *, cancelled=False, now=None):
    now = time.time() if now is None else now
    if type(now) not in (int, float) or not math.isfinite(now) or now < 0:
        raise ValueError('A finite nonnegative observation time is required.')
    known = []; unknown = 0
    for blocker in assessment['blockers']:
        since = blocker.get('since')
        if type(since) in (int, float) and math.isfinite(since) and 0 <= since <= now:
            known.append(since)
        else:
            unknown += 1
    active = assessment['blocked'] and not cancelled
    since = min(known) if active and known else None
    elapsed = now - since if since is not None else None
    overdue = elapsed is not None and elapsed > THRESHOLD_SECONDS
    return dict(active=active, since=since, elapsed_seconds=elapsed,
                evaluated_at=now if elapsed is not None else None, threshold_seconds=THRESHOLD_SECONDS,
                overdue=overdue, unknown_since_count=unknown if active else 0,
                coverage='known_recorded_blockers_only',
                status='overdue' if overdue else 'active' if since is not None else 'unknown' if active else 'inactive')
