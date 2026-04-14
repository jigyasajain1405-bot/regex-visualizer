"""
nfa_to_dfa.py
-------------
Converts an ε-NFA to a DFA using the Subset Construction algorithm.

Key concepts:
  - ε-closure: the set of all states reachable from a state using ONLY ε transitions
  - move(states, symbol): all states reachable from a set of states on a given symbol
  - Each DFA state represents a SUBSET of NFA states

The DFA is represented as:
  - states: list of frozenset (each is a subset of NFA states)
  - transitions: dict { frozenset: { symbol: frozenset } }
  - start_state: frozenset
  - accept_states: set of frozensets (any subset containing the NFA's accept state)
  - state_labels: dict { frozenset: readable string label }
"""

EPSILON = 'ε'


def epsilon_closure(nfa_transitions, states):
    """
    Compute ε-closure of a set of NFA states.
    Returns the set of all states reachable via ε transitions (including the states themselves).
    Uses iterative DFS/BFS.
    """
    closure = set(states)
    stack = list(states)

    while stack:
        state = stack.pop()
        eps_targets = nfa_transitions.get(state, {}).get(EPSILON, [])
        for next_state in eps_targets:
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)

    return frozenset(closure)


def move(nfa_transitions, states, symbol):
    """
    Compute the set of NFA states reachable from `states` on `symbol` (not ε).
    """
    reachable = set()
    for state in states:
        targets = nfa_transitions.get(state, {}).get(symbol, [])
        reachable.update(targets)
    return reachable


def get_alphabet(nfa):
    """Extract all symbols used in the NFA (excluding ε)."""
    alphabet = set()
    for state_transitions in nfa['transitions'].values():
        for symbol in state_transitions:
            if symbol != EPSILON:
                alphabet.add(symbol)
    return sorted(alphabet)


def nfa_to_dfa(nfa):
    """
    Main function: Subset Construction to convert ε-NFA → DFA.

    Returns a dict:
      - dfa_transitions: { frozenset → { symbol → frozenset } }
      - start_state: frozenset
      - accept_states: set of frozenset
      - all_states: list of all DFA states (frozensets)
      - alphabet: list of input symbols
      - state_labels: { frozenset → display string }
    """
    transitions = nfa['transitions']
    nfa_accept = nfa['accept']
    alphabet = get_alphabet(nfa)

    # DFA start state = ε-closure of NFA start state
    start = epsilon_closure(transitions, {nfa['start']})

    # BFS / worklist algorithm
    unprocessed = [start]
    visited = {start}
    dfa_transitions = {}
    accept_states = set()

    while unprocessed:
        current = unprocessed.pop(0)

        # Check if this DFA state is an accept state
        if nfa_accept in current:
            accept_states.add(current)

        dfa_transitions[current] = {}

        for symbol in alphabet:
            # Compute move then ε-closure
            moved = move(transitions, current, symbol)
            next_state = epsilon_closure(transitions, moved)

            if not next_state:
                # Dead/trap state — we can skip or represent as empty set
                next_state = frozenset()

            dfa_transitions[current][symbol] = next_state

            if next_state and next_state not in visited:
                visited.add(next_state)
                unprocessed.append(next_state)

    # Build readable labels for DFA states: {q0,q1} → "D0", "D1", etc.
    all_states = list(visited)
    state_labels = {}
    for i, state in enumerate(all_states):
        state_labels[state] = f"D{i}"

    # Label the start state clearly
    state_labels[start] = "D0 (start)"

    return {
        'dfa_transitions': dfa_transitions,
        'start_state': start,
        'accept_states': accept_states,
        'all_states': all_states,
        'alphabet': alphabet,
        'state_labels': state_labels
    }


def simulate_dfa(dfa, input_string):
    """
    Simulate the DFA on an input string.
    Returns (accepted: bool, path: list of state labels)
    """
    current = dfa['start_state']
    path = [dfa['state_labels'].get(current, str(set(current)))]

    for symbol in input_string:
        if symbol not in dfa['alphabet']:
            return False, path + [f"[ERROR: '{symbol}' not in alphabet]"]

        transitions = dfa['dfa_transitions'].get(current, {})
        next_state = transitions.get(symbol, frozenset())

        if not next_state:
            return False, path + ["[DEAD STATE]"]

        current = next_state
        path.append(dfa['state_labels'].get(current, str(set(current))))

    accepted = current in dfa['accept_states']
    return accepted, path


def simulate_nfa(nfa, input_string):
    """
    Simulate the ε-NFA on an input string using subset construction on-the-fly.
    Returns (accepted: bool, path: list of state set descriptions)
    """
    transitions = nfa['transitions']
    current_states = epsilon_closure(transitions, {nfa['start']})
    path = [f"{{{', '.join(sorted(current_states))}}}"]

    for symbol in input_string:
        moved = move(transitions, current_states, symbol)
        current_states = epsilon_closure(transitions, moved)
        path.append(f"{{{', '.join(sorted(current_states))}}}")
        if not current_states:
            return False, path

    accepted = nfa['accept'] in current_states
    return accepted, path
