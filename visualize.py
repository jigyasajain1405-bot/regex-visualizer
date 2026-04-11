"""
visualize.py
------------
Generates Graphviz DOT diagrams for ε-NFA and DFA.

Uses the `graphviz` Python library to render:
  - States as circles (double circle for accept states)
  - Start state with an arrow from an invisible node
  - Epsilon transitions shown as dashed edges labeled 'ε'
  - Regular transitions shown as solid edges

Returns graphviz.Digraph objects that Streamlit can render as SVG.
"""

import graphviz

EPSILON = 'ε'


def visualize_nfa(nfa, title="ε-NFA (Thompson's Construction)"):
    """
    Build a Graphviz diagram for an ε-NFA.

    Args:
        nfa: dict with keys: states, transitions, start, accept
        title: diagram title shown as graph label

    Returns:
        graphviz.Digraph object
    """
    dot = graphviz.Digraph(
        name="NFA",
        graph_attr={
            'rankdir': 'LR',        # Left to Right layout
            'label': title,
            'labelloc': 't',        # Label at top
            'fontsize': '16',
            'fontname': 'Helvetica',
            'bgcolor': 'transparent'
        },
        node_attr={
            'fontname': 'Helvetica',
            'fontsize': '12'
        },
        edge_attr={
            'fontname': 'Helvetica',
            'fontsize': '11'
        }
    )

    start = nfa['start']
    accept = nfa['accept']

    # Invisible start arrow
    dot.node('__start__', shape='none', label='', width='0', height='0')
    dot.edge('__start__', start, label='start', style='bold', color='#2ecc71')

    # Add all states
    for state in sorted(nfa['states']):
        if state == accept:
            # Accept state: double circle, filled green
            dot.node(state, state,
                     shape='doublecircle',
                     style='filled',
                     fillcolor='#2ecc71',
                     color='#27ae60',
                     fontcolor='white')
        elif state == start:
            # Start state: filled blue
            dot.node(state, state,
                     shape='circle',
                     style='filled',
                     fillcolor='#3498db',
                     color='#2980b9',
                     fontcolor='white')
        else:
            # Regular state: light gray
            dot.node(state, state,
                     shape='circle',
                     style='filled',
                     fillcolor='#ecf0f1',
                     color='#bdc3c7')

    # Add transitions
    for state, trans in nfa['transitions'].items():
        for symbol, targets in trans.items():
            for target in targets:
                if symbol == EPSILON:
                    # Epsilon: dashed gray edge
                    dot.edge(state, target,
                             label='ε',
                             style='dashed',
                             color='#95a5a6',
                             fontcolor='#7f8c8d')
                else:
                    # Regular: solid colored edge
                    dot.edge(state, target,
                             label=symbol,
                             color='#e74c3c',
                             fontcolor='#c0392b',
                             penwidth='2')

    return dot


def visualize_dfa(dfa, title="DFA (Subset Construction)"):
    """
    Build a Graphviz diagram for a DFA.

    Args:
        dfa: dict returned by nfa_to_dfa() with keys:
             dfa_transitions, start_state, accept_states,
             all_states, alphabet, state_labels
        title: diagram title

    Returns:
        graphviz.Digraph object
    """
    dot = graphviz.Digraph(
        name="DFA",
        graph_attr={
            'rankdir': 'LR',
            'label': title,
            'labelloc': 't',
            'fontsize': '16',
            'fontname': 'Helvetica',
            'bgcolor': 'transparent'
        },
        node_attr={
            'fontname': 'Helvetica',
            'fontsize': '12'
        },
        edge_attr={
            'fontname': 'Helvetica',
            'fontsize': '11'
        }
    )

    labels = dfa['state_labels']
    start = dfa['start_state']
    accept_states = dfa['accept_states']

    # Invisible start arrow
    dot.node('__start__', shape='none', label='', width='0', height='0')
    dot.edge('__start__', labels[start], label='start', style='bold', color='#2ecc71')

    # Add all DFA states
    for state in dfa['all_states']:
        label = labels[state]
        # Show which NFA states this DFA state contains (tooltip-style)
        nfa_states_str = "{" + ", ".join(sorted(state)) + "}" if state else "∅"

        if state in accept_states:
            dot.node(label,
                     f"{label}\n{nfa_states_str}",
                     shape='doublecircle',
                     style='filled',
                     fillcolor='#2ecc71',
                     color='#27ae60',
                     fontcolor='white')
        elif state == start:
            dot.node(label,
                     f"{label}\n{nfa_states_str}",
                     shape='circle',
                     style='filled',
                     fillcolor='#3498db',
                     color='#2980b9',
                     fontcolor='white')
        else:
            dot.node(label,
                     f"{label}\n{nfa_states_str}",
                     shape='circle',
                     style='filled',
                     fillcolor='#ecf0f1',
                     color='#bdc3c7')

    # Add DFA transitions
    # Group edges with multiple labels (for cleaner diagrams)
    edge_labels = {}
    for state, trans in dfa['dfa_transitions'].items():
        for symbol, next_state in trans.items():
            if not next_state:
                continue  # skip dead state transitions
            key = (labels[state], labels[next_state])
            edge_labels.setdefault(key, []).append(symbol)

    for (src, dst), symbols in edge_labels.items():
        dot.edge(src, dst,
                 label=', '.join(sorted(symbols)),
                 color='#e74c3c',
                 fontcolor='#c0392b',
                 penwidth='2')

    return dot


def get_nfa_table(nfa):
    """
    Build a transition table for the ε-NFA as a list of dicts (for Streamlit dataframe).
    """
    transitions = nfa['transitions']
    # Collect all symbols
    symbols = set()
    for trans in transitions.values():
        symbols.update(trans.keys())
    symbols = sorted(symbols, key=lambda s: (s == EPSILON, s))

    rows = []
    for state in sorted(nfa['states']):
        row = {'State': state}
        for sym in symbols:
            targets = transitions.get(state, {}).get(sym, [])
            row[sym if sym != EPSILON else 'ε'] = '{' + ', '.join(sorted(targets)) + '}' if targets else '∅'
        rows.append(row)
    return rows


def get_dfa_table(dfa):
    """
    Build a transition table for the DFA as a list of dicts (for Streamlit dataframe).
    """
    labels = dfa['state_labels']
    rows = []
    for state in dfa['all_states']:
        row = {'DFA State': labels[state], 'NFA States': '{' + ', '.join(sorted(state)) + '}'}
        for sym in dfa['alphabet']:
            next_state = dfa['dfa_transitions'].get(state, {}).get(sym, frozenset())
            row[sym] = labels.get(next_state, '∅') if next_state else '∅'
        row['Accept?'] = '✅' if state in dfa['accept_states'] else '❌'
        rows.append(row)
    return rows
