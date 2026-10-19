"""Scoped, deterministic structural audit. Missing links never cancel tasks."""
import json
class OrphanAudit:
    def __init__(self,core):self.core=core
    def run(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            records=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 1001',(self.core.workspace,project)).fetchall()
            edges=self.core.db.execute('SELECT origin,target,kind,revision,state FROM edges WHERE workspace=? AND project=? ORDER BY origin,target,kind LIMIT 5001',(self.core.workspace,project)).fetchall()
            partial=len(records)>1000 or len(edges)>5000;records=records[:1000];edges=edges[:5000];by_id={r[0]:dict(version=r[1],body=json.loads(r[2])) for r in records};findings=[]
            for rid,record in by_id.items():
                if record['body']['type']!='Task':continue
                rationale=[e for e in edges if e[0]==rid and e[2]=='required_by'];active=[e for e in rationale if e[4]=='asserted']
                if not active:findings.append(dict(record=rid,version=record['version'],kind='no_active_rationale_in_snapshot',retired_edges=sum(e[4]!='asserted' for e in rationale),certainty='partial_snapshot' if partial else 'structural_only',suggested_action='review',auto_cancel=False))
            for origin,target,kind,revision,state in edges:
                if state=='asserted' and (origin not in by_id or target not in by_id):findings.append(dict(origin=origin,target=target,kind='endpoint_outside_snapshot' if partial else 'missing_endpoint',relation=kind,edge_revision=revision,suggested_action='review',auto_cancel=False))
            return dict(project=project,knowledge_revision=self.core.project(scope,project)['knowledge_revision'],coverage='partial' if partial else 'complete_structural_snapshot',records_examined=len(records),edges_examined=len(edges),findings=findings,semantic_equivalence_verified=False,canonical_mutations=0,model_calls=0)
