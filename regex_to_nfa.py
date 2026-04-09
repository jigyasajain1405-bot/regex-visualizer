"""
regex_to_nfa.py
---------------
Converts a regular expression into an ε-NFA using Thompson's Construction Algorithm.

Supported operators:
  |  → Union (OR)
  *  → Kleene Star (zero or more)
  +  → One or more (converted internally)
  ?  → Optional (zero or one)
  () → Grouping
  Concatenation is implicit (e.g., "ab" means a followed by b)

Each NFA is represented as:
  - states: set of state names (e.g., q0, q1, ...)
  - transitions: dict { state: { symbol: [list of next states] } }
  - start_state: the starting state
  - accept_state: the accepting state
  - epsilon: 'ε' used for epsilon transitions
"""

EPSILON = 'ε'
_state_counter = [0]


def new_state():
    """Generate a unique state name like q0, q1, q2..."""
    name = f"q{_state_counter[0]}"
    _state_counter[0] += 1
    return name


def reset_states():
    """Reset the state counter (call before each new conversion)."""
    _state_counter[0] = 0


# ──────────────────────────────────────────────
# NFA Building Blocks (Thompson's Construction)
# ──────────────────────────────────────────────

def nfa_for_symbol(symbol):
    """
    Base case: NFA that accepts exactly one character.
    Creates two states with one transition: start --symbol--> accept
    """
    start = new_state()
    accept = new_state()
    transitions = {
        start: {symbol: [accept]},
        accept: {}
    }
    return {
        'states': {start, accept},
        'transitions': transitions,
        'start': start,
        'accept': accept
    }


def nfa_concatenation(nfa1, nfa2):
    """
    Concatenation: nfa1 followed by nfa2.
    Connects nfa1's accept state to nfa2's start via ε.
    """
    # Merge transitions
    transitions = {**nfa1['transitions'], **nfa2['transitions']}

    # Add ε from nfa1's accept → nfa2's start
    transitions[nfa1['accept']][EPSILON] = [nfa2['start']]

    return {
        'states': nfa1['states'] | nfa2['states'],
        'transitions': transitions,
        'start': nfa1['start'],
        'accept': nfa2['accept']
    }


def nfa_union(nfa1, nfa2):
    """
    Union (|): accepts strings matched by nfa1 OR nfa2.
    New start → (ε→ nfa1.start, ε→ nfa2.start)
    Both nfa1.accept and nfa2.accept → ε → new accept
    """
    start = new_state()
    accept = new_state()

    transitions = {**nfa1['transitions'], **nfa2['transitions']}
    transitions[start] = {EPSILON: [nfa1['start'], nfa2['start']]}
    transitions[nfa1['accept']] = {EPSILON: [accept]}
    transitions[nfa2['accept']] = {EPSILON: [accept]}
    transitions[accept] = {}

    return {
        'states': nfa1['states'] | nfa2['states'] | {start, accept},
        'transitions': transitions,
        'start': start,
        'accept': accept
    }


def nfa_kleene_star(nfa):
    """
    Kleene Star (*): accepts zero or more repetitions.
    New start → ε→ nfa.start → (loop back + forward to new accept)
    """
    start = new_state()
    accept = new_state()

    transitions = {**nfa['transitions']}
    transitions[start] = {EPSILON: [nfa['start'], accept]}
    transitions[nfa['accept']] = {EPSILON: [nfa['start'], accept]}
    transitions[accept] = {}

    return {
        'states': nfa['states'] | {start, accept},
        'transitions': transitions,
        'start': start,
        'accept': accept
    }


def nfa_plus(nfa):
    """
    Plus (+): one or more repetitions = nfa followed by nfa*.
    """
    return nfa_concatenation(nfa, nfa_kleene_star(nfa))


def nfa_optional(nfa):
    """
    Optional (?): zero or one occurrence.
    New start → ε→ nfa.start  AND  new start → ε→ new accept
    nfa.accept → ε→ new accept
    """
    start = new_state()
    accept = new_state()

    transitions = {**nfa['transitions']}
    transitions[start] = {EPSILON: [nfa['start'], accept]}
    transitions[nfa['accept']] = {EPSILON: [accept]}
    transitions[accept] = {}

    return {
        'states': nfa['states'] | {start, accept},
        'transitions': transitions,
        'start': start,
        'accept': accept
    }


# ──────────────────────────────────────────────
# Regex Parser (Recursive Descent)
# ──────────────────────────────────────────────

class RegexParser:
    """
    Parses a regular expression string and builds an ε-NFA using Thompson's Construction.

    Grammar:
      expr     → term ('|' term)*
      term     → factor factor*
      factor   → atom ('*' | '+' | '?')*
      atom     → CHAR | '(' expr ')'
    """

    def __init__(self, regex):
        self.regex = regex
        self.pos = 0

    def peek(self):
        """Look at current character without consuming."""
        if self.pos < len(self.regex):
            return self.regex[self.pos]
        return None

    def consume(self, expected=None):
        """Consume current character (optionally check it matches expected)."""
        ch = self.regex[self.pos]
        if expected and ch != expected:
            raise ValueError(f"Expected '{expected}' but got '{ch}' at position {self.pos}")
        self.pos += 1
        return ch

    def parse(self):
        """Entry point: parse the full regex."""
        nfa = self.parse_expr()
        if self.pos < len(self.regex):
            raise ValueError(f"Unexpected character '{self.regex[self.pos]}' at position {self.pos}")
        return nfa

    def parse_expr(self):
        """expr → term ('|' term)*"""
        nfa = self.parse_term()
        while self.peek() == '|':
            self.consume('|')
            right = self.parse_term()
            nfa = nfa_union(nfa, right)
        return nfa

    def parse_term(self):
        """term → factor factor* (concatenation)"""
        nfa = self.parse_factor()
        while self.peek() not in (None, '|', ')'):
            right = self.parse_factor()
            nfa = nfa_concatenation(nfa, right)
        return nfa

    def parse_factor(self):
        """factor → atom ('*' | '+' | '?')*"""
        nfa = self.parse_atom()
        while self.peek() in ('*', '+', '?'):
            op = self.consume()
            if op == '*':
                nfa = nfa_kleene_star(nfa)
            elif op == '+':
                nfa = nfa_plus(nfa)
            elif op == '?':
                nfa = nfa_optional(nfa)
        return nfa

    def parse_atom(self):
        """atom → CHAR | '(' expr ')'"""
        ch = self.peek()
        if ch is None:
            raise ValueError("Unexpected end of regex")
        if ch == '(':
            self.consume('(')
            nfa = self.parse_expr()
            self.consume(')')
            return nfa
        elif ch in ('|', ')', '*', '+', '?'):
            raise ValueError(f"Unexpected operator '{ch}' at position {self.pos}")
        else:
            self.consume()
            return nfa_for_symbol(ch)


def regex_to_nfa(regex):
    """
    Main function: convert a regex string to an ε-NFA.
    Returns the NFA dict with keys: states, transitions, start, accept.
    """
    reset_states()
    if not regex.strip():
        raise ValueError("Regular expression cannot be empty.")
    parser = RegexParser(regex.strip())
    return parser.parse()
