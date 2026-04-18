"""
A simple logic programming library for fact/rule-based deduction.
Supports basic Prolog-like syntax with facts and rules.
"""

import re
import sys
from typing import List, Dict, Set, Optional, Tuple


class Fact:
    """Represents a single fact (e.g., parent(john, mary))"""

    def __init__(self, predicate: str, args: List[str]):
        self.predicate = predicate
        self.args = args

    def __str__(self):
        if not self.args:
            return self.predicate
        return f"{self.predicate}({', '.join(self.args)})"

    def __eq__(self, other):
        return (isinstance(other, Fact) and
                self.predicate == other.predicate and
                self.args == other.args)

    def __hash__(self):
        return hash((self.predicate, tuple(self.args)))

    def copy(self):
        return Fact(self.predicate, self.args.copy())


class Rule:
    """Represents a rule (e.g., grandparent(X,Z) :- parent(X,Y), parent(Y,Z))"""

    def __init__(self, head: Fact, body: List[Fact]):
        self.head = head
        self.body = body

    def __str__(self):
        body_str = ", ".join(str(f) for f in self.body)
        return f"{self.head} :- {body_str}"


class LogicProgram:
    """Simple logic programming system for deduction"""

    def __init__(self):
        self.facts: Set[Fact] = set()
        self.rules: List[Rule] = []
        self._var_counter = 0

    def load(self, program_str: str):
        """Load facts and rules from a string"""
        for line in program_str.split('\n'):
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            self._parse_line(line)

    def _parse_line(self, line: str):
        """Parse a single fact or rule"""
        if ':-' in line:
            # It's a rule
            head_str, body_str = line.split(':-', 1)
            head = self._parse_fact(head_str.strip().rstrip('.'))
            body = self._split_facts(body_str)
            self.rules.append(Rule(head, body))
        else:
            # It's a fact
            fact_str = line.rstrip('.')
            fact = self._parse_fact(fact_str)
            self.facts.add(fact)

    def _split_facts(self, facts_str: str) -> List[Fact]:
        """Split comma-separated facts, respecting parentheses"""
        facts = []
        current = ""
        paren_depth = 0

        for char in facts_str:
            if char == '(':
                paren_depth += 1
                current += char
            elif char == ')':
                paren_depth -= 1
                current += char
            elif char == ',' and paren_depth == 0:
                if current.strip():
                    facts.append(self._parse_fact(current.strip()))
                current = ""
            else:
                current += char

        if current.strip():
            facts.append(self._parse_fact(current.strip()))

        return facts

    def _parse_fact(self, fact_str: str) -> Fact:
        """Parse a fact string into a Fact object"""
        match = re.match(r'(\w+)\((.*)\)', fact_str.strip())
        if not match:
            raise ValueError(f"Invalid fact: {fact_str}")

        predicate = match.group(1)
        args_str = match.group(2).strip()

        if not args_str:
            args = []
        else:
            args = [arg.strip() for arg in args_str.split(',')]

        return Fact(predicate, args)

    def query(self, query_str: str) -> List[Dict[str, str]]:
        """
        Execute a query and return all solutions.
        Returns a list of substitutions (variable bindings).
        """
        query_fact = self._parse_fact(query_str)
        solutions = []
        self._solve(query_fact, {}, solutions)
        return solutions

    def _solve(self, goal: Fact, bindings: Dict[str, str], solutions: List):
        """Solve a goal using forward chaining"""
        # Try to unify with known facts
        for fact in self.facts:
            unifier = self._unify(goal, fact, bindings)
            if unifier is not None:
                solutions.append(unifier.copy())

        # Try to unify with rule heads
        for rule in self.rules:
            renamed_rule = self._rename_variables(rule)
            unifier = self._unify(goal, renamed_rule.head, bindings)

            if unifier is not None:
                # Recursively solve the rule body
                self._solve_goals(renamed_rule.body, unifier, solutions)

    def _solve_goals(self, goals: List[Fact], bindings: Dict[str, str], solutions: List):
        """Solve a list of goals (conjunction)"""
        if not goals:
            solutions.append(bindings.copy())
            return

        first_goal = self._apply_bindings(goals[0], bindings)
        remaining = goals[1:]

        goal_solutions = []
        self._solve(first_goal, bindings, goal_solutions)

        for solution in goal_solutions:
            self._solve_goals(remaining, solution, solutions)

    def _unify(self, goal: Fact, fact: Fact, bindings: Dict[str, str]) -> Optional[Dict]:
        """Try to unify goal with fact, return updated bindings or None"""
        if goal.predicate != fact.predicate or len(goal.args) != len(fact.args):
            return None

        current = bindings.copy()

        for goal_arg, fact_arg in zip(goal.args, fact.args):
            goal_arg = self._deref(goal_arg, current)
            fact_arg = self._deref(fact_arg, current)

            if goal_arg == fact_arg:
                continue
            elif self._is_variable(goal_arg):
                current[goal_arg] = fact_arg
            elif self._is_variable(fact_arg):
                current[fact_arg] = goal_arg
            else:
                return None

        return current

    def _apply_bindings(self, fact: Fact, bindings: Dict[str, str]) -> Fact:
        """Apply variable bindings to a fact"""
        new_args = [self._deref(arg, bindings) for arg in fact.args]
        return Fact(fact.predicate, new_args)

    def _deref(self, term: str, bindings: Dict[str, str]) -> str:
        """Dereference a term (follow variable chains)"""
        if term in bindings:
            return self._deref(bindings[term], bindings)
        return term

    def _is_variable(self, term: str) -> bool:
        """Check if a term is a variable (starts with uppercase or _)"""
        return term and (term[0].isupper() or term[0] == '_')

    def _rename_variables(self, rule: Rule) -> Rule:
        """Rename all variables in a rule to avoid conflicts"""
        self._var_counter += 1
        suffix = f"_{self._var_counter}"

        def rename_args(args):
            return [f"{arg}{suffix}" if self._is_variable(arg) else arg for arg in args]

        new_head = Fact(rule.head.predicate, rename_args(rule.head.args))
        new_body = [Fact(f.predicate, rename_args(f.args)) for f in rule.body]

        return Rule(new_head, new_body)

    def print_facts(self):
        """Print all known facts"""
        print("Facts:")
        for fact in sorted(self.facts, key=str):
            print(f"  {fact}")

    def print_rules(self):
        """Print all rules"""
        print("Rules:")
        for rule in self.rules:
            print(f"  {rule}")

    def _extract_query_vars(self, query_str: str) -> Set[str]:
        """Extract variable names from a query string"""
        # Find all uppercase identifiers in the query
        matches = re.findall(r'\b([A-Z_]\w*)\b', query_str)
        return set(matches)


def interactive_main(filename=None):
    """Interactive mode: load a file and query it"""
    print("=" * 60)
    print("Logic Programming System - Interactive Mode")
    print("=" * 60)

    # Get filename from parameter or prompt for it
    if filename is None:
        filename = input("\nEnter the path to your logic program file: ").strip()

    try:
        with open(filename, 'r') as f:
            program_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Load the program
    logic = LogicProgram()
    try:
        logic.load(program_text)
    except Exception as e:
        print(f"Error parsing program: {e}")
        return

    # Display loaded program
    print(f"\n✓ Program loaded successfully from '{filename}'")
    print()
    logic.print_facts()
    print()
    logic.print_rules()
    print()

    # Query loop
    print("=" * 60)
    print("Enter queries (type 'exit' to quit)")
    print("=" * 60)

    while True:
        query = input("\n? ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break

        if not query:
            continue

        try:
            solutions = logic.query(query)
            seen = set()

            if solutions:
                for sol in solutions:
                    # Extract only the variables mentioned in the original query
                    query_vars = logic._extract_query_vars(query)
                    bindings = []
                    for var in sorted(query_vars):
                        val = logic._deref(var, sol)
                        bindings.append((var, val))

                    bindings_tuple = tuple(bindings)
                    if bindings_tuple not in seen:
                        seen.add(bindings_tuple)
                        result = query
                        for var, val in bindings:
                            result = result.replace(var, val)
                        print(f"  ✓ {result}")
            else:
                print(f"  ✗ No solutions found")

        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    # Check if filename provided as command-line argument
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    interactive_main(filename)