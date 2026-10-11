"""Independent candidate-stage rubric. Not a canonical-state or production release gate."""
from collections import Counter
from protocol import canonical, validate
from anchors import anchor

FIELDS = {'message_id', 'kind', 'quote', 'attributes'}


def key(record):
    return canonical({field: record[field] for field in FIELDS})


def evaluate_candidates(request, derived_response, rubric):
    """Exact message/kind/quote/attribute multiset matching; no label projection.

    Provisional entity_key and source positions are deliberately not quality metrics.
    Positions are validated separately. Gold review status must remain visible.
    """
    checked = validate(request, canonical(derived_response))
    if not isinstance(rubric, dict) or set(rubric) != {
        'format', 'request_id', 'review_status', 'expected'}:
        raise ValueError('invalid candidate rubric')
    if rubric['format'] != 'decivora-candidate-rubric-1' or rubric['request_id'] != request['request_id']:
        raise ValueError('rubric revision mismatch')
    if rubric['review_status'] not in ('authored_draft', 'human_reviewed'):
        raise ValueError('unknown rubric review status')
    expected = rubric['expected']
    if not isinstance(expected, list) or len(expected) > 64:
        raise ValueError('invalid rubric bounds')
    # Check expected candidates against source independently of predictions.
    records = []
    for i, row in enumerate(expected):
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError('invalid rubric candidate')
        records.append(dict(row, entity_key='rubric-' + str(i)))
    from anchors import FORMAT, prepare_quotes
    packet = prepare_quotes(request)
    anchor(request, canonical(dict(format=FORMAT, request_id=request['request_id'],
        contract_id=packet['contract_id'], status='ok', records=records)))
    gold = Counter(key(r) for r in expected)
    if any(n > 1 for n in gold.values()):
        raise ValueError('duplicate rubric expectation')
    predicted = Counter(key(r) for r in checked['records'])
    tp = sum((gold & predicted).values())
    fp, fn = sum((predicted - gold).values()), sum((gold - predicted).values())
    return dict(format='decivora-candidate-score-1', review_status=rubric['review_status'],
        status='incomplete' if checked['coverage'] == 'abstained' else 'evaluated',
        true_positive=tp, false_positive=fp, false_negative=fn,
        precision=tp/(tp+fp) if tp+fp else None, recall=tp/(tp+fn) if tp+fn else None,
        scored_fields=sorted(FIELDS), canonical_mutations=0,
        unscored=['entity_identity', 'canonical_state', 'authority', 'relations',
                  'impact', 'target_verification', 'acceptance_criteria'],
        missing=list((gold-predicted).elements()), extra=list((predicted-gold).elements()))
