from pathlib import Path
from typing import Dict, List, Optional, Union

from ._mplist import SimpleArithmeticList
from ._number import Num
from ._simple import SimpleArithmetic, TProperties
from ._two_step_problem import TwoStepArithmetic

FLD = "datasets"


class Datasets:
    @staticmethod
    def read_dataset(flname: Union[Path, str]) -> SimpleArithmeticList:
        rtn = SimpleArithmeticList()
        p = Path(__file__).parent.absolute()
        rtn.import_toml(p.joinpath(FLD, flname))
        return rtn

    @classmethod
    def Ahren_Jackson_79(cls) -> SimpleArithmeticList:
        return cls.read_dataset("Ahren_Jackson_79.toml")

    @classmethod
    def Lindemann_Tira_10(cls) -> SimpleArithmeticList:
        return cls.read_dataset("Lindemann_Tira_10.toml")

    @classmethod
    def Lyons_Bielock_12(cls) -> Dict[str, List[TwoStepArithmetic]]:
        """all possible 'Hard' problems as used by Lyons & Beilock (2012). Mathematics
        Anxiety: Separating the Math from the Anxiety. Cereb. Cortex 22, 2102–2110.

        (a*b) – c = d

        where a ≠ b, 5≤ a ≤ 9, 5≤ b ≤ 9, a*b ≥ 30, 15 ≤ c ≤19,
        and d > 0. Moreover, subtracting c from a*b always involved a
        borrow operation (e.g., “borrowing” from the tens place when
        subtracting 5 from 32). Half of the trials were valid (correct = ‘Yes’)
        and half were invalid (correct = ‘No’).

        """
        from .datasets import Lyons_Bielock

        return Lyons_Bielock.all_problems()

    @staticmethod
    def problem_space(
        operation: str,
        operand1: List[int],
        operand2: List[int],
        incorrect_deviations: Optional[List[int]] = None,
        decade_results=True,
        tie_problem=True,
        negative_results=True,
        carry_problems=True,
        properties: Optional[TProperties] = None,
    ) -> SimpleArithmeticList:
        """creates a MathProblemList comprising the defined problem space"""
        if incorrect_deviations is None:
            inc_dev = set()
        else:
            inc_dev = set(incorrect_deviations)
        inc_dev.add(0)  # correct result

        rtn = SimpleArithmeticList()
        for op1 in operand1:
            for op2 in operand2:
                if tie_problem or op1 != op2:
                    for dev in inc_dev:
                        p = SimpleArithmetic(op1, operation, op2)
                        correct = p.calc()
                        result = correct + dev
                        if not decade_results and (
                            result % 10 == 0 or correct % 10 == 0
                        ):
                            continue
                        if not negative_results and (result < 0 or correct < 0):
                            continue
                        n_carry = p.n_carry()
                        if not carry_problems and (n_carry is None or n_carry > 0):
                            continue
                        p.result = Num(p.calc() + dev)
                        if isinstance(properties, Dict):
                            p.update_properties(properties)
                        rtn.append(p)
        return rtn
