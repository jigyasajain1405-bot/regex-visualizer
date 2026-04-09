# 🤖 Regular Expression → ε-NFA & DFA Visualizer

A complete interactive web application that converts regular expressions into
ε-NFA (using Thompson's Construction) and DFA (using Subset Construction),
with visual diagrams and string simulation.

---

## 📁 Project Structure

```
regex_visualizer/
├── main.py           ← Streamlit UI (run this)
├── regex_to_nfa.py   ← Regex parser + Thompson's Construction
├── nfa_to_dfa.py     ← Subset Construction + simulation
├── visualize.py      ← Graphviz diagram generation
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## ⚙️ Setup Instructions (Mac / VS Code)

### Step 1: Install Graphviz (system dependency)

Graphviz must be installed on your system (not just as a Python package).

```bash
# Using Homebrew (recommended on Mac):
brew install graphviz
```

If you don't have Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Create a virtual environment (recommended)

```bash
cd regex_visualizer
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the application

```bash
streamlit run main.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 🚀 How to Use

1. **Enter a regular expression** in the input box (e.g. `(a|b)*abb`)
2. Click **Convert** to generate both automata
3. Browse the **ε-NFA Diagram** tab — see Thompson's construction with ε transitions
4. Browse the **DFA Diagram** tab — see the deterministic automaton
5. Check **Transition Tables** for detailed state/symbol mappings
6. Use **Simulate String** to test if a string is accepted or rejected
7. Use **Batch Test** to test multiple strings at once

---

## ✅ Supported Regex Operators

| Operator | Meaning           | Example     |
|----------|-------------------|-------------|
| `\|`     | Union (OR)        | `a\|b`      |
| `*`      | Kleene Star       | `a*`        |
| `+`      | One or more       | `a+`        |
| `?`      | Optional          | `a?`        |
| `()`     | Grouping          | `(ab)*`     |
| (none)   | Concatenation     | `ab`        |

---

## 🧪 Example Patterns to Try

| Pattern         | Matches                          |
|-----------------|----------------------------------|
| `a\|b`          | Single character: 'a' or 'b'    |
| `a*`            | Empty string, 'a', 'aa', ...    |
| `(a\|b)*`       | Any string over {a, b}          |
| `ab*c`          | 'ac', 'abc', 'abbc', ...        |
| `(a\|b)*abb`    | Strings ending in 'abb'         |
| `(a\|b)*(aa\|bb)` | Strings ending in 'aa' or 'bb' |

---

## 🎨 Diagram Color Legend

- 🔵 **Blue circle** — Start state
- 🟢 **Green double circle** — Accept (final) state
- ⚪ **Gray circle** — Regular state
- **Red arrow** — Symbol transition
- **Gray dashed arrow** — ε (epsilon) transition

---

## 📚 Algorithm References

- **Thompson's Construction** — Ken Thompson (1968), "Programming Techniques: Regular Expression Search Algorithm"
- **Subset Construction** — Rabin & Scott (1959), "Finite and Infinite Automata"
- **Textbook**: Sipser, *Introduction to the Theory of Computation*; Hopcroft, Motwani & Ullman, *Introduction to Automata Theory*

---

## 🛠 Troubleshooting

**`ExecutableNotFound: failed to execute 'dot'`**
→ Graphviz system binary is missing. Run: `brew install graphviz`

**`ModuleNotFoundError: No module named 'graphviz'`**
→ Run: `pip install graphviz`

**Blank diagrams**
→ Make sure your regex is valid and uses only supported operators

---

## 👩‍💻 Technologies Used

- **Python 3.10+**
- **Streamlit** — Interactive web UI
- **Graphviz** — Automata diagram rendering
- **Pandas** — Transition table display
