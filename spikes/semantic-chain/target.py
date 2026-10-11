"""Pure assessment of a separately collected scoped target observation; no fetch/auth."""


def assess(expected, observation):
    # An authenticated observer collects this metadata, never the extraction model.
    if any(observation.get(k) != expected[k] for k in ('repository','path')):
        return dict(status='wrong_scope',task_verified=False)
    if observation.get('availability') != 'read':
        return dict(status='missing' if observation.get('availability')=='missing' else 'unknown',task_verified=False)
    if any(observation.get(k) != expected[k] for k in ('ref','artifact_revision')):
        return dict(status='stale',task_verified=False)
    if not isinstance(observation.get('sha256'),str) or len(observation['sha256'])!=64:
        return dict(status='unknown',task_verified=False)
    if observation['sha256'] != expected['sha256']:
        return dict(status='mismatch',task_verified=False)
    return dict(status='observed_match',task_verified=False)
