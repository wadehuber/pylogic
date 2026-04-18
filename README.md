# pylogic

A lightweight Python library for logic programming with facts, rules, and deductive querying.

## Overview

PyLogic is a simple Prolog-inspired logic programming system that lets you define facts and rules, then query them to derive new conclusions. It uses unification and backward chaining to perform logical deduction.

**Perfect for:**

- Learning logic programming concepts
- Building simple rule-based systems
- Experimenting with deductive reasoning
- Prototyping knowledge bases

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/pylogic.git
cd pylogic
```

No external dependencies required—pylogic uses only Python standard library.

## Quick Start

### Using the Interactive CLI

Run with a logic program file:

```bash
python logic_program.py factsandrules.pl
```

Or run and be prompted for a filename:

```bash
python logic_program.py
```

Then enter queries at the `?` prompt:

```(text)
? parent(tom, X)
  ✓ parent(tom, bob)
  ✓ parent(tom, liz)

? ancestor(tom, X)
  ✓ ancestor(tom, bob)
  ✓ ancestor(tom, liz)
  ✓ ancestor(tom, ann)
  ✓ ancestor(tom, pat)
  ✓ ancestor(tom, jim)

? exit
```

### Using as a Library

```python
from logic_program import LogicProgram

# Create a logic program
logic = LogicProgram()

# Load facts and rules from a string
program = """
parent(tom, bob).
parent(bob, ann).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
"""

logic.load(program)

# Query the program
solutions = logic.query("grandparent(tom, X)")
print(solutions)  # Returns list of variable bindings
```

## Syntax

### Facts

Simple assertions about the world:

```prolog
parent(tom, bob).
parent(bob, ann).
likes(alice, pizza).
```

### Rules

Logical rules with conditions:

```prolog
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
```

Read `:-` as "if" and `,` as "and".

### Queries

Variables start with uppercase letters:

```prolog
parent(tom, X)        % Who are tom's children?
grandparent(X, ann)   % Who is ann's grandparent?
ancestor(tom, X)      % Who are all of tom's ancestors?
```

### Comments

Use `%` for comments:

```prolog
% This is a comment
parent(tom, bob).  % tom is the parent of bob
```

## Example: Family Relations

See `factsandrules.pl` for a complete family relations example:

```prolog
parent(tom, bob).
parent(tom, liz).
parent(bob, ann).
parent(bob, pat).
parent(pat, jim).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
sibling(X, Y) :- parent(Z, X), parent(Z, Y).
```

Run it:

```bash
python logic_program.py factsandrules.pl
```

Then try queries:

- `parent(tom, X)` — Direct children
- `grandparent(tom, X)` — Grandchildren
- `ancestor(tom, X)` — All descendants
- `sibling(bob, X)` — Bob's siblings

## How It Works

PyLogic uses:

- **Unification** — Matches query variables with facts and rule heads
- **Backward Chaining** — Recursively applies rules to derive new facts
- **Variable Renaming** — Avoids variable conflicts during rule application
- **Depth-First Search** — Explores all possible solutions

## API Reference

### `LogicProgram()`

Main class for logic programming.

#### Methods

- **`load(program_str)`** — Load facts and rules from a string
- **`query(query_str)`** — Execute a query, returns list of variable bindings
- **`print_facts()`** — Display all known facts
- **`print_rules()`** — Display all rules

### Example

```python
logic = LogicProgram()
logic.load("parent(a, b). parent(b, c). grandparent(X, Z) :- parent(X, Y), parent(Y, Z).")

# Get all solutions
solutions = logic.query("grandparent(a, X)")

# solutions is a list of dicts: [{'X': 'c'}]
for sol in solutions:
    print(f"X = {sol.get('X')}")
```

## Limitations

- No built-in operators (>, <, =, etc.)
- No arithmetic evaluation
- No cut (!) operator
- Simple forward/backward chaining only
- Not optimized for large datasets

PyLogic prioritizes simplicity and clarity over performance or advanced features.

## Contributing

Contributions welcome! Feel free to:

- Report issues
- Suggest features
- Submit pull requests
- Improve documentation

## License

MIT License - feel free to use this project however you like.

---

Happy deducing! 🎓

## Credits

Version 0.1 written with [Claude](https://claude.ai) by Anthropic.
