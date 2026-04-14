"""
visualize.py
------------
Clean Graphviz diagrams for ε-NFA and DFA.

Design rules:
  - Left-to-right layout
  - Blue start state, green accept state, gray regular states
  - Epsilon: dashed gray edges
  - Symbol: solid red edges (grouped per pair to avoid clutter)
  - DFA labels: q0, q1, q2 … (no subset notation in node body)
  - Transparent background (works in both light and dark mode)
"""

import graphviz

EPSILON = 'ε'


def _base_graph(name, title):
    return graphviz.Digraph(
        name=name,
        graph_attr={
            'rankdir':  'LR',
            'label':    title,
            'labelloc': 't',
            'fontsize': '14',
            'fontname': 'Helvetica',
            'bgcolor':  'transparent',
            'nodesep':  '0.5',
            'ranksep':  '0.6',
        },
        node_attr={'fontname': 'Helvetica', 'fontsize': '12'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '11'},
    )


def _add_states(dot, states, start, accept):
    dot.node('__arrow__', shape='none', label='', width='0', height='0')
    dot.edge('__arrow__', start, arrowhead='normal', color='#555555')

    for s in sorted(states):
        if s == accept:
            dot.node(s, s, shape='doublecircle', style='filled',
                     fillcolor='#27ae60', color='#1e8449', fontcolor='white')
        elif s == start:
            dot.node(s, s, shape='circle', style='filled',
                     fillcolor='#2980b9', color='#1a5276', fontcolor='white')
        else:
            dot.node(s, s, shape='circle', style='filled',
                     fillcolor='#d5d8dc', color='#808b96', fontcolor='#17202a')


def _add_nfa_edges(dot, transitions):
    # Group labels per (src, dst) pair to avoid parallel edges
    edge_map = {}
    for src, trans in transitions.items():
        for sym, targets in trans.items():
            for dst in targets:
                edge_map.setdefault((src, dst), []).append(sym)

    for (src, dst), syms in edge_map.items():
        eps_syms  = [s for s in syms if s == EPSILON]
        real_syms = [s for s in syms if s != EPSILON]

        if real_syms:
            dot.edge(src, dst,
                     label=', '.join(sorted(real_syms)),
                     color='#c0392b', fontcolor='#c0392b', penwidth='2.0')
        if eps_syms:
            dot.edge(src, dst,
                     label='ε',
                     style='dashed', color='#7f8c8d', fontcolor='#7f8c8d')


def visualize_nfa(nfa, title="ε-NFA (Thompson's Construction)"):
    dot = _base_graph("NFA", title)
    _add_states(dot, nfa['states'], nfa['start'], nfa['accept'])
    _add_nfa_edges(dot, nfa['transitions'])
    return dot


def visualize_dfa(dfa, title="Minimized DFA"):
    dot    = _base_graph("DFA", title)
    labels = dfa['state_labels']
    start  = dfa['start_state']
    accept = dfa['accept_states']

    dot.node('__arrow__', shape='none', label='', width='0', height='0')
    dot.edge('__arrow__', labels[start], arrowhead='normal', color='#555555')

    for s in dfa['all_states']:
        lbl = labels[s]
        if s in accept:
            dot.node(lbl, lbl, shape='doublecircle', style='filled',
                     fillcolor='#27ae60', color='#1e8449', fontcolor='white')
        elif s == start:
            dot.node(lbl, lbl, shape='circle', style='filled',
                     fillcolor='#2980b9', color='#1a5276', fontcolor='white')
        else:
            dot.node(lbl, lbl, shape='circle', style='filled',
                     fillcolor='#d5d8dc', color='#808b96', fontcolor='#17202a')

    # Group edges
    edge_map = {}
    for s, trans in dfa['dfa_transitions'].items():
        for sym, nxt in trans.items():
            if not nxt:
                continue
            key = (labels[s], labels[nxt])
            edge_map.setdefault(key, []).append(sym)

    for (src, dst), syms in edge_map.items():
        dot.edge(src, dst,
                 label=', '.join(sorted(syms)),
                 color='#c0392b', fontcolor='#c0392b', penwidth='2.0')

    return dot


def get_nfa_table(nfa):
    trans   = nfa['transitions']
    symbols = set()
    for t in trans.values():
        symbols.update(t.keys())
    symbols = sorted(symbols, key=lambda s: (s == EPSILON, s))

    rows = []
    for state in sorted(nfa['states']):
        row = {'State': state}
        for sym in symbols:
            tgts = trans.get(state, {}).get(sym, [])
            col  = 'ε' if sym == EPSILON else sym
            row[col] = ('{' + ', '.join(sorted(tgts)) + '}') if tgts else '∅'
        rows.append(row)
    return rows


def get_dfa_table(dfa):
    labels = dfa['state_labels']
    rows   = []
    for s in dfa['all_states']:
        row = {'State': labels[s]}
        for sym in dfa['alphabet']:
            nxt = dfa['dfa_transitions'].get(s, {}).get(sym, frozenset())
            row[sym] = labels.get(nxt, '∅') if nxt else '∅'
        row['Accept?'] = '✅' if s in dfa['accept_states'] else '❌'
        rows.append(row)
    return rows
