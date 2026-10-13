"""T11 typed graph and baseline unblock tests, no human/capture quality claims."""
import unittest
from packages.impact.graph import rationale,DependencyGraph
from packages.domain.source_event import ContractError


class GraphTests(unittest.TestCase):
    def test_any_all_truth_tables_and_unknown_revision(self):
        for a in (True,False,None):
            for b in (True,False,None):
                facts={'a':dict(revision=1,valid=a),'b':dict(revision=1,valid=b)}
                leaves=[dict(ref='a',revision=1),dict(ref='b',revision=1)]
                self.assertIs(rationale({'any':leaves},facts),True if a is True or b is True else None if a is None or b is None else False)
                self.assertIs(rationale({'all':leaves},facts),False if a is False or b is False else None if a is None or b is None else True)
        self.assertIsNone(rationale(dict(ref='a',revision=2),{'a':dict(revision=1,valid=True)}))
        self.assertIsNone(rationale({'any':[]},{}))

    def test_required_by_is_not_execution_dependency(self):
        graph=DependencyGraph({'task':{'eligible':True},'decision':{}},complete=True)
        graph.add('task','decision','required_by')
        self.assertEqual(graph.prerequisites('task'),[])
        self.assertTrue(graph.assessment('task')['ready'])

    def test_dependency_and_supersedes_cycles_are_rejected_without_mutation(self):
        for kind in ('depends_on','supersedes'):
            graph=DependencyGraph({'a':{},'b':{},'c':{}})
            graph.add('a','b',kind);graph.add('b','c',kind)
            with self.assertRaises(ContractError):graph.add('c','a',kind)
            self.assertEqual(len(graph.edges),2)
            with self.assertRaises(ContractError):graph.add('a','a',kind)

    def test_related_to_cycles_allowed_and_missing_endpoint_rejected(self):
        graph=DependencyGraph({'a':{},'b':{}})
        graph.add('a','b','related_to');graph.add('b','a','related_to')
        with self.assertRaises(ContractError):graph.add('a','missing','required_by')

    def test_unknown_or_incomplete_snapshot_never_ready(self):
        graph=DependencyGraph({'a':{'eligible':True},'b':{'verification':'unknown'}},complete=True)
        graph.add('a','b','depends_on')
        self.assertFalse(graph.assessment('a')['ready'])
        other=DependencyGraph({'a':{'eligible':True}},complete=False)
        self.assertFalse(other.assessment('a')['ready'])

    def test_forty_task_baseline_prioritizes_unique_downstream_blocker(self):
        nodes={f't{i:02}':{'eligible':True} for i in range(40)}
        graph=DependencyGraph(nodes,complete=True,revision=7)
        for i in range(1,40):graph.add(f't{i:02}','t00','depends_on')
        graph.add('t02','t01','depends_on')
        ranked=graph.rank()
        self.assertEqual((ranked[0]['task'],ranked[0]['unblocks']),('t00',39))
        self.assertEqual(ranked[0]['assessment']['graph_revision'],7)
        self.assertEqual(ranked[0]['assessment']['canonical_mutations'],0)

    def test_depth_and_node_budget_fail_closed(self):
        expression={'ref':'a','revision':1}
        for _ in range(20):expression={'all':[expression]}
        with self.assertRaises(ContractError):rationale(expression,{'a':dict(revision=1,valid=True)})
        with self.assertRaises(ContractError):DependencyGraph({'a':{},'b':{}},max_nodes=1)


if __name__=='__main__':unittest.main()
