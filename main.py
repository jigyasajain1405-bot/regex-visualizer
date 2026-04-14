"""
main.py
-------
Streamlit web application: Regular Expression to ε-NFA and DFA Visualizer
Run with:  streamlit run main.py
"""

import streamlit as st
import pandas as pd
import graphviz

from regex_to_nfa import (
    regex_to_nfa, new_state, reset_states,
    nfa_for_symbol, nfa_concatenation, nfa_union,
    nfa_kleene_star, nfa_plus, nfa_optional,
    EPSILON
)
from nfa_to_dfa import nfa_to_dfa, simulate_dfa, simulate_nfa
from visualize import visualize_nfa, visualize_dfa, get_nfa_table, get_dfa_table

st.set_page_config(
    page_title="RE → ε-NFA & DFA Visualizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme toggle ──
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False

# ── Dynamic CSS based on theme ──
def get_css(dark):
    if dark:
        bg        = "#0f0f1a"
        card_bg   = "#1a1a2e"
        text      = "#e2e8f0"
        text_muted= "#94a3b8"
        border    = "rgba(168,85,247,0.3)"
        step_bg   = "rgba(168,85,247,0.08)"
        code_bg   = "rgba(168,85,247,0.15)"
        info_bg   = "rgba(168,85,247,0.1)"
        toggle_bg = "#1e1b4b"
    else:
        bg        = "#fafafa"
        card_bg   = "#ffffff"
        text      = "#1e293b"
        text_muted= "#64748b"
        border    = "rgba(168,85,247,0.25)"
        step_bg   = "rgba(168,85,247,0.05)"
        code_bg   = "rgba(168,85,247,0.08)"
        info_bg   = "rgba(168,85,247,0.07)"
        toggle_bg = "#ede9fe"

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Poppins:wght@400;600;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif !important;
    }}

    /* Page background */
    .stApp {{
        background-color: {bg} !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {card_bg} !important;
        border-right: 1px solid {border} !important;
    }}

    /* Title */
    .main-title {{
        font-size: 2.5em;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #a855f7, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.1em;
        padding-top: 0.3em;
    }}
    .subtitle {{
        text-align: center;
        color: {text_muted};
        font-size: 0.95em;
        margin-bottom: 1.5em;
        letter-spacing: 0.04em;
    }}

    /* Theme toggle bar */
    .theme-bar {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding: 6px 0 10px 0;
        gap: 8px;
        font-size: 13px;
        color: {text_muted};
    }}

    /* Result boxes */
    .result-accepted {{
        background: rgba(16,185,129,0.12);
        border-left: 5px solid #10b981;
        padding: 1em 1.2em;
        border-radius: 10px;
        font-size: 1.15em;
        font-weight: 600;
        color: #10b981;
        margin: 0.5em 0;
    }}
    .result-rejected {{
        background: rgba(239,68,68,0.12);
        border-left: 5px solid #ef4444;
        padding: 1em 1.2em;
        border-radius: 10px;
        font-size: 1.15em;
        font-weight: 600;
        color: #ef4444;
        margin: 0.5em 0;
    }}

    /* Info box */
    .info-box {{
        background: {info_bg};
        border-left: 4px solid #a855f7;
        padding: 0.9em 1.1em;
        border-radius: 0 10px 10px 0;
        margin: 0.6em 0;
        color: {text};
        font-size: 0.95em;
    }}

    /* Section header */
    .section-header {{
        font-size: 1.25em;
        font-weight: 700;
        color: {text};
        border-bottom: 2px solid #a855f7;
        padding-bottom: 0.3em;
        margin-top: 1em;
        margin-bottom: 0.8em;
    }}

    /* Step box */
    .step-box {{
        background: {step_bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 1em 1.3em;
        margin: 0.8em 0;
        color: {text};
    }}
    .step-number {{
        font-size: 1.05em;
        font-weight: 700;
        color: #a855f7;
        margin-bottom: 0.4em;
    }}
    .step-desc {{
        color: {text_muted};
        font-size: 0.9em;
        margin-bottom: 0.6em;
    }}

    /* Code */
    code {{
        font-family: 'Fira Code', monospace !important;
        background: {code_bg} !important;
        color: #a855f7 !important;
        border-radius: 4px;
        padding: 0.1em 0.4em;
    }}

    /* Primary button */
    div[data-testid="stButton"] button[kind="primary"] {{
        background: linear-gradient(135deg, #a855f7, #06b6d4) !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}

    /* Tabs */
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: #a855f7 !important;
        border-bottom-color: #a855f7 !important;
    }}
</style>
"""

dark = st.session_state['dark_mode']
st.markdown(get_css(dark), unsafe_allow_html=True)

# ── Theme toggle button at top right ──
tcol1, tcol2 = st.columns([6, 1])
with tcol2:
    mode_label = "☀️ Light" if dark else "🌙 Dark"
    if st.button(mode_label, key="theme_toggle", use_container_width=True):
        st.session_state['dark_mode'] = not dark
        st.rerun()

# ── Header ──
st.markdown('<div class="main-title">⚡ Regex → ε-NFA & DFA Visualizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Thompson\'s Construction &nbsp;·&nbsp; Subset Construction &nbsp;·&nbsp; Interactive Simulation</div>', unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 📖 How to Use")
    st.markdown("""
1. **Enter a Regex** in the input box
2. Click **Convert** to generate automata
3. View the **ε-NFA** and **DFA** diagrams
4. Check **Construction Steps** for step diagrams
5. **Simulate** a string to test acceptance
    """)
    st.markdown("### ✅ Supported Operators")
    st.markdown("""
| Op | Meaning | Example |
|---|---|---|
| `\\|` | Union | `a\\|b` |
| `*` | Kleene Star | `a*` |
| `+` | One or more | `a+` |
| `?` | Optional | `a?` |
| `()` | Grouping | `(ab)*` |
    """)
    st.markdown("### 📌 Try These Examples")
    examples = {
        "a|b": "Matches 'a' or 'b'",
        "a*": "Zero or more 'a's",
        "a+": "One or more 'a's",
        "(a|b)*": "Any string of a's and b's",
        "ab*c": "a, then b's, then c",
        "(a|b)*abb": "Ends with 'abb'",
        "a?b": "Optional 'a' then 'b'",
        "(a|b)*(aa|bb)": "Ends with aa or bb"
    }
    for pattern, desc in examples.items():
        if st.button(pattern, key=pattern, help=desc, use_container_width=True):
            st.session_state['regex_input'] = pattern
    st.markdown("### 🎨 Diagram Legend")
    st.markdown("""
- 🔵 **Blue** — Start state
- 🟢 **Green** — Accept state
- ⚪ **Gray** — Regular state
- **Red arrow** — Symbol transition
- **Dashed arrow** — ε transition
    """)

# ── Input ──
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    regex_input = st.text_input(
        "⚡ Enter Regular Expression:",
        value=st.session_state.get('regex_input', '(a|b)*abb'),
        placeholder="e.g. (a|b)*abb",
    )
with col2:
    st.write("")
    st.write("")
    convert_btn = st.button("⚙️ Convert", type="primary", use_container_width=True)
with col3:
    st.write("")
    st.write("")
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    st.session_state['regex_input'] = ''
    st.rerun()


# ── Helper: build small demo NFA diagrams for each step ──
def make_step_diagram(title, states, transitions, start, accept):
    """Build a small Graphviz diagram for a construction step."""
    dot = graphviz.Digraph(
        graph_attr={
            'rankdir': 'LR',
            'label': title,
            'labelloc': 't',
            'fontsize': '13',
            'fontname': 'Helvetica',
            'bgcolor': 'transparent',
            'size': '6,2',
            'ratio': 'compress'
        },
        node_attr={'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '10'}
    )
    dot.node('__s__', shape='none', label='', width='0', height='0')
    dot.edge('__s__', start, label='', style='bold', color='#2ecc71')
    for state in states:
        if state == accept:
            dot.node(state, state, shape='doublecircle', style='filled',
                     fillcolor='#2ecc71', color='#27ae60', fontcolor='white')
        elif state == start:
            dot.node(state, state, shape='circle', style='filled',
                     fillcolor='#3498db', color='#2980b9', fontcolor='white')
        else:
            dot.node(state, state, shape='circle', style='filled',
                     fillcolor='#ecf0f1', color='#bdc3c7', fontcolor='#2c3e50')
    for s, trans in transitions.items():
        for sym, targets in trans.items():
            for t in targets:
                if sym == EPSILON:
                    dot.edge(s, t, label='ε', style='dashed',
                             color='#95a5a6', fontcolor='#7f8c8d')
                else:
                    dot.edge(s, t, label=sym,
                             color='#e74c3c', fontcolor='#c0392b', penwidth='2')
    return dot


def show_step_diagram(title, nfa_dict):
    """Render a step diagram from an NFA dict."""
    d = make_step_diagram(
        title,
        sorted(nfa_dict['states']),
        nfa_dict['transitions'],
        nfa_dict['start'],
        nfa_dict['accept']
    )
    st.graphviz_chart(d.source, use_container_width=True)


# ── Main Logic ──
if regex_input and (convert_btn or st.session_state.get('last_regex') == regex_input):
    st.session_state['last_regex'] = regex_input
    try:
        nfa = regex_to_nfa(regex_input)
        dfa = nfa_to_dfa(nfa)

        st.success(f"✅ Converted **`{regex_input}`** | "
                   f"ε-NFA: **{len(nfa['states'])} states** | "
                   f"DFA: **{len(dfa['all_states'])} states** | "
                   f"Alphabet: **{{{', '.join(dfa['alphabet'])}}}**")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔵 ε-NFA Diagram",
            "🔴 DFA Diagram",
            "📊 Transition Tables",
            "▶️ Simulate String",
            "📖 Construction Steps"
        ])

        # ── Tab 1 ──
        with tab1:
            st.markdown('<div class="section-header">ε-NFA via Thompson\'s Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Thompson\'s Construction builds the ε-NFA recursively. Each operator adds new states and ε-transitions (dashed arrows).</div>', unsafe_allow_html=True)
            nfa_dot = visualize_nfa(nfa, title=f"ε-NFA for: {regex_input}")
            st.graphviz_chart(nfa_dot.source, use_container_width=True)
            with st.expander("ℹ️ ε-NFA Details"):
                st.write(f"**Start state:** `{nfa['start']}`")
                st.write(f"**Accept state:** `{nfa['accept']}`")
                st.write(f"**Total states:** {len(nfa['states'])}")

        # ── Tab 2 ──
        with tab2:
            st.markdown('<div class="section-header">DFA via Subset Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Each DFA state represents a set of NFA states reachable after reading the same input prefix.</div>', unsafe_allow_html=True)
            dfa_dot = visualize_dfa(dfa, title=f"DFA for: {regex_input}")
            st.graphviz_chart(dfa_dot.source, use_container_width=True)
            with st.expander("ℹ️ DFA Details"):
                st.write(f"**Start state:** `{dfa['state_labels'][dfa['start_state']]}`")
                st.write(f"**Accept states:** `{[dfa['state_labels'][s] for s in dfa['accept_states']]}`")
                st.write(f"**Total states:** {len(dfa['all_states'])}")

        # ── Tab 3 ──
        with tab3:
            st.markdown('<div class="section-header">Transition Tables</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("ε-NFA Table")
                nfa_rows = get_nfa_table(nfa)
                if nfa_rows:
                    st.dataframe(pd.DataFrame(nfa_rows).set_index('State'), use_container_width=True)
            with col_b:
                st.subheader("DFA Table")
                dfa_rows = get_dfa_table(dfa)
                if dfa_rows:
                    st.dataframe(pd.DataFrame(dfa_rows).set_index('DFA State'), use_container_width=True)

        # ── Tab 4 ──
        with tab4:
            st.markdown('<div class="section-header">▶️ Simulate an Input String</div>', unsafe_allow_html=True)
            sim_col1, sim_col2 = st.columns([3, 1])
            with sim_col1:
                test_string = st.text_input("Enter a string to test:", placeholder="e.g. aabb")
            with sim_col2:
                automaton_choice = st.radio("Simulate on:", ["DFA", "ε-NFA"], horizontal=True)
            if test_string is not None:
                if st.button("▶️ Simulate", type="primary"):
                    if automaton_choice == "DFA":
                        accepted, path = simulate_dfa(dfa, test_string)
                    else:
                        accepted, path = simulate_nfa(nfa, test_string)
                    if accepted:
                        st.markdown(f'<div class="result-accepted">✅ ACCEPTED — "{test_string}" matched by <code>{regex_input}</code></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="result-rejected">❌ REJECTED — "{test_string}" not matched by <code>{regex_input}</code></div>', unsafe_allow_html=True)
                    st.subheader("🔍 Step-by-Step Trace")
                    symbols_list = ["(start)"] + list(test_string) if test_string else ["(start — empty string)"]
                    for i, (symbol, state) in enumerate(zip(symbols_list, path)):
                        if i == 0:
                            st.write(f"**Step {i}:** Initial state → `{state}`")
                        else:
                            st.write(f"**Step {i}:** Read `'{symbol}'` → `{state}`")
                    final_icon = "✅ Accept" if accepted else "❌ Reject"
                    st.info(f"**Final state:** `{path[-1]}` → **{final_icon}**")
            st.divider()
            st.subheader("📋 Batch Test Strings")
            batch_input = st.text_area("Enter multiple strings (one per line):", placeholder="aabb\nabb\nbba\n", height=120)
            if st.button("Run All Tests"):
                if batch_input.strip():
                    results = []
                    for s in batch_input.strip().split('\n'):
                        s = s.strip()
                        if s:
                            acc, _ = simulate_dfa(dfa, s)
                            results.append({'String': f'"{s}"', 'Result': '✅ Accepted' if acc else '❌ Rejected'})
                    if results:
                        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

        # ── Tab 5: Construction Steps with diagrams ──
        with tab5:
            st.markdown('<div class="section-header">📖 Step-by-Step Thompson\'s Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Each step below shows the construction rule AND a live diagram of how that NFA piece looks for your regex characters.</div>', unsafe_allow_html=True)
            st.markdown(f"### Your Regex: `{regex_input}`")
            st.divider()

            # ── Step 1: Base symbol NFAs ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-number">📌 Step 1: Base Symbol NFAs</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-desc">For every character in your regex, Thompson\'s Construction creates a simple 2-state NFA:</div>', unsafe_allow_html=True)
            st.code("→ (start) --symbol--> ((accept))", language=None)

            symbols = sorted(set(c for c in regex_input if c not in '()|*+?'))
            if symbols:
                cols = st.columns(min(len(symbols), 3))
                for i, sym in enumerate(symbols):
                    with cols[i % 3]:
                        reset_states()
                        sym_nfa = nfa_for_symbol(sym)
                        show_step_diagram(f"NFA for symbol '{sym}'", sym_nfa)
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # ── Step 2: Concatenation ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-number">📌 Step 2: Concatenation ( AB )</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-desc">Concatenation connects NFA_A\'s accept state to NFA_B\'s start via an ε transition:</div>', unsafe_allow_html=True)
            st.code("accept(NFA_A)  →ε→  start(NFA_B)", language=None)

            if len(symbols) >= 2:
                reset_states()
                nfa_a = nfa_for_symbol(symbols[0])
                nfa_b = nfa_for_symbol(symbols[1] if len(symbols) > 1 else symbols[0])
                concat_nfa = nfa_concatenation(nfa_a, nfa_b)
                show_step_diagram(
                    f"Concatenation: '{symbols[0]}' followed by '{symbols[1] if len(symbols)>1 else symbols[0]}'",
                    concat_nfa
                )
            else:
                st.info("Only one unique symbol in your regex — concatenation uses repeated symbols.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # ── Step 3: Union (if used) ──
            if '|' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-number">📌 Step 3: Union ( A | B )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">Union creates a new start state with ε-transitions to both NFA_A and NFA_B, and merges their accept states into one new accept:</div>', unsafe_allow_html=True)
                st.code(
                    "new_start →ε→ start(NFA_A),  accept(NFA_A) →ε→ new_accept\n"
                    "new_start →ε→ start(NFA_B),  accept(NFA_B) →ε→ new_accept",
                    language=None
                )
                reset_states()
                u_a = nfa_for_symbol(symbols[0])
                u_b = nfa_for_symbol(symbols[1] if len(symbols) > 1 else symbols[0])
                union_nfa = nfa_union(u_a, u_b)
                show_step_diagram(
                    f"Union: '{symbols[0]}' | '{symbols[1] if len(symbols)>1 else symbols[0]}'",
                    union_nfa
                )
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Step 4: Kleene Star (if used) ──
            if '*' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-number">📌 Step 4: Kleene Star ( A* )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">Kleene Star wraps NFA_A with a loop. A new start connects to both NFA_A (to enter) and the new accept (to skip). NFA_A\'s accept loops back to its start:</div>', unsafe_allow_html=True)
                st.code(
                    "new_start →ε→ start(NFA_A) →ε→ new_accept\n"
                    "new_start →ε→ new_accept          [zero times]\n"
                    "accept(NFA_A) →ε→ start(NFA_A)    [loop back]",
                    language=None
                )
                reset_states()
                star_inner = nfa_for_symbol(symbols[0])
                star_nfa = nfa_kleene_star(star_inner)
                show_step_diagram(f"Kleene Star: '{symbols[0]}*'", star_nfa)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Step 5: Plus (if used) ──
            if '+' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-number">📌 Step 5: Plus ( A+ )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">Plus means one or more. It is built as NFA_A followed by NFA_A* — must go through at least once:</div>', unsafe_allow_html=True)
                st.code("accept(NFA_A) →ε→ start(NFA_A*)   [go through once, then loop]", language=None)
                reset_states()
                plus_inner = nfa_for_symbol(symbols[0])
                plus_nfa = nfa_plus(plus_inner)
                show_step_diagram(f"Plus: '{symbols[0]}+'", plus_nfa)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Step 6: Optional (if used) ──
            if '?' in regex_input:
                st.markdown('<div class="step-box">', unsafe_allow_html=True)
                st.markdown('<div class="step-number">📌 Step 6: Optional ( A? )</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-desc">Optional means zero or one occurrence. New start can either go through NFA_A or skip directly to accept:</div>', unsafe_allow_html=True)
                st.code(
                    "new_start →ε→ start(NFA_A) →ε→ new_accept\n"
                    "new_start →ε→ new_accept             [skip A]",
                    language=None
                )
                reset_states()
                opt_inner = nfa_for_symbol(symbols[0])
                opt_nfa = nfa_optional(opt_inner)
                show_step_diagram(f"Optional: '{symbols[0]}?'", opt_nfa)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

            # ── Final Step: Complete NFA ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-number">📌 Final Step: Complete ε-NFA for Your Regex</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-desc">All the above steps are combined together to produce the final ε-NFA for your entire regex:</div>', unsafe_allow_html=True)
            st.markdown(f"""
| Property | Value |
|---|---|
| Total states | **{len(nfa['states'])}** |
| Start state | **`{nfa['start']}`** |
| Accept state | **`{nfa['accept']}`** |
| Alphabet | **{{{', '.join(dfa['alphabet'])}}}** |
            """)
            show_step_diagram(f"Complete ε-NFA for: {regex_input}", nfa)
            st.success("👉 See the full interactive diagram in the **ε-NFA Diagram** tab!")
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # ── DFA Conversion Summary ──
            st.markdown('<div class="step-box">', unsafe_allow_html=True)
            st.markdown('<div class="step-number">📌 DFA Conversion: Subset Construction</div>', unsafe_allow_html=True)
            st.markdown(f"""
**1.** ε-closure of start state `{nfa['start']}` → **DFA state D0**

**2.** For each symbol in `{{{', '.join(dfa['alphabet'])}}}`:
   - move(states, symbol) + ε-closure = new DFA state

**3.** DFA state containing `{nfa['accept']}` → **accept state**

**4.** Repeat until no new states found
            """)
            st.markdown(f"""
| | Value |
|---|---|
| NFA states | **{len(nfa['states'])}** |
| DFA states | **{len(dfa['all_states'])}** |
| Accept states | **{len(dfa['accept_states'])}** |
            """)
            dfa_dot2 = visualize_dfa(dfa, title=f"Final DFA for: {regex_input}")
            st.graphviz_chart(dfa_dot2.source, use_container_width=True)
            st.success("👉 See the full interactive DFA in the **DFA Diagram** tab!")
            st.markdown('</div>', unsafe_allow_html=True)

    except ValueError as e:
        st.error(f"❌ **Invalid regex:** {e}")
        st.info("💡 Make sure your regex only uses letters, |, *, +, ?, and balanced parentheses.")
    except Exception as e:
        st.error(f"❌ **Unexpected error:** {e}")
        st.info("Please try a different regex pattern.")

else:
    st.markdown("""
    <div style="text-align:center; padding: 3em; opacity: 0.5;">
        <h2>⚡ Enter a regular expression above and click Convert</h2>
        <p>Or pick one of the example patterns in the sidebar</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Step 1:** Enter a regex like `(a|b)*abb`")
    with col2:
        st.info("**Step 2:** View ε-NFA and DFA diagrams")
    with col3:
        st.info("**Step 3:** Simulate strings to test acceptance")
