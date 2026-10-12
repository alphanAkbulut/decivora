import copy
import hashlib
import json
import unittest

from protocol import canonical, digest
from project_review import CONTEXT, associate_reply, clarification_records, review_projects
from receiver_smoke import ROOT, RULES, SCHEMA, ACTION_TYPES, evaluate


def fixture_context(request):
    return dict(format=CONTEXT, request_id=request['request_id'], atomic_groups=[],
        projects={v['binding']['project_id']: dict(review_access=True, current_binding=copy.deepcopy(v['binding']))
                  for v in request['views']})


def rebind_fixture(request):
    request['identity'] = dict(version='receiver-source-1', rules_sha256=digest(RULES), schema_sha256=digest(SCHEMA),
                              action_types=sorted(ACTION_TYPES), views_sha256=digest(request['views']))
    request['request_id'] = digest(request['identity'])
    request['prompt'] = RULES + '\nACTION_TYPES\n' + canonical(sorted(ACTION_TYPES)) + '\nCONTRACT\n' + canonical(SCHEMA) + '\nVIEWS\n' + canonical(dict(request_id=request['request_id'], views=request['views'])) + '\n'
    request['prompt_bytes'] = len(request['prompt'].encode())
    request['prompt_sha256'] = hashlib.sha256(request['prompt'].encode()).hexdigest()


class TestProjectReview(unittest.TestCase):
    def setUp(self):
        self.request = json.loads((ROOT / 'examples/receiver-smoke/request.json').read_text())
        self.output = json.loads((ROOT / 'examples/receiver-contract/valid-review.json').read_text())
        self.context = fixture_context(self.request)
        self.p1, self.p2 = [v['binding']['project_id'] for v in self.request['views']]

    def run_review(self, output=None):
        return review_projects(self.request, canonical(self.output if output is None else output), self.context)

    def reply(self):
        question = clarification_records(self.request, self.request['views'][1])[0]
        result = dict(clarification_id=question['clarification_id'], project_id=self.p2,
                      question_id='Q_UI', question_revision=1, option_id='B',
                      source_message_id='delayed-human-01', source_revision=1,
                      text='My earlier B was for Q_UI revision 1: timeline.', actor_type='human_owner')
        result['source_sha256'] = digest({k: result[k] for k in ('source_message_id', 'source_revision', 'text', 'actor_type')})
        return question, result

    def test_valid_other_project_survives_technical_type_error(self):
        self.output['responses'][1]['readback']['reported_test_results'][0]['criterion_revision'] = '2'
        result = self.run_review()
        self.assertEqual(result['status'], 'partial_review')
        self.assertEqual(result['projects'][0]['status'], 'ready_for_review')
        self.assertIsNotNone(result['projects'][0]['review'])
        self.assertEqual(result['projects'][1]['status'], 'invalid_project_output')
        self.assertIsNone(result['projects'][1]['review'])
        self.assertEqual(result['projects'][1]['clarifications'], [])
        self.assertEqual(result['projects'][1]['diagnostics'][0]['kind'], 'technical_output_error')
        self.assertFalse(result['quality_scored'])

    def test_known_question_and_ambiguity_coexist_without_global_completion(self):
        result = self.run_review()
        item = result['projects'][1]
        self.assertEqual(item['status'], 'needs_clarification')
        self.assertEqual(item['review']['readback']['question_id'], 'Q_UI')
        self.assertEqual(item['clarifications'][0]['message_id'], 'N02-m04')
        self.assertEqual(len(item['clarifications'][0]['question_presentations']), 2)
        self.assertEqual(result['status'], 'partial_review')
        self.assertFalse(item['review']['readback']['approved_real_decision'])

    def test_abstain_and_missing_outputs_stay_visible(self):
        self.output['responses'][1].update(status='abstain', readback=None, next_actions=[])
        self.assertEqual(self.run_review()['projects'][1]['status'], 'awaiting_context')
        self.output['responses'].pop()
        result = self.run_review()
        self.assertEqual(result['projects'][1]['status'], 'missing_output')
        self.assertEqual(result['status'], 'partial_review')
        self.output['responses'] = []
        self.assertEqual(self.run_review()['status'], 'awaiting_resolution')

    def test_abstain_with_data_is_error_not_silently_repaired(self):
        self.output['responses'][1]['status'] = 'abstain'
        result = self.run_review()
        self.assertEqual(result['projects'][1]['status'], 'invalid_project_output')
        self.assertIsNotNone(self.output['responses'][1]['readback'])

    def test_bad_envelope_duplicate_keys_foreign_request_and_oversize_fail_globally(self):
        for raw in ('{"request_id":1,"request_id":2}', canonical(dict(self.output, request_id='foreign')),
                    canonical(dict(self.output, extra='execute')), ' ' * 32769):
            with self.assertRaises(ValueError):
                review_projects(self.request, raw, self.context)

    def test_unknown_duplicate_project_and_stale_package_fail_globally(self):
        for kind in ('unknown', 'duplicate', 'package', 'missing_identity'):
            bad = copy.deepcopy(self.output)
            if kind == 'unknown':
                bad['responses'][1]['project_id'] = 'foreign'
            elif kind == 'duplicate':
                bad['responses'][1] = copy.deepcopy(bad['responses'][0])
            elif kind == 'package':
                bad['responses'][1]['package_digest'] = '0' * 64
            else:
                del bad['responses'][1]['project_id']
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.run_review(bad)

    def test_access_denied_missing_or_model_supplied_context_fail_globally(self):
        for kind in ('denied', 'missing', 'supplied_in_model_output'):
            context = copy.deepcopy(self.context)
            output = copy.deepcopy(self.output)
            if kind == 'denied':
                context['projects'][self.p2]['review_access'] = False
            elif kind == 'missing':
                del context['projects'][self.p2]
            else:
                output['context'] = context
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                review_projects(self.request, canonical(output), context)

    def test_current_source_state_and_access_revision_must_match(self):
        for field in ('source_sha256', 'state_sha256', 'authz_revision', 'base_revision'):
            context = copy.deepcopy(self.context)
            context['projects'][self.p2]['current_binding'][field] = 'stale'
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'stale source/state/access'):
                review_projects(self.request, canonical(self.output), context)

    def test_foreign_source_and_unsupported_action_are_project_local_errors(self):
        for field, value in (('message_id', 'N01-m01'), ('type', 'execute_shell')):
            bad = copy.deepcopy(self.output)
            bad['responses'][1]['next_actions'][0][field] = value
            result = self.run_review(bad)
            self.assertEqual(result['projects'][0]['status'], 'ready_for_review')
            self.assertEqual(result['projects'][1]['status'], 'invalid_project_output')

    def test_atomic_group_with_ambiguity_error_or_missing_withholds_all(self):
        self.context['atomic_groups'] = [[self.p1, self.p2]]
        for kind in ('ambiguous', 'invalid', 'missing'):
            bad = copy.deepcopy(self.output)
            if kind == 'invalid':
                bad['responses'][1]['readback']['task_verified'] = True
            elif kind == 'missing':
                bad['responses'].pop()
            result = self.run_review(bad)
            self.assertEqual(result['status'], 'awaiting_resolution')
            self.assertTrue(all(i['review'] is None and i['status'] == 'blocked_atomic_group' for i in result['projects']))

    def test_unknown_duplicate_or_overlapping_atomic_groups_are_rejected(self):
        for groups in ([[self.p1, 'foreign']], [[self.p1, self.p1]], [[self.p1, self.p2], [self.p1, self.p2]]):
            context = copy.deepcopy(self.context)
            context['atomic_groups'] = groups
            with self.assertRaises(ValueError):
                review_projects(self.request, canonical(self.output), context)

    def test_fully_ready_atomic_group_is_reviewed_together_without_execution(self):
        # A fresh in-memory synthetic source omits the ambiguous fourth message.
        view = self.request['views'][1]
        view['source_messages'] = [m for m in view['source_messages'] if m['message_id'] != 'N02-m04']
        view['preserved_records'] = [r for r in view['preserved_records'] if r['message_id'] != 'N02-m04']
        view['answer_candidates'] = [c for c in view['answer_candidates'] if c['message_id'] != 'N02-m04']
        view['binding']['source_sha256'] = digest(view['source_messages'])
        view['binding']['package_digest'] = digest({k: v for k, v in view.items() if k != 'binding'})
        rebind_fixture(self.request)
        self.context = fixture_context(self.request)
        self.context['atomic_groups'] = [[self.p1, self.p2]]
        self.output['request_id'] = self.request['request_id']
        row = self.output['responses'][1]
        row['package_digest'] = view['binding']['package_digest']
        row['readback']['answer_states'] = [a for a in row['readback']['answer_states'] if a['message_id'] != 'N02-m04']
        row['next_actions'] = [a for a in row['next_actions'] if a['message_id'] != 'N02-m04']
        result = self.run_review()
        self.assertEqual(result['status'], 'ready_for_review')
        self.assertTrue(all(i['review'] is not None for i in result['projects']))
        self.assertEqual(result['atomic_groups'], [[self.p1, self.p2]])
        self.assertFalse(result['execution_authorized'])
        self.assertFalse(result['quality_scored'])

    def test_delayed_reply_after_access_revocation_or_source_change_is_rejected(self):
        question, reply = self.reply()
        for kind in ('revoke', 'source'):
            context = copy.deepcopy(self.context)
            if kind == 'revoke':
                context['projects'][self.p2]['review_access'] = False
            else:
                context['projects'][self.p2]['current_binding']['source_sha256'] = 'changed'
            with self.assertRaises(ValueError):
                associate_reply(self.request, context, question['clarification_id'], reply)

    def test_clarification_id_is_stable_and_reply_does_not_clear_pending_state(self):
        question, reply = self.reply()
        before = copy.deepcopy((self.request, self.context, reply))
        first = associate_reply(self.request, self.context, question['clarification_id'], reply)
        second = associate_reply(self.request, self.context, question['clarification_id'], reply)
        self.assertEqual(first, second)
        self.assertEqual(first['status'], 'pending_trusted_selection')
        self.assertFalse(first['clarification_resolved'])
        self.assertFalse(first['approved_real_decision'])
        self.assertEqual(first['binding'], self.request['views'][1]['binding'])
        self.assertEqual(first['source_message_id'], reply['source_message_id'])
        self.assertEqual(first['request_id'], self.request['request_id'])
        self.assertEqual(clarification_records(self.request, self.request['views'][1])[0], question)
        self.assertEqual((self.request, self.context, reply), before)

    def test_delayed_reply_foreign_question_option_revision_or_id_does_not_associate(self):
        question, reply = self.reply()
        for field, value in (('project_id', self.p1), ('question_id', 'foreign'),
                             ('question_revision', 2), ('option_id', 'Z'), ('clarification_id', 'foreign')):
            bad = dict(reply, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                associate_reply(self.request, self.context, question['clarification_id'], bad)

    def test_agent_reply_bad_source_and_coerced_revision_do_not_associate(self):
        question, reply = self.reply()
        for field, value in (('actor_type', 'agent'), ('source_sha256', 'wrong'),
                             ('question_revision', '1'), ('question_revision', True), ('source_revision', True)):
            bad = dict(reply, **{field: value})
            if field == 'actor_type':
                bad['source_sha256'] = digest({k: bad[k] for k in ('source_message_id', 'source_revision', 'text', 'actor_type')})
            with self.subTest(field=field), self.assertRaises(ValueError):
                associate_reply(self.request, self.context, question['clarification_id'], bad)

    def test_known_presentation_without_current_question_needs_more_context(self):
        question, reply = self.reply()
        reply.update(question_id='Q_RELEASE', option_id='B')
        result = associate_reply(self.request, self.context, question['clarification_id'], reply)
        self.assertEqual(result['status'], 'needs_question_context')
        self.assertFalse(result['approved_real_decision'])

    def test_resolved_question_and_old_clarification_snapshot_do_not_apply(self):
        old, reply = self.reply()
        self.request['views'][1]['fixture_state']['question']['state'] = 'resolved'
        self.request['views'][1]['binding']['base_revision'] += 1
        rebind_fixture(self.request)
        self.context = fixture_context(self.request)
        new = clarification_records(self.request, self.request['views'][1])[0]
        reply['clarification_id'] = new['clarification_id']
        with self.assertRaisesRegex(ValueError, 'already resolved'):
            associate_reply(self.request, self.context, new['clarification_id'], reply)
        reply['clarification_id'] = old['clarification_id']
        with self.assertRaisesRegex(ValueError, 'unknown/stale clarification'):
            associate_reply(self.request, self.context, old['clarification_id'], reply)

    def test_first_failed_model_output_is_not_salvaged_into_success(self):
        raw = (ROOT / 'docs/quality/model-runs/receiver-001-response.txt').read_text()
        result = review_projects(self.request, raw, self.context)
        self.assertEqual(result['status'], 'awaiting_resolution')
        self.assertTrue(all(i['status'] == 'invalid_project_output' for i in result['projects']))
        oracle = json.loads((ROOT / 'examples/receiver-smoke/expected.json').read_text())
        with self.assertRaisesRegex(ValueError, 'invalid receiver abstention'):
            evaluate(self.request, raw, oracle)
        self.assertEqual(result['raw_sha256'], 'f17e134b68bec39cf7d5539cc812db7a87bd970a851aa30ecf2b43aaeaac4b03')

    def test_output_request_context_unchanged_and_review_detached_from_input(self):
        before = copy.deepcopy((self.request, self.context, self.output))
        result = self.run_review()
        self.assertEqual((self.request, self.context, self.output), before)
        self.assertFalse(result['execution_authorized'])
        self.assertEqual(result['canonical_mutations'], 0)
        self.assertEqual(result['model_dispatches'], 0)
        result['projects'][0]['review']['next_actions'].clear()
        self.assertEqual((self.request, self.context, self.output), before)


if __name__ == '__main__':
    unittest.main()
