"""Typed graph, three-valued rationale and deterministic unblock ranking."""
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError

KINDS={'depends_on','required_by','supersedes','related_to','part_of','refines','conflicts_with','implements'}


def rationale(expression, facts, *, depth=0):
    if depth>16:raise ContractError('graph_limit','Rationale nesting exceeds the local limit.')
    if type(expression) is not dict:return None
    if set(expression)=={'ref','revision'}:
        identifier(expression['ref'])
        fact=facts.get(expression['ref'])
        if type(expression['revision']) is not int or expression['revision']<1 or type(fact) is not dict or type(fact.get('revision')) is not int or fact.get('revision')!=expression['revision']:
            return None
        value=fact.get('valid')
        return value if value is None or type(value) is bool else None
    if len(expression)!=1 or next(iter(expression)) not in ('any','all'):return None
    mode=next(iter(expression));children=expression[mode]
    if type(children) is not list or not 1<=len(children)<=64:return None
    values=[rationale(child,facts,depth=depth+1) for child in children]
    if mode=='any':return True if True in values else None if None in values else False
    return False if False in values else None if None in values else True


class DependencyGraph:
    def __init__(self,nodes,*,complete=False,revision=1,max_nodes=10000,max_edges=20000):
        if type(nodes) is not dict or len(nodes)>max_nodes or type(complete) is not bool or type(revision) is not int or revision<1:
            raise ContractError('graph_limit','Invalid bounded graph snapshot.')
        for node in nodes:identifier(node)
        self.nodes=dict(nodes);self.edges=set();self.complete=complete;self.revision=revision;self.max_edges=max_edges

    def add(self,origin,target,kind):
        identifier(origin);identifier(target)
        if kind not in KINDS or origin not in self.nodes or target not in self.nodes:
            raise ContractError('invalid_edge','Typed edge must reference this graph snapshot.')
        if len(self.edges)>=self.max_edges:raise ContractError('graph_limit','Graph edge limit reached.')
        if kind in ('depends_on','supersedes'):
            pending=[target];seen=set()
            while pending:
                node=pending.pop()
                if node==origin:raise ContractError('graph_cycle','Dependency or supersession cycle rejected.')
                if node in seen:continue
                seen.add(node)
                pending.extend(b for a,b,k in self.edges if a==node and k==kind)
        self.edges.add((origin,target,kind))

    def prerequisites(self,task):
        identifier(task)
        return sorted(b for a,b,k in self.edges if a==task and k=='depends_on')

    def assessment(self,task):
        if task not in self.nodes:raise ContractError('node_unavailable','Selected task is unavailable.')
        dependencies=self.prerequisites(task)
        blockers=[d for d in dependencies if self.nodes[d].get('verification')!='passed']
        ready=self.nodes[task].get('execution')!='cancelled' and self.complete and not blockers and self.nodes[task].get('eligible') is True
        return dict(task=task,ready=ready,blockers=blockers,coverage='complete_snapshot' if self.complete else 'incomplete',
                    graph_revision=self.revision,execution=self.nodes[task].get('execution','unknown'),reason='task_cancelled' if self.nodes[task].get('execution')=='cancelled' else 'prerequisites_verified' if ready else 'review_or_dependency_pending',canonical_mutations=0)

    def rank(self):
        """Unique downstream unblock count; never a schedule/critical-path estimate."""
        result=[]
        for task,node in self.nodes.items():
            if node.get('verification')=='passed' or node.get('execution')=='cancelled':continue
            pending=[task];downstream=set()
            while pending:
                current=pending.pop()
                for origin,target,kind in self.edges:
                    if kind=='depends_on' and target==current and origin not in downstream:
                        downstream.add(origin);pending.append(origin)
            assessment=self.assessment(task)
            age=node.get('age_seconds',0)
            if type(age) is not int or age<0:age=0
            result.append(dict(task=task,unblocks=len(downstream),assessment=assessment,age_seconds=age,
                priority_reason='Recorded unique downstream blockers first, then age.',
                next_action=task if assessment['ready'] else 'review_context' if not self.complete else assessment['blockers'][0] if assessment['blockers'] else 'review_eligibility'))
        return sorted(result,key=lambda r:(-r['unblocks'],-r['age_seconds'],r['task']))
