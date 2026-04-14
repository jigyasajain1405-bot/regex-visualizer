"""
nfa_to_dfa.py
-------------
Converts an ε-NFA to a minimized DFA.

Steps:
  1. Subset Construction  (ε-NFA → DFA)
  2. State Minimization   (Myhill-Nerode / table-filling)

State labels use simple q0, q1, q2 … NOT subset labels like {q0,q2}.
"""

EPSILON = 'ε'


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def epsilon_closure(nfa_transitions, states):
    closure = set(states)
    stack = list(states)
    while stack:
        s = stack.pop()
        for t in nfa_transitions.get(s, {}).get(EPSILON, []):
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return frozenset(closure)


def move(nfa_transitions, states, symbol):
    reachable = set()
    for s in states:
        reachable.update(nfa_transitions.get(s, {}).get(symbol, []))
    return reachable


def get_alphabet(nfa):
    alpha = set()
    for trans in nfa['transitions'].values():
        for sym in trans:
            if sym != EPSILON:
                alpha.add(sym)
    return sorted(alpha)


# ─────────────────────────────────────────────
# Subset Construction
# ─────────────────────────────────────────────

def subset_construction(nfa):
    trans  = nfa['transitions']
    accept = nfa['accept']
    alpha  = get_alphabet(nfa)

    start = epsilon_closure(trans, {nfa['start']})
    queue = [start]
    visited = {start}
    dfa_trans = {}
    accept_states = set()

    while queue:
        cur = queue.pop(0)
        if accept in cur:
            accept_states.add(cur)
        dfa_trans[cur] = {}
        for sym in alpha:
            nxt = epsilon_closure(trans, move(trans, cur, sym))
            dfa_trans[cur][sym] = nxt if nxt else frozenset()
            if nxt and nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)

    return {
        'raw_trans': dfa_trans,
        'start': start,
        'accept_states': accept_states,
        'all_states': list(visited),
        'alphabet': alpha,
    }


# ─────────────────────────────────────────────
# DFA Minimization (Myhill-Nerode table-filling)
# ─────────────────────────────────────────────

def minimize_dfa(raw):
    states       = raw['all_states']
    alpha        = raw['alphabet']
    accept_set   = raw['accept_states']
    raw_trans    = raw['raw_trans']
    start        = raw['start']

    # Remove unreachable states
    reachable = set()
    queue = [start]
    while queue:
        s = queue.pop()
        if s in reachable:
            continue
        reachable.add(s)
        for sym in alpha:
            nxt = raw_trans.get(s, {}).get(sym, frozenset())
            if nxt and nxt not in reachable:
                queue.append(nxt)
    states = [s for s in states if s in reachable]

    if not states:
        return raw  # nothing to minimize

    # Initial partition: accepting vs non-accepting
    acc     = frozenset(s for s in states if s in accept_set)
    non_acc = frozenset(s for s in states if s not in accept_set)
    partition = set()
    if acc:     partition.add(acc)
    if non_acc: partition.add(non_acc)

    def get_group(state, part):
        for g in part:
            if state in g:
                return g
        return None

    # Refine partition
    changed = True
    while changed:
        changed = False
        new_part = set()
        for group in partition:
            splits = {}
            for s in group:
                sig = tuple(
                    id(get_group(raw_trans.get(s, {}).get(sym, frozenset()), partition))
                    if raw_trans.get(s, {}).get(sym, frozenset()) else -1
                    for sym in alpha
                )
                splits.setdefault(sig, set()).add(s)
            for sub in splits.values():
                new_part.add(frozenset(sub))
            if len(splits) > 1:
                changed = True
        partition = new_part

    # Build minimized DFA
    # Representative of each group = first element (sorted)
    def rep(group):
        return sorted(group, key=lambda x: sorted(x))[0]

    # Map each original state → its group representative
    state_to_rep = {}
    for group in partition:
        r = rep(group)
        for s in group:
            state_to_rep[s] = r

    min_start   = state_to_rep[start]
    min_states  = list(set(state_to_rep.values()))
    min_accept  = set(state_to_rep[s] for s in states if s in accept_set)
    min_trans   = {}
    for group in partition:
        r = rep(group)
        min_trans[r] = {}
        for sym in alpha:
            raw_nxt = raw_trans.get(r, {}).get(sym, frozenset())
            if raw_nxt and raw_nxt in state_to_rep:
                min_trans[r][sym] = state_to_rep[raw_nxt]
            else:
                min_trans[r][sym] = frozenset()

    # Assign clean labels q0, q1, q2 …  (start = q0)
    ordered = [min_start] + [s for s in min_states if s != min_start]
    labels  = {s: f"q{i}" for i, s in enumerate(ordered)}

    return {
        'dfa_transitions': min_trans,
        'start_state':     min_start,
        'accept_states':   min_accept,
        'all_states':      ordered,
        'alphabet':        alpha,
        'state_labels':    labels,
    }


def nfa_to_dfa(nfa):
    """Full pipeline: NFA → subset DFA → minimized DFA."""
    raw = subset_construction(nfa)
    return minimize_dfa(raw)


# ─────────────────────────────────────────────
# Simulation
# ─────────────────────────────────────────────

def simulate_dfa(dfa, input_string):
    current = dfa['start_state']
    labels  = dfa['state_labels']
    path    = [labels.get(current, '?')]

    for sym in input_string:
        if sym not in dfa['alphabet']:
            return False, path + [f"['{sym}' not in alphabet]"]
        nxt = dfa['dfa_transitions'].get(current, {}).get(sym, frozenset())
        if not nxt:
            return False, path + ["[dead state]"]
        current = nxt
        path.append(labels.get(current, '?'))

    return current in dfa['accept_states'], path


def simulate_nfa(nfa, input_string):
    trans = nfa['transitions']
    cur   = epsilon_closure(trans, {nfa['start']})
    path  = ["{" + ", ".join(sorted(cur)) + "}"]

    for sym in input_string:
        cur = epsilon_closure(trans, move(trans, cur, sym))
        path.append("{" + ", ".join(sorted(cur)) + "}")
        if not cur:
            return False, path

    return nfa['accept'] in cur, path
