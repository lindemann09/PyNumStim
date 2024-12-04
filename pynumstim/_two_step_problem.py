from __future__ import annotations

from typing import Any, Dict, Optional, Set

from ._number import Num, TNum, TPyNum
from ._problem import MathProblem, SimpleMathProblem, TProperties


class TwoStepMathProblem(MathProblem):
    def __init__(
        self,
        operand1: TNum,
        operand2: TNum,
        operand3: TNum,
        operation1: str,
        operation2: str,
        result: Optional[TNum] = None,
        properties: Optional[TProperties] = None,
    ) -> None:
        """properties: dict of properties.
        Keys represent the property name and must be text strings
        """

        self.step1 = SimpleMathProblem(
            operand1=operand1, operation=operation1, operand2=operand2
        )
        self.step2 = SimpleMathProblem(
            operand1=self.step1.calc(),
            operation=operation2,
            operand2=operand3,
            result=result,
            properties=properties,
        )
