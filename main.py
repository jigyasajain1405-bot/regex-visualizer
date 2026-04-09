"""
main.py
-------
Streamlit web application: Regular Expression to ε-NFA and DFA Visualizer

Run with:  streamlit run main.py

Features:
  - Input any regular expression
  - View Thompson's Construction ε-NFA diagram
  - View Subset Construction DFA diagram
  - Transition tables for both automata
  - Simulate input strings on NFA and DFA
  - Step-by-step simulation trace
"""

import streamlit as st
import pandas as pd

from regex_to_nfa import regex_to_nfa
from nfa_to_dfa import nfa_to_dfa, simulate_dfa, simulate_nfa
from visualize import visualize_nfa, visualize_dfa, get_nfa_table, get_dfa_table

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RE → ε-NFA & DFA Visualizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Custom CSS Styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.5em;
        font-weight: 800;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1em;
        margin-bottom: 2em;
    }
    .result-accepted {
        background-color: #d5f5e3;
        border-left: 5px solid #2ecc71;
        padding: 1em;
        border-radius: 6px;
        font-size: 1.3em;
        font-weight: bold;
        color: #1e8449;
    }
    .result-rejected {
        background-color: #fadbd8;
        border-left: 5px solid #e74c3c;
        padding: 1em;
        border-radius: 6px;
        font-size: 1.3em;
        font-weight: bold;
        color: #922b21;
    }
    .info-box {
        background-color: #eaf4fb;
        border-left: 5px solid #3498db;
        padding: 1em;
        border-radius: 6px;
        margin: 0.5em 0;
    }
    .section-header {
        font-size: 1.4em;
        font-weight: 700;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.3em;
        margin-top: 1em;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">🤖 Regular Expression → ε-NFA & DFA Visualizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Thompson\'s Construction · Subset Construction · Interactive Simulation</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar — Instructions & Examples
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("📖 How to Use")
    st.markdown("""
1. **Enter a Regex** in the input box
2. Click **Convert** to generate automata
3. View the **ε-NFA** and **DFA** diagrams
4. Check the **transition tables**
5. **Simulate** a string to test acceptance
    """)

    st.header("✅ Supported Operators")
    st.markdown("""
| Operator | Meaning         | Example |
|----------|-----------------|---------|
| `\\|`    | Union (OR)      | `a\\|b`   |
| `*`      | Kleene Star     | `a*`    |
| `+`      | One or more     | `a+`    |
| `?`      | Optional        | `a?`    |
| `()`     | Grouping        | `(ab)*` |
| —        | Concatenation   | `ab`    |
    """)

    st.header("📌 Example Patterns")
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
        if st.button(f"`{pattern}`", key=pattern, help=desc, use_container_width=True):
            st.session_state['regex_input'] = pattern

    st.header("🎨 Legend")
    st.markdown("""
- 🔵 **Blue circle** — Start state  
- 🟢 **Green double circle** — Accept state  
- ⚪ **Gray circle** — Regular state  
- ➡️ **Red arrow** — Symbol transition  
- ➡️ **Gray dashed** — ε (epsilon) transition  
    """)

# ─────────────────────────────────────────────
# Main Input
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    regex_input = st.text_input(
        "🔤 Enter Regular Expression:",
        value=st.session_state.get('regex_input', '(a|b)*abb'),
        placeholder="e.g. (a|b)*abb",
        help="Type your regex using letters, |, *, +, ?, and parentheses"
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

# ─────────────────────────────────────────────
# Main Logic
# ─────────────────────────────────────────────
if regex_input and (convert_btn or st.session_state.get('last_regex') == regex_input):

    st.session_state['last_regex'] = regex_input

    try:
        # 1. Build ε-NFA
        nfa = regex_to_nfa(regex_input)

        # 2. Build DFA
        dfa = nfa_to_dfa(nfa)

        # ── Summary ──
        st.success(f"✅ Successfully converted **`{regex_input}`** | "
                   f"ε-NFA: **{len(nfa['states'])} states** | "
                   f"DFA: **{len(dfa['all_states'])} states** | "
                   f"Alphabet: **{{{', '.join(dfa['alphabet'])}}}**")

        # ─────────────────────────────────────────────
        # Tabs: NFA | DFA | Tables | Simulate
        # ─────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔵 ε-NFA Diagram",
            "🔴 DFA Diagram",
            "📊 Transition Tables",
            "▶️ Simulate String"
        ])

        # ── Tab 1: ε-NFA ──
        with tab1:
            st.markdown('<div class="section-header">ε-NFA via Thompson\'s Construction</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="info-box">
            Thompson's Construction builds the ε-NFA recursively from the regex structure.
            Each operator (union, concatenation, star) adds new states and ε-transitions.
            </div>
            """, unsafe_allow_html=True)

            nfa_dot = visualize_nfa(nfa, title=f"ε-NFA for: {regex_input}")
            st.graphviz_chart(nfa_dot.source, use_container_width=True)

            with st.expander("ℹ️ ε-NFA Details"):
                st.write(f"**Start state:** `{nfa['start']}`")
                st.write(f"**Accept state:** `{nfa['accept']}`")
                st.write(f"**Total states:** {len(nfa['states'])}")
                st.write(f"**States:** {sorted(nfa['states'])}")

        # ── Tab 2: DFA ──
        with tab2:
            st.markdown('<div class="section-header">DFA via Subset Construction</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="info-box">
            Subset Construction converts the ε-NFA into a DFA. Each DFA state represents
            a set of NFA states reachable after reading the same input prefix.
            </div>
            """, unsafe_allow_html=True)

            dfa_dot = visualize_dfa(dfa, title=f"DFA for: {regex_input}")
            st.graphviz_chart(dfa_dot.source, use_container_width=True)

            with st.expander("ℹ️ DFA Details"):
                st.write(f"**Start state:** `{dfa['state_labels'][dfa['start_state']]}`")
                st.write(f"**Accept states:** `{[dfa['state_labels'][s] for s in dfa['accept_states']]}`")
                st.write(f"**Total states:** {len(dfa['all_states'])}")
                st.write(f"**Alphabet:** `{dfa['alphabet']}`")

        # ── Tab 3: Transition Tables ──
        with tab3:
            st.markdown('<div class="section-header">Transition Tables</div>', unsafe_allow_html=True)

            col_a, col_b = st.columns(2)

            with col_a:
                st.subheader("ε-NFA Transition Table")
                nfa_rows = get_nfa_table(nfa)
                if nfa_rows:
                    df_nfa = pd.DataFrame(nfa_rows).set_index('State')
                    st.dataframe(df_nfa, use_container_width=True)

            with col_b:
                st.subheader("DFA Transition Table")
                dfa_rows = get_dfa_table(dfa)
                if dfa_rows:
                    df_dfa = pd.DataFrame(dfa_rows).set_index('DFA State')
                    st.dataframe(df_dfa, use_container_width=True)

        # ── Tab 4: String Simulation ──
        with tab4:
            st.markdown('<div class="section-header">▶️ Simulate an Input String</div>', unsafe_allow_html=True)

            sim_col1, sim_col2 = st.columns([3, 1])
            with sim_col1:
                test_string = st.text_input(
                    "Enter a string to test:",
                    placeholder="e.g. aabb",
                    help="Enter a string using only characters from the regex alphabet"
                )
            with sim_col2:
                automaton_choice = st.radio("Simulate on:", ["DFA", "ε-NFA"], horizontal=True)

            if test_string is not None:
                sim_btn = st.button("▶️ Simulate", type="primary")

                if sim_btn:
                    if automaton_choice == "DFA":
                        accepted, path = simulate_dfa(dfa, test_string)
                    else:
                        accepted, path = simulate_nfa(nfa, test_string)

                    if accepted:
                        st.markdown(f'<div class="result-accepted">✅ ACCEPTED — "{test_string}" is matched by <code>{regex_input}</code></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="result-rejected">❌ REJECTED — "{test_string}" is NOT matched by <code>{regex_input}</code></div>', unsafe_allow_html=True)

                    st.subheader("🔍 Step-by-Step Trace")
                    if test_string == "":
                        symbols_list = ["(start — empty string)"]
                    else:
                        symbols_list = ["(start)"] + list(test_string)

                    for i, (symbol, state) in enumerate(zip(symbols_list, path)):
                        if i == 0:
                            st.write(f"**Step {i}:** Initial state → `{state}`")
                        else:
                            st.write(f"**Step {i}:** Read `'{symbol}'` → `{state}`")

                    final_icon = "✅ Accept" if accepted else "❌ Reject"
                    st.info(f"**Final state:** `{path[-1]}` → **{final_icon}**")

            # Batch simulation
            st.divider()
            st.subheader("📋 Batch Test Strings")
            batch_input = st.text_area(
                "Enter multiple strings (one per line):",
                placeholder="aabb\nabb\nbba\n",
                height=120
            )
            if st.button("Run All Tests"):
                if batch_input.strip():
                    results = []
                    for s in batch_input.strip().split('\n'):
                        s = s.strip()
                        if s:
                            acc, _ = simulate_dfa(dfa, s)
                            results.append({
                                'String': f'"{s}"',
                                'Result': '✅ Accepted' if acc else '❌ Rejected'
                            })
                    if results:
                        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    except ValueError as e:
        st.error(f"❌ **Invalid regex:** {e}")
        st.info("💡 Make sure your regex only uses letters, |, *, +, ?, and balanced parentheses.")

    except Exception as e:
        st.error(f"❌ **Unexpected error:** {e}")
        st.info("Please try a different regex pattern.")

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align:center; padding: 3em; color: #7f8c8d;">
        <h2>👆 Enter a regular expression above and click <b>Convert</b></h2>
        <p>Or click one of the example patterns in the sidebar</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Step 1:** Enter a regex like `(a|b)*abb`")
    with col2:
        st.info("**Step 2:** View the ε-NFA and DFA diagrams")
    with col3:
        st.info("**Step 3:** Simulate strings to test acceptance")
