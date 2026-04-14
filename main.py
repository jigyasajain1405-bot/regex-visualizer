"""
main.py
-------
Streamlit web application: Regular Expression to ε-NFA and DFA Visualizer
Run with:  streamlit run main.py
"""

import streamlit as st
import pandas as pd

from regex_to_nfa import regex_to_nfa
from nfa_to_dfa import nfa_to_dfa, simulate_dfa, simulate_nfa
from visualize import visualize_nfa, visualize_dfa, get_nfa_table, get_dfa_table

st.set_page_config(
    page_title="RE → ε-NFA & DFA Visualizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Poppins:wght@400;600;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* ── Title ── */
    .main-title {
        font-size: 2.6em;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #a855f7, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.1em;
        padding-top: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: inherit;
        opacity: 0.6;
        font-size: 1em;
        margin-bottom: 1.5em;
        letter-spacing: 0.05em;
    }

    /* ── Success/Info boxes ── */
    .result-accepted {
        background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.1));
        border-left: 5px solid #10b981;
        padding: 1em 1.2em;
        border-radius: 10px;
        font-size: 1.2em;
        font-weight: 600;
        color: #10b981;
        margin: 0.5em 0;
    }
    .result-rejected {
        background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(168,85,247,0.1));
        border-left: 5px solid #ef4444;
        padding: 1em 1.2em;
        border-radius: 10px;
        font-size: 1.2em;
        font-weight: 600;
        color: #ef4444;
        margin: 0.5em 0;
    }
    .info-box {
        background: rgba(168,85,247,0.08);
        border-left: 4px solid #a855f7;
        padding: 0.9em 1.1em;
        border-radius: 0 10px 10px 0;
        margin: 0.6em 0;
        color: inherit;
        font-size: 0.95em;
    }
    .section-header {
        font-size: 1.3em;
        font-weight: 700;
        color: inherit;
        border-bottom: 2px solid #a855f7;
        padding-bottom: 0.3em;
        margin-top: 1em;
        margin-bottom: 0.8em;
    }

    /* ── Construction step boxes ── */
    .step-box {
        background: rgba(168,85,247,0.06);
        border: 1px solid rgba(168,85,247,0.25);
        border-radius: 12px;
        padding: 1em 1.3em;
        margin: 0.8em 0;
        color: inherit;
    }
    .step-number {
        font-size: 1.05em;
        font-weight: 700;
        color: #a855f7;
        margin-bottom: 0.4em;
    }

    /* ── Code blocks ── */
    code {
        font-family: 'Fira Code', monospace !important;
        background: rgba(168,85,247,0.1) !important;
        color: #a855f7 !important;
        border-radius: 4px;
        padding: 0.1em 0.4em;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: rgba(168,85,247,0.04);
        border-right: 1px solid rgba(168,85,247,0.15);
    }

    /* ── Buttons ── */
    div[data-testid="stButton"] button {
        border-radius: 8px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #a855f7, #06b6d4) !important;
        border: none !important;
        color: white !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    /* ── Tabs ── */
    div[data-testid="stTabs"] button {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #a855f7 !important;
        border-bottom-color: #a855f7 !important;
    }
</style>
""", unsafe_allow_html=True)

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
4. Check **Construction Steps** to learn how
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
        help="Use letters, |, *, +, ?, and parentheses"
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

        # ── Tab 1: NFA ──
        with tab1:
            st.markdown('<div class="section-header">ε-NFA via Thompson\'s Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Thompson\'s Construction builds the ε-NFA recursively. Each operator adds new states and ε-transitions (dashed arrows).</div>', unsafe_allow_html=True)
            nfa_dot = visualize_nfa(nfa, title=f"ε-NFA for: {regex_input}")
            st.graphviz_chart(nfa_dot.source, use_container_width=True)
            with st.expander("ℹ️ ε-NFA Details"):
                st.write(f"**Start state:** `{nfa['start']}`")
                st.write(f"**Accept state:** `{nfa['accept']}`")
                st.write(f"**Total states:** {len(nfa['states'])}")
                st.write(f"**All states:** {sorted(nfa['states'])}")

        # ── Tab 2: DFA ──
        with tab2:
            st.markdown('<div class="section-header">DFA via Subset Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Each DFA state (labeled D0, D1...) represents a set of NFA states reachable after reading the same input.</div>', unsafe_allow_html=True)
            dfa_dot = visualize_dfa(dfa, title=f"DFA for: {regex_input}")
            st.graphviz_chart(dfa_dot.source, use_container_width=True)
            with st.expander("ℹ️ DFA Details"):
                st.write(f"**Start state:** `{dfa['state_labels'][dfa['start_state']]}`")
                st.write(f"**Accept states:** `{[dfa['state_labels'][s] for s in dfa['accept_states']]}`")
                st.write(f"**Total states:** {len(dfa['all_states'])}")
                st.write(f"**Alphabet:** `{dfa['alphabet']}`")

        # ── Tab 3: Tables ──
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

        # ── Tab 4: Simulate ──
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

        # ── Tab 5: Construction Steps ──
        with tab5:
            st.markdown('<div class="section-header">📖 Step-by-Step Thompson\'s Construction</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Thompson\'s Construction breaks the regex into smaller parts and builds the ε-NFA piece by piece. Below are the exact steps applied to your regex.</div>', unsafe_allow_html=True)

            st.markdown(f"### Your Regex: `{regex_input}`")
            st.divider()

            # Step 1
            st.markdown('<div class="step-box"><div class="step-number">📌 Step 1: Identify Base Symbols</div>', unsafe_allow_html=True)
            symbols = sorted(set(c for c in regex_input if c not in '()|*+?'))
            st.markdown(f"Characters found: **{', '.join(f'`{s}`' for s in symbols)}**")
            st.markdown("For each character, a simple 2-state NFA is created:")
            st.code("→ (start_state) --symbol--> ((accept_state))", language=None)
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # Step 2
            st.markdown('<div class="step-box"><div class="step-number">📌 Step 2: Operators Found in Your Regex</div>', unsafe_allow_html=True)
            ops_used = []
            if '|' in regex_input: ops_used.append('**Union** `|` — matches either left or right side')
            if '*' in regex_input: ops_used.append('**Kleene Star** `*` — zero or more repetitions')
            if '+' in regex_input: ops_used.append('**Plus** `+` — one or more repetitions')
            if '?' in regex_input: ops_used.append('**Optional** `?` — zero or one occurrence')
            ops_used.append('**Concatenation** — placing symbols/groups next to each other')
            for op in ops_used:
                st.markdown(f"- {op}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # Step 3
            st.markdown('<div class="step-box"><div class="step-number">📌 Step 3: Construction Rules for Each Operator</div>', unsafe_allow_html=True)
            st.markdown("**Concatenation ( AB ):**")
            st.code("accept(NFA_A)  →ε→  start(NFA_B)", language=None)
            if '|' in regex_input:
                st.markdown("**Union ( A | B ):**")
                st.code("new_start →ε→ start(NFA_A),  accept(NFA_A) →ε→ new_accept\nnew_start →ε→ start(NFA_B),  accept(NFA_B) →ε→ new_accept", language=None)
            if '*' in regex_input:
                st.markdown("**Kleene Star ( A* ):**")
                st.code("new_start →ε→ start(NFA_A) →ε→ new_accept\nnew_start →ε→ new_accept                   [zero times]\naccept(NFA_A) →ε→ start(NFA_A)             [loop back]", language=None)
            if '+' in regex_input:
                st.markdown("**Plus ( A+ ) = A followed by A*:**")
                st.code("accept(NFA_A) →ε→ start(NFA_A*)   [must go through once, then loop]", language=None)
            if '?' in regex_input:
                st.markdown("**Optional ( A? ):**")
                st.code("new_start →ε→ start(NFA_A) →ε→ new_accept\nnew_start →ε→ new_accept               [skip A entirely]", language=None)
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # Step 4
            st.markdown('<div class="step-box"><div class="step-number">📌 Step 4: Final ε-NFA Result</div>', unsafe_allow_html=True)
            st.markdown(f"""
| Property | Value |
|---|---|
| Total states | **{len(nfa['states'])}** |
| Start state | **`{nfa['start']}`** |
| Accept state | **`{nfa['accept']}`** |
| Alphabet | **{{{', '.join(dfa['alphabet'])}}}** |
            """)
            st.success("👉 See the full diagram in the **ε-NFA Diagram** tab!")
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

            # Step 5
            st.markdown('<div class="step-box"><div class="step-number">📌 Step 5: Subset Construction (ε-NFA → DFA)</div>', unsafe_allow_html=True)
            st.markdown(f"""
**1.** Compute **ε-closure** of NFA start state `{nfa['start']}` → becomes **DFA state D0**

**2.** For each symbol in `{{{', '.join(dfa['alphabet'])}}}`:
   - Compute **move(current_states, symbol)**
   - Then compute **ε-closure** of the result
   - This set of NFA states = new DFA state

**3.** Any DFA state containing NFA accept state `{nfa['accept']}` → **DFA accept state**

**4.** Repeat until no new DFA states are found
            """)
            st.markdown(f"""
| Property | Value |
|---|---|
| NFA states | **{len(nfa['states'])}** |
| DFA states after conversion | **{len(dfa['all_states'])}** |
| DFA accept states | **{len(dfa['accept_states'])}** |
            """)
            st.success("👉 See the final DFA in the **DFA Diagram** tab!")
            st.markdown('</div>', unsafe_allow_html=True)

    except ValueError as e:
        st.error(f"❌ **Invalid regex:** {e}")
        st.info("💡 Make sure your regex only uses letters, |, *, +, ?, and balanced parentheses.")
    except Exception as e:
        st.error(f"❌ **Unexpected error:** {e}")
        st.info("Please try a different regex pattern.")

else:
    st.markdown("""
    <div style="text-align:center; padding: 3em; opacity: 0.6;">
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
