import unittest
from typing import Optional, Tuple

# ================================================================
# Arithmetic Expression Evaluator
# (inputs string and returns int() on success and None on failure)
# ================================================================

def evaluate(expression: str) -> Optional[int]:
    """Evaluate arithmetic expression and return an integer result.
    Returns:
      - Computed integer on success
      - None on error
    """
    # Remove all whitespace
    s = ''.join(ch for ch in expression if not ch.isspace())
    n = len(s)

    # Reject any character not in valid tokens in the assignment
    allowed = set("0123456789+-*/()")
    for ch in s:
        if ch not in allowed:
            return None

    # Verify the parentheses
    # Ensure number of open ')' is same as closed '('
    balance = 0
    for ch in s:
        if ch == '(':
            balance += 1
        elif ch == ')':
            balance -= 1
            if balance < 0:
                # Found a closing ')' without a matching open '('
                return None
    if balance != 0:
        # Mismatch: some open '(' were not closed
        return None

    # Method to parse and convert the number to int along with optional unary +/-, requires at least one digit
    def parse_number(i: int) -> Tuple[Optional[int], int]:
        """Parse a signed integer.
        Returns (value, next_i) on success, (None, i) on failure.
        """
        if i >= n:
            return None, i

        #Expecting number, handling the optional unary sign before digits
        sign_char = None
        if s[i] in '+-':
            sign_char = s[i]
            i += 1
            if i >= n:
                # Sign cannot be last string, it is an error
                return None, i

        # Collect all the digits of the number
        start = i
        while i < n and s[i].isdigit():
            i += 1

        if i == start:
            # No digits after optional sign → invalid number
            return None, start

        # Convert string to int
        num_str = s[start:i]
        try:
            num = int(num_str)
            if sign_char == '-':
                num = -num  # apply sign when it is '-' as + is optional
            return num, i
        except ValueError:
            # Shouldn't occur as we already check for isdigit(), but safe to handle
            return None, start

    # Method to implement the valid arithmetic operation with truncation-toward-zero division
    def perform_arithmetic_op(a: int, op: str, b: int) -> Optional[int]:
        """Implement the arithmetic operation(op) on the operands(a,b).
        Returns value on success, None on failure.
        """
        if op == '+':
            return a + b
        if op == '-':
            return a - b
        if op == '*':
            return a * b
        if op == '/':
            if b == 0:
                return None
            # Truncate toward zero
            return int(a / b)
        return None

    # Parse an expression (parentheses-first, left-to-right within level and parentheses close)
    def parse_expression(i: int, sub_expr: bool = False)-> tuple[Optional[int], int, bool]:
        """Parse expression from left to right.
        Returns (value, next_i, ok).
        If sub_expr=True, stop at a matching ')'.
        """
        result: Optional[int] = None
        current_op: Optional[str] = None
        expecting_number = True

        # This is how I approached -
        # 2 main cases -
        # case 1. expecting numbers -(numbers are expected 1.after a unary operator followed by parentheses
        # 2.after a parentheses, 3.after a unary operator and also 4.after
        # an operator) - these scenarios are hit with expecting_number set to True.
        # case 2. expecting operator or closing parentheses
        # Next main logic is recursive call to parse the sub expression within the parentheses, in 2 cases -
        # 1. when a unary operator followed by '(' like +( 2. '(' is encountered
        # to differentiate the recursive call, bool sub_expr is set to true in parse_expression.

        while i < n:
            ch = s[i]

            if expecting_number:
                # Unary sign directly before a parentheses of a subexpression
                # +(expr) is a no-op; -(expr) negates the subexpression
                if ch in '+-' and i + 1 < n and s[i + 1] == '(':
                    unary = -1 if ch == '-' else 1
                    # Advance to '(' and parse the subexpression
                    i += 1  # now s[i] == '('
                    sub_val, next_i, ok = parse_expression(i + 1, sub_expr=True)
                    if not ok or sub_val is None:
                        return None, i, False
                    i = next_i
                    # apply unary operator outside the parentheses to the result
                    operand = unary * sub_val

                elif ch == '(':
                    # Recurse into subexpression
                    sub_val, next_i, ok = parse_expression(i + 1, sub_expr=True)
                    if not ok or sub_val is None:
                        return None, i, False
                    i = next_i
                    operand = sub_val

                elif ch.isdigit() or ch in '+-':
                    # Parse signed number (sign must be followed by digits) - this is the unary sign
                    # before the number
                    value, next_i = parse_number(i)
                    if value is None:
                        return None, i, False
                    i = next_i
                    operand = value

                elif ch == ')':
                    # Can't close group when we expected an operand (e.g., "()")
                    # This is not expected, still safe to catch and return error
                    return None, i, False

                else:
                    # Any other character would have been filtered earlier
                    return None, i, False

                # Organise operands into the expression, first operand is copied to result
                if result is None:
                    result = operand
                else:
                    if current_op is None:
                        return None, i, False
                    applied = perform_arithmetic_op(result, current_op, operand)
                    if applied is None:
                        return None, i, False
                    result = applied
                # set to false before leaving
                expecting_number = False

            else:
                # Expect an operator or a closing ')'
                if ch in '+-*/':
                    current_op = ch
                    i += 1
                    expecting_number = True
                elif ch == ')':
                    if sub_expr:
                        i += 1
                        # Cannot end with a pending operator
                        if result is None or (current_op is not None and expecting_number):
                            return None, i, False
                        return result, i, True
                    else:
                        # Unmatched ')'
                        return None, i, False
                else:
                    # Invalid where operator expected
                    return None, i, False

        # End-of-string or expression handling any incomplete errors
        if sub_expr:
            # if still sub_expr is true, which means we have not encountered closing ')'
            return None, i, False
        if result is None or expecting_number:
            # Empty input or trailing operator
            return None, i, False
        return result, i, True

    # Kick off the top-level expression parse
    final_val, _, ok = parse_expression(0, sub_expr=False)
    return final_val if ok else None


# ============================================================
# Different test scenarios
# ============================================================

class EvaluateExpressionTests(unittest.TestCase):
    def assertEval(self, expr: str, expected: Optional[int]):
        got = evaluate(expr)
        self.assertEqual(
            got, expected,
            msg=f"{expr!r} -> {got} (expected {expected})"
        )

    # Test scenario examples as in the assignment
    def test_examples(self):
        self.assertEval("1 + 3", 4)
        self.assertEval("(1 + 3) * 2", 8)
        self.assertEval("(4 / 2) + 6", 8)
        self.assertEval("4 + (12 / (1 * 2))", 10)
        self.assertEval("(1 + (12 * 2)", None)  # mismatched ')'

    # Different parenthesis validation testcases
    def test_parentheses_validation_early(self):
        self.assertEval(")", None)             # bad expression ')'
        self.assertEval(")1+2(", None)         # bad expression
        self.assertEval("(1+2))", None)        # extra ')'
        self.assertEval("((1+2)", None)        # missing ')'
        self.assertEval("1 + 2)", None)        # unmatched ')'
        self.assertEval("", None)              # handled later as empty (but OK)
        self.assertEval("((2))", 2)            # considering valid to return a value
        self.assertEval("((2 + 3) * 4) / 5", 4) # nested parentheses

    # Left-to-right testcases
    def test_left_to_right(self):
        self.assertEval("1 + 3 * 4", 16)       # first (1+3)=4;next 4*4=16
        self.assertEval("20 / 3 / 2", 3)       # first int(20/3)=6;next int(6/2)=3

    # Whitespace ignoring testcases
    def test_whitespace(self):
        self.assertEval("  7   -   2   ", 5)
        self.assertEval("(  8+2 )/ 5  ", 2)

    # Signed integers (+/- before numbers) testcases
    def test_signed_integers(self):
        self.assertEval("-5 + 3", -2)
        self.assertEval("(+7) * (-2)", -14)
        self.assertEval("+5", 5)
        self.assertEval("4 + +5", 9)
        self.assertEval("-4 + (+5)", 1)
        self.assertEval("20 / -4 / +2", -2)     # int(20/-4)=5; int(-5/2)=2

    # Unary +/- operator before parentheses testcases
    def test_unary_over_parentheses(self):
        self.assertEval("+(1+2)", 3)
        self.assertEval("-(1+2)", -3)          # minus negates group
        self.assertEval("4 * -(2+3)", -20)     # 4 * (-5) = -20
        self.assertEval("-(-3)", 3)   # double negation, is positive
        self.assertEval("+(-5)", -5)
        self.assertEval("-(+5)", -5)

    # Division by zero testcases
    def test_division_by_zero(self):
        self.assertEval("10 / 0", None)
        self.assertEval("(1 + 2) / (3 - 3)", None)

    # Invalid characters / symbols / variables(instead of numbers)/ decimal testcases
    def test_invalid_characters(self):
        self.assertEval("2 & 3", None)
        self.assertEval("12.5 + 3", None)
        self.assertEval("10,000 + 1", None)
        self.assertEval("3 % 2", None)
        self.assertEval("square(3)", None)
        self.assertEval("√9", None)
        self.assertEval("x + y", None)

    # expression error testcases
    def test_structure_errors(self):
        self.assertEval("1 +", None)           # ends with operator
        self.assertEval("()", None)            # empty expression

if __name__ == "__main__":
    unittest.main(verbosity=2)