from __future__ import annotations

import re
from copy import copy
from fractions import Fraction
from typing import Any, Dict, Optional, Set

from ._math_problem import MathProblem
from ._number import Num, TNum, TPyNum

LATEX_TIMES = "\\times"  # "\\cdot"
LATEX_SYMBOL_NAMES = {
    "=": "equal",
    "+": "plus",
    LATEX_TIMES: "multiply",
    "/": "divide",
    "-": "minus",
}

TProperties = Dict[str, Any]


class SimpleArithmetic(MathProblem):
    LABEL_MULTI = "t"  # multiplication, times
    LABEL_DIVIDE = "d"  # divide
    OPERATIONS = ["+", "-", "*", "/", LABEL_MULTI, LABEL_DIVIDE]

    def __init__(
        self,
        operand1: TNum,
        operation: str,
        operand2: TNum,
        result: Optional[TNum] = None,
        properties: Optional[TProperties] = None,
    ) -> None:
        """properties: dict of properties.
        Keys represent the property name and must be text strings
        """

        self.operand1 = Num(operand1)
        self.operand2 = Num(operand2)

        if operation not in SimpleArithmetic.OPERATIONS:
            raise ValueError(f"Unknown operation: '{operation}'")
        if operation == SimpleArithmetic.LABEL_MULTI:
            self.operation = "*"
        elif operation == SimpleArithmetic.LABEL_DIVIDE:
            self.operation = "/"
        else:
            self.operation = operation

        if result is None:
            self.result = None
        else:
            self.result = Num(result)
        self.properties = copy(properties)

    def number_types(self) -> Set[type]:
        rtn = set((self.operand1.number_type(), self.operand2.number_type()))
        if self.result is not None:
            rtn.add(self.result.number_type())
            return rtn
        else:
            return rtn

    def operation_label(self) -> str:
        if self.operation == "*":
            return self.LABEL_MULTI
        elif self.operation == "/":
            return self.LABEL_DIVIDE
        else:
            return self.operation

    def update_properties(self, props: Dict[str, Any]):
        if isinstance(self.properties, dict):
            self.properties.update(props.copy())
        else:
            self.properties = props.copy()

    def has_properites(self, props: TProperties) -> bool:
        """returns if problem is the properties defined in props"""
        if self.properties is None:
            return False
        for key, value in props.items():
            if key not in self.properties or self.properties[key] != value:
                return False
        return True

    def _as_dict(self) -> Dict[str, Any]:
        """minimal dict representation of the problem without properties"""
        rtn = {
            "op1": self.operand1.label(),
            "operation": self.operation,
            "op2": self.operand2.label(),
        }

        if self.result is None:
            rtn["result"] = ""
        else:
            rtn["result"] = self.result.label()
        return rtn

    def problem_dict(
        self, incl_hash=False, problem_size=False, n_carry=False
    ) -> Dict[str, str | int | float]:
        rtn = self._as_dict()
        if self.result is not None:
            rtn["correct"] = int(self.is_correct())
            rtn["dev"] = self.deviation()

        if problem_size:
            rtn["prob_size"] = self.problem_size()
        if n_carry:
            nc = self.n_carry()
            if nc is not None:
                rtn["n_carry"] = nc

        rtn["label"] = self.label()
        if isinstance(self.properties, dict):
            rtn.update(self.properties)
        if incl_hash:
            rtn["hash"] = self.hash()
        return rtn

    def calc(self) -> TPyNum:
        # returns correct result
        o1 = self.operand1.py_number()
        o2 = self.operand2.py_number()

        if self.operation == "+":
            return o1 + o2
        elif self.operation == "-":
            return o1 - o2
        elif self.operation == "*":
            return o1 * o2
        elif self.operation == "/":
            if isinstance(o1, float) or isinstance(o2, float):
                return o1 / o2
            else:
                return Fraction(o1, o2)
        else:
            # should never happen
            raise RuntimeError(f"Unknown operation: '{self.operation}'")

    def deviation(self) -> Optional[float]:
        """deviation from correct"""
        if self.result is None:
            return None
        else:
            return float(self.result) - self.calc()

    def tex(self, brackets: bool = False) -> str:
        o1 = self.operand1.tex()
        o2 = self.operand2.tex()
        if self.operation == "*":
            operation = LATEX_TIMES
        else:
            operation = self.operation
        rtn = f"{o1} {operation} {o2}"
        if brackets:
            rtn = f"({rtn})"
        if self.result is not None:
            rtn += f" = {self.result.tex()}"
        return rtn

    def label(self) -> str:
        """labels not not have no spaces and not the characters \\*{}=
        They can thus be used for filenames and as ids in data tables
        """
        o1 = self.operand1.label()
        o2 = self.operand2.label()
        rtn = f"{o1}{self.operation_label()}{o2}"
        if self.result is not None:
            rtn += f"={self.result.label()}"
        return rtn

    def __str__(self) -> str:
        """text representation"""
        o1 = self.operand1.label()
        o2 = self.operand2.label()
        rtn = f"{o1} {self.operation} {o2}"
        if self.result is not None:
            rtn += f" = {self.result.label()}"
        return rtn

    def is_correct(self):
        if self.result is None:
            return False
        return self.calc() == self.result.py_number()

    def n_carry(self) -> Optional[int]:
        """number of carry operations for addition and subtraction
        else None"""

        if self.operand1.is_fraction() or self.operand2.is_fraction():
            return None
        if self.operation == "+":
            subtraction = False
        elif self.operation == "-":
            subtraction = True
        else:
            return None

        str_op1 = str(self.operand1)
        str_op2 = str(self.operand2)
        # Get the length of the longer number
        max_length = max(len(str_op1), len(str_op2))
        # Add leading zeros to make the numbers have the same length
        str_op1 = str_op1.zfill(max_length)
        str_op2 = str_op2.zfill(max_length)

        current_carry = 0
        ncarry = 0
        # Iterate over digits from right to left
        for i in range(max_length - 1, -1, -1):
            if subtraction:
                res = int(str_op1[i]) - int(str_op2[i])
                res -= current_carry
            else:
                res = int(str_op1[i]) + int(str_op2[i])
                res += current_carry

            if (subtraction and res < 0) or (not subtraction and res >= 10):
                ncarry += 1
                current_carry = 1
            else:
                current_carry = 0

        return ncarry

    def problem_size(self) -> float:
        return (_size(self.operand1) + _size(self.operand2)) / 2.0

    @staticmethod
    def parse(txt: str, properties: Optional[TProperties] = None) -> SimpleArithmetic:
        """fractions have to presented like in labels: frac5_6
        can also convert labels to problems
        """
        x = txt.split("=")
        if len(x) < 3:
            if len(x) == 1:
                result = None
            else:
                result = Num(x[1])

            op1, op2, operation = (None, None, None)
            for op in SimpleArithmetic.OPERATIONS:
                try:
                    op1, op2 = _split_after_digit(x[0], op)
                    operation = op
                    break
                except ValueError:
                    pass

            if None not in (op1, op2, operation):
                return SimpleArithmetic(op1, operation, op2, result, properties)  # type: ignore

        raise ValueError(f"Can't convert '{txt}' to MathProblem.")

    def same_operands(self) -> bool:
        return self.operand1.py_number() == self.operand2.py_number()

    def decade_solution(self) -> bool:
        return self.calc() % 10 == 0

    def same_parities(self) -> bool:
        return self.operand1.py_number() % 2 == self.operand2.py_number() % 2


def _split_after_digit(txt: str, letter: str):
    # splits txt at letter only if a digit proceeds the letter
    if letter in ["+", "*", "\\"]:  # escaping required
        letter = f"\\{letter}"
    a = re.search(f"\\d\\s*{letter}", txt)
    if a is not None:
        return txt[: a.span()[0] + 1], txt[a.span()[1] :]
    else:
        return txt


def _size(num: Num) -> TPyNum:
    """helper for calculation problem size with fractions.
    In this case, return mean of numerator and denominator"""
    if num.is_fraction():
        return (num.numerator + num.denominator) / 2.0
    else:
        return num.py_number()
