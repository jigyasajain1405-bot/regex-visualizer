"""
main.py
-------
Regular Expression → ε-NFA & DFA Visualizer
Run with:  streamlit run main.py
"""

import streamlit as st
import pandas as pd
import graphviz

from regex_to_nfa import (
    regex_to_nfa, reset_states,
    nfa_for_symbol, nfa_concatenation, nfa_union,
    nfa_kleene_star, nfa_plus, nfa_optional,
    EPSILON
)
from nfa_to_dfa import nfa_to_dfa, simulate_dfa, simulate_nfa
from visualize import visualize_nfa, visualize_dfa, get_nfa_table, get_dfa_table

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RE → ε-NFA & DFA Visualizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Theme — stored in session state
# Default = "Auto" which follows OS/browser preference
# ─────────────────────────────────────────────
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Auto'

theme = st.session_state['theme']

# CSS variables per theme
THEMES = {
    'Light': {
        'bg':          '#f8f9fb',
        'card':        '#ffffff',
        'text':        '#1a1a2e',
        'muted':       '#64748b',
        'border':      'rgba(139,92,246,0.2)',
        'step_bg':     'rgba(139,92,246,0.05)',
        'info_bg':     'rgba(139,92,246,0.07)',
        'code_bg':     'rgba(139,92,246,0.08)',
        'sidebar_bg':  '#f1f0ff',
        'input_bg':    '#ffffff',
        'success_bg':  'rgba(16,185,129,0.1)',
        'reject_bg':   'rgba(239,68,68,0.1)',
        'toggle_active': '#7c3aed',
    },
    'Dark': {
        'bg':          '#0d0d1a',
        'card':        '#13132b',
        'text':        '#e2e8f0',
        'muted':       '#94a3b8',
        'border':      'rgba(139,92,246,0.35)',
        'step_bg':     'rgba(139,92,246,0.1)',
        'info_bg':     'rgba(139,92,246,0.12)',
        'code_bg':     'rgba(139,92,246,0.18)',
        'sidebar_bg':  '#111127',
        'input_bg':    '#1e1e3f',
        'success_bg':  'rgba(16,185,129,0.15)',
        'reject_bg':   'rgba(239,68,68,0.15)',
        'toggle_active': '#a78bfa',
    },
}

# Auto = use CSS media query to detect system preference
def get_css(theme_name):
    def _vars(t):
        v = THEMES[t]
        return f"""
        --bg:         {v['bg']};
        --card:       {v['card']};
        --text:       {v['text']};
        --muted:      {v['muted']};
        --border:     {v['border']};
        --step-bg:    {v['step_bg']};
        --info-bg:    {v['info_bg']};
        --code-bg:    {v['code_bg']};
        --sidebar-bg: {v['sidebar_bg']};
        --input-bg:   {v['input_bg']};
        --success-bg: {v['success_bg']};
        --reject-bg:  {v['reject_bg']};
        """

    if theme_name == 'Auto':
        vars_block = f"""
        :root {{  {_vars('Light')} }}
        @media (prefers-color-scheme: dark) {{
          :root {{ {_vars('Dark')} }}
        }}
        """
    elif theme_name == 'Dark':
        vars_block = f":root {{ {_vars('Dark')} }}"
    else:
        vars_block = f":root {{ {_vars('Light')} }}"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Poppins:wght@400;600;800&display=swap');

{vars_block}

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif !important;
    color: var(--text) !important;
}}

/* App background */
.stApp, .main .block-container {{
    background-color: var(--bg) !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] > div {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
}}
section[data-testid="stSidebar"] * {{
    color: var(--text) !important;
}}

/* All text */
p, li, span, label, div {{
    color: var(--text) !important;
}}
h1, h2, h3, h4, h5, h6 {{
    color: var(--text) !important;
}}

/* Input fields */
input, textarea {{
    background-color: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}}

/* DataFrames */
.stDataFrame, [data-testid="stDataFrameResizable"] {{
    background-color: var(--card) !important;
    color: var(--text) !important;
}}
.stDataFrame th, .stDataFrame td {{
    color: var(--text) !important;
    background-color: var(--card) !important;
}}

/* Tabs */
div[data-testid="stTabs"] button {{
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: #8b5cf6 !important;
    border-bottom-color: #8b5cf6 !important;
}}

/* Primary button */
div[data-testid="stButton"] button[kind="primary"] {{
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Poppins', sans-serif !important;
}}

/* Secondary buttons */
div[data-testid="stButton"] button:not([kind="primary"]) {{
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Poppins', sans-serif !important;
}}

/* Code */
code {{
    font-family: 'Fira Code', monospace !important;
    background: var(--code-bg) !important;
    color: #8b5cf6 !important;
    border-radius: 4px !important;
    padding: 0.15em 0.4em !important;
}}
pre, .stCodeBlock {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}}
pre code {{
    color: #a78bfa !important;
}}

/* Expander */
details summary {{
    color: var(--text) !important;
}}

/* ─── Custom components ─── */

.main-title {{
    font-size: 2.4em;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.05em;
    padding-top: 0.2em;
}}
.subtitle {{
    text-align: center;
    color: var(--muted) !important;
    font-size: 0.92em;
    margin-bottom: 1.2em;
    letter-spacing: 0.04em;
}}

/* Theme toggle row */
.theme-row {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    margin-bottom: 4px;
}}
.theme-label {{
    font-size: 12px;
    color: var(--muted) !important;
    font-weight: 500;
}}
.theme-btn {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid var(--border);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    background: var(--card);
    color: var(--muted) !important;
    margin-left: 2px;
    transition: all 0.15s;
}}
.theme-btn.active {{
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
    color: white !important;
    border-color: transparent !important;
}}

.section-header {{
    font-size: 1.2em;
    font-weight: 700;
    color: var(--text) !important;
    border-bottom: 2px solid #8b5cf6;
    padding-bottom: 0.3em;
    margin-top: 0.8em;
    margin-bottom: 0.7em;
}}

.info-box {{
    background: var(--info-bg) !important;
    border-left: 4px solid #8b5cf6;
    padding: 0.85em 1.1em;
    border-radius: 0 10px 10px 0;
    margin: 0.5em 0 0.8em 0;
    color: var(--text) !important;
    font-size: 0.93em;
}}
.info-box * {{ color: var(--text) !important; }}

.step-box {{
    background: var(--step-bg) !important;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1em 1.3em 0.8em 1.3em;
    margin: 0.7em 0;
}}
.step-box * {{ color: var(--text) !important; }}

.step-title {{
    font-size: 1em;
    font-weight: 700;
    color: #8b5cf6 !important;
    margin-bottom: 0.35em;
}}

.step-desc {{
    font-size: 0.88em;
    color: var(--muted) !important;
    margin-bottom: 0.55em;
    line-height: 1.5;
}}

.result-accepted {{
    background: var(--success-bg) !important;
    border-left: 5px solid #10b981;
    padding: 0.9em 1.2em;
    border-radius: 10px;
    font-size: 1.1em;
    font-weight: 600;
    color: #10b981 !important;
    margin: 0.5em 0;
}}
.result-accepted * {{ color: #10b981 !important; }}

.result-rejected {{
    background: var(--reject-bg) !important;
    border-left: 5px solid #ef4444;
    padding: 0.9em 1.2em;
    border-radius: 10px;
    font-size: 1.1em;
    font-weight: 600;
    color: #ef4444 !important;
    margin: 0.5em 0;
}}
.result-rejected * {{ color: #ef4444 !important; }}

.stat-row {{
    display: flex;
    gap: 12px;
    margin: 0.6em 0;
    flex-wrap: wrap;
}}
.stat-card {{
    background: var(--card) !important;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 18px;
    text-align: center;
    min-width: 100px;
}}
.stat-val {{
    font-size: 1.5em;
    font-weight: 800;
    color: #8b5cf6 !important;
}}
.stat-lbl {{
    font-size: 0.75em;
    color: var(--muted) !important;
    margin-top: 2px;
}}
</style>
"""

st.markdown(get_css(theme), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Theme toggle (top right)
# ─────────────────────────────────────────────
tc1, tc2, tc3, tc4 = st.columns([5, 1, 1, 1])
with tc2:
    if st.button("☀️ Light", key="t_light",
                 type="primary" if theme == "Light" else "secondary",
                 use_container_width=True):
        st.session_state['theme'] = 'Light'
        st.rerun()
with tc3:
    if st.button("🌙 Dark", key="t_dark",
                 type="primary" if theme == "Dark" else "secondary",
                 use_container_width=True):
        st.session_state['theme'] = 'Dark'
        st.rerun()
with tc4:
    if st.button("🔄 Auto", key="t_auto",
                 type="primary" if theme == "Auto" else "secondary",
                 use_container_width=True):
        st.session_state['theme'] = 'Auto'
        st.rerun()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">⚡ Regex → ε-NFA & DFA Visualizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Thompson\'s Construction &nbsp;·&nbsp; Subset Construction &nbsp;·&nbsp; Myhill-Nerode Minimization</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📖 How to Use")
    st.markdown("""
1. **Enter** a regex in the input box
2. Click **Convert** to generate automata
3. Browse **ε-NFA / DFA** diagram tabs
4. Open **Construction Steps** for per-step diagrams
5. **Simulate** any string to test acceptance
    """)
    st.markdown("### ✅ Operators")
    st.markdown("""
| Op | Meaning | Example |
|---|---|---|
| `\\|` | Union | `a\\|b` |
| `*` | Kleene star | `a*` |
| `+` | One or more | `a+` |
| `?` | Optional | `a?` |
| `()` | Grouping | `(ab)*` |
    """)
    st.markdown("### 📌 Examples")
    examples = {
        "a|b":          "Matches 'a' or 'b'",
        "a*":           "Zero or more 'a'",
        "a+":           "One or more 'a'",
        "(a|b)*":       "Any string over {a,b}",
        "ab*c":         "a, then b's, then c",
        "(a|b)*abb":    "Ends with 'abb'",
        "a?b":          "Optional 'a' then 'b'",
        "(a|b)*(aa|bb)":"Ends with aa or bb",
    }
    for pat, desc in examples.items():
        if st.button(pat, key=pat, help=desc, use_container_width=True):
            st.session_state['regex_input'] = pat
    st.markdown("### 🎨 Legend")
    st.markdown("""
- 🔵 **Blue** — Start state
- 🟢 **Green** — Accept state
- ⚫ **Gray** — Regular state
- **Red arrow** — Symbol transition
- **Dashed** — ε transition
    """)

# ─────────────────────────────────────────────
# Input row
# ─────────────────────────────────────────────
c1, c2, c3 = st.columns([4, 1, 1])
with c1:
    regex_input = st.text_input(
        "⚡ Regular Expression:",
        value=st.session_state.get('regex_input', '(a|b)*abb'),
        placeholder="e.g. (a|b)*abb",
    )
with c2:
    st.write(""); st.write("")
    convert_btn = st.button("⚙️ Convert", type="primary", use_container_width=True)
with c3:
    st.write(""); st.write("")
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state['regex_input'] = ''
        st.rerun()


# ─────────────────────────────────────────────
# Small step diagram helper
# ─────────────────────────────────────────────
def small_diagram(title, nfa_dict):
    import graphviz as gv
    dot = gv.Digraph(
        graph_attr={
            'rankdir':  'LR',
            'label':    title,
            'labelloc': 't',
            'fontsize': '12',
            'fontname': 'Helvetica',
            'bgcolor':  'transparent',
            'nodesep':  '0.4',
            'ranksep':  '0.5',
        },
        node_attr={'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '10'},
    )
    start  = nfa_dict['start']
    accept = nfa_dict['accept']
    states = nfa_dict['states']
    trans  = nfa_dict['transitions']

    dot.node('__s__', shape='none', label='', width='0', height='0')
    dot.edge('__s__', start, arrowhead='normal', color='#555555')

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

    # Group edges
    em = {}
    for src, tr in trans.items():
        for sym, tgts in tr.items():
            for dst in tgts:
                em.setdefault((src, dst), []).append(sym)

    for (src, dst), syms in em.items():
        real = [s for s in syms if s != EPSILON]
        eps  = [s for s in syms if s == EPSILON]
        if real:
            dot.edge(src, dst, label=', '.join(sorted(real)),
                     color='#c0392b', fontcolor='#c0392b', penwidth='2')
        if eps:
            dot.edge(src, dst, label='ε',
                     style='dashed', color='#7f8c8d', fontcolor='#7f8c8d')

    st.graphviz_chart(dot.source, use_container_width=True)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if regex_input and (convert_btn or st.session_state.get('last_regex') == regex_input):
    st.session_state['last_regex'] = regex_input
    try:
        nfa = regex_to_nfa(regex_input)
        dfa = nfa_to_dfa(nfa)

        # Stat cards
        st.markdown(f"""
<div class="stat-row">
  <div class="stat-card"><div class="stat-val">{len(nfa['states'])}</div><div class="stat-lbl">NFA states</div></div>
  <div class="stat-card"><div class="stat-val">{len(dfa['all_states'])}</div><div class="stat-lbl">DFA states (minimized)</div></div>
  <div class="stat-card"><div class="stat-val">{len(dfa['accept_states'])}</div><div class="stat-lbl">Accept states</div></div>
  <div class="stat-card"><div class="stat-val">{{{', '.join(dfa['alphabet'])}}}</div><div class="stat-lbl">Alphabet</div></div>
</div>
""", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔵 ε-NFA Diagram",
            "🟢 DFA Diagram",
            "📊 Transition Tables",
            "▶️ Simulate",
            "📖 Construction Steps",
        ])

        # ── Tab 1: NFA ──
        with tab1:
            st.markdown('<div class="section-header">ε-NFA — Thompson\'s Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Built by composing small 2-state NFAs using union, concatenation and Kleene-star rules. ε-transitions (dashed) are used only where mathematically required.</div>', unsafe_allow_html=True)
            st.graphviz_chart(visualize_nfa(nfa, f"ε-NFA  ·  {regex_input}").source, use_container_width=True)
            with st.expander("Details"):
                st.write(f"Start: `{nfa['start']}`  |  Accept: `{nfa['accept']}`  |  States: {sorted(nfa['states'])}")

        # ── Tab 2: DFA ──
        with tab2:
            st.markdown('<div class="section-header">Minimized DFA — Subset + Myhill-Nerode</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">States are labeled q0, q1 … after minimization. Equivalent states are merged, giving the smallest possible DFA for this language.</div>', unsafe_allow_html=True)
            st.graphviz_chart(visualize_dfa(dfa, f"Minimized DFA  ·  {regex_input}").source, use_container_width=True)
            with st.expander("Details"):
                st.write(f"Start: `{dfa['state_labels'][dfa['start_state']]}`  |  "
                         f"Accept: `{[dfa['state_labels'][s] for s in dfa['accept_states']]}`")

        # ── Tab 3: Tables ──
        with tab3:
            st.markdown('<div class="section-header">Transition Tables</div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca:
                st.subheader("ε-NFA table")
                rows = get_nfa_table(nfa)
                if rows:
                    st.dataframe(pd.DataFrame(rows).set_index('State'), use_container_width=True)
            with cb:
                st.subheader("DFA table (minimized)")
                rows = get_dfa_table(dfa)
                if rows:
                    st.dataframe(pd.DataFrame(rows).set_index('State'), use_container_width=True)

        # ── Tab 4: Simulate ──
        with tab4:
            st.markdown('<div class="section-header">▶️ Simulate a String</div>', unsafe_allow_html=True)
            s1, s2 = st.columns([3, 1])
            with s1:
                test_str = st.text_input("String to test:", placeholder="e.g. aabb")
            with s2:
                mode = st.radio("Run on:", ["DFA", "ε-NFA"], horizontal=True)
            if st.button("▶️ Run", type="primary"):
                acc, path = simulate_dfa(dfa, test_str) if mode == "DFA" else simulate_nfa(nfa, test_str)
                if acc:
                    st.markdown(f'<div class="result-accepted">✅ ACCEPTED — "{test_str}" matches <code>{regex_input}</code></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="result-rejected">❌ REJECTED — "{test_str}" does not match <code>{regex_input}</code></div>', unsafe_allow_html=True)
                st.subheader("Trace")
                syms = ["(start)"] + list(test_str) if test_str else ["(start — ε)"]
                for i, (sym, st_name) in enumerate(zip(syms, path)):
                    prefix = "Initial state" if i == 0 else f"Read '{sym}'"
                    st.write(f"**Step {i}:** {prefix} → `{st_name}`")
                st.info(f"Final: `{path[-1]}` → {'✅ Accept' if acc else '❌ Reject'}")

            st.divider()
            st.subheader("Batch test")
            batch = st.text_area("One string per line:", placeholder="aabb\nabb\nbba", height=110)
            if st.button("Run batch"):
                if batch.strip():
                    rows = []
                    for s in batch.strip().splitlines():
                        s = s.strip()
                        if s:
                            a, _ = simulate_dfa(dfa, s)
                            rows.append({'String': f'"{s}"', 'Result': '✅ Accepted' if a else '❌ Rejected'})
                    if rows:
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ── Tab 5: Construction steps with diagrams ──
        with tab5:
            st.markdown('<div class="section-header">📖 Step-by-Step Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Every step below shows the construction rule AND a live diagram built from the actual characters in your regex.</div>', unsafe_allow_html=True)
            st.markdown(f"**Regex:** `{regex_input}`")
            st.divider()

            symbols = sorted(set(c for c in regex_input if c not in '()|*+?'))

            # ── Step 1: Base symbols ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-title">📌 Step 1 — Base symbol NFAs</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-desc">Every character becomes a tiny 2-state NFA with one transition.</div>', unsafe_allow_html=True)
            st.code("→ (s) --symbol--> ((a))", language=None)
            if symbols:
                cols = st.columns(min(len(symbols), 4))
                for i, sym in enumerate(symbols):
                    with cols[i % 4]:
                        reset_states()
                        small_diagram(f"'{sym}'", nfa_for_symbol(sym))
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # ── Step 2: Concatenation ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-title">📌 Step 2 — Concatenation ( AB )</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-desc">NFA_A\'s accept state is linked to NFA_B\'s start via ε. The two NFAs become one sequential NFA.</div>', unsafe_allow_html=True)
            st.code("accept(A)  →ε→  start(B)", language=None)
            if len(symbols) >= 2:
                reset_states()
                c_a = nfa_for_symbol(symbols[0])
                c_b = nfa_for_symbol(symbols[1])
                small_diagram(f"'{symbols[0]}' then '{symbols[1]}'", nfa_concatenation(c_a, c_b))
            elif len(symbols) == 1:
                reset_states()
                c_a = nfa_for_symbol(symbols[0])
                c_b = nfa_for_symbol(symbols[0])
                small_diagram(f"'{symbols[0]}' then '{symbols[0]}'", nfa_concatenation(c_a, c_b))
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # ── Step 3: Union ──
            if '|' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-title">📌 Step 3 — Union ( A | B )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">A new start branches via ε into both NFA_A and NFA_B. Both their accept states merge via ε into one new accept state.</div>', unsafe_allow_html=True)
                st.code(
                    "new_start →ε→ start(A),  accept(A) →ε→ new_accept\n"
                    "new_start →ε→ start(B),  accept(B) →ε→ new_accept",
                    language=None
                )
                sym_a = symbols[0]
                sym_b = symbols[1] if len(symbols) > 1 else symbols[0]
                reset_states()
                small_diagram(
                    f"'{sym_a}' | '{sym_b}'",
                    nfa_union(nfa_for_symbol(sym_a), nfa_for_symbol(sym_b))
                )
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Step 4: Kleene Star ──
            if '*' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-title">📌 Step 4 — Kleene Star ( A* )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">New start → ε → NFA_A, with a loop back from NFA_A\'s accept to its start, and a skip path from new start directly to new accept.</div>', unsafe_allow_html=True)
                st.code(
                    "new_start →ε→ start(A) →ε→ new_accept   (enter)\n"
                    "new_start →ε→ new_accept                 (zero times)\n"
                    "accept(A) →ε→ start(A)                   (loop back)",
                    language=None
                )
                reset_states()
                small_diagram(f"'{symbols[0]}*'", nfa_kleene_star(nfa_for_symbol(symbols[0])))
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Step 5: Plus ──
            if '+' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-title">📌 Step 5 — Plus ( A+ )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">A+ = A followed by A*. Must pass through NFA_A at least once before entering the loop.</div>', unsafe_allow_html=True)
                st.code("accept(A) →ε→ start(A*)   (must go through once, then loop)", language=None)
                reset_states()
                small_diagram(f"'{symbols[0]}+'", nfa_plus(nfa_for_symbol(symbols[0])))
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Step 6: Optional ──
            if '?' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-title">📌 Step 6 — Optional ( A? )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">New start can either enter NFA_A or skip directly to accept — giving zero or one occurrence.</div>', unsafe_allow_html=True)
                st.code(
                    "new_start →ε→ start(A) →ε→ new_accept   (one time)\n"
                    "new_start →ε→ new_accept                 (zero times)",
                    language=None
                )
                reset_states()
                small_diagram(f"'{symbols[0]}?'", nfa_optional(nfa_for_symbol(symbols[0])))
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Final: Complete NFA ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-title">📌 Final — Complete ε-NFA</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-desc">All the above pieces combined into one ε-NFA for your entire regex:</div>', unsafe_allow_html=True)
            st.markdown(f"""
| | |
|---|---|
| States | **{len(nfa['states'])}** |
| Start | **`{nfa['start']}`** |
| Accept | **`{nfa['accept']}`** |
""")
            small_diagram(f"Complete ε-NFA: {regex_input}", nfa)
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # ── DFA Summary ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-title">📌 DFA — Subset Construction + Minimization</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-desc">ε-NFA is converted to DFA via subset construction, then minimized using Myhill-Nerode. States are relabeled q0, q1, q2 …</div>', unsafe_allow_html=True)
            st.markdown(f"""
| | |
|---|---|
| NFA states | **{len(nfa['states'])}** |
| DFA states (minimized) | **{len(dfa['all_states'])}** |
| Accept states | **{', '.join(dfa['state_labels'][s] for s in dfa['accept_states'])}** |
""")
            st.graphviz_chart(visualize_dfa(dfa, f"Minimized DFA: {regex_input}").source, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except ValueError as e:
        st.error(f"❌ Invalid regex: {e}")
        st.info("Use only letters, |, *, +, ?, and balanced parentheses.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.info("Try a different pattern.")

else:
    st.markdown("""
<div style="text-align:center;padding:3em 0;opacity:0.45;">
  <div style="font-size:2em;">⚡</div>
  <div style="font-size:1.3em;font-weight:600;margin:0.4em 0;">Enter a regex above and click Convert</div>
  <div style="font-size:0.9em;">or pick an example from the sidebar</div>
</div>
""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.info("**Step 1** — Enter regex like `(a|b)*abb`")
    with c2: st.info("**Step 2** — View ε-NFA and DFA diagrams")
    with c3: st.info("**Step 3** — Simulate strings for acceptance")
