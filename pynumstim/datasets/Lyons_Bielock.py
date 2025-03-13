from typing import Dict, List

from pynumstim import Num, TNum, TwoStepArithmetic


def make_problem_Lyons_Beilock(
    a: TNum, b: TNum, c: TNum, result: TNum | None = None
) -> TwoStepArithmetic:
    """'Hard' problems as used by Lyons & Beilock (2012). Mathematics
    Anxiety: Separating the Math from the Anxiety. Cereb. Cortex 22, 2102–2110.
    """

    a = Num(a)
    b = Num(b)
    c = Num(c)
    if result is None:
        result = a * b - c

    rtn = TwoStepArithmetic(a, b, c, operation1="*", operation2="-", result=result)
    return rtn


def _is_admissible(prob: TwoStepArithmetic) -> bool:
    """admissible regarding criteria of  Lyons and Beilock

    (a*b) – c = d, where a ≠ b, 5≤ a ≤ 9, 5≤ b ≤ 9, a*b ≥ 30, 15 ≤ c ≤19,
    and d > 0. Moreover, subtracting c from a*b always involved a
    borrow operation (e.g., “borrowing” from the tens place when
    subtracting 5 from 32). Half of the trials were valid (correct = ‘Yes’)
    and half were invalid (correct = ‘No’).
    """

    if prob.result is None:
        return False
    a = prob.operand1.py_number()
    b = prob.operand2.py_number()
    c = prob.operand3.py_number()
    if (
        a >= 5
        and a <= 9
        and b >= 5
        and b <= 9
        and c >= 15
        and c <= 19
        and a != b
        and a * b >= 30
        and prob.result > 0
    ):
        x = a * b
        # check require borrowing
        while x > 0 or c > 0:
            digit_x = x % 10  # Extract the least digit
            digit_c = c % 10
            if digit_c > digit_x:
                return True  # requires borrowing
            x //= 10

    return False


def all_problems() -> Dict[str, List[TwoStepArithmetic]]:
    correct = []
    too_small_result = []
    too_large_result = []
    for a in range(5, 9 + 1):
        for b in range(5, 9 + 1):
            for c in range(15, 19 + 1):
                p = make_problem_Lyons_Beilock(a, b, c)
                if _is_admissible(p):
                    correct.append(p)
                    s = make_problem_Lyons_Beilock(a, b, c, int(float(p.result) - 2))  # type: ignore
                    l = make_problem_Lyons_Beilock(a, b, c, int(float(p.result) + 2))  # type: ignore
                    too_small_result.append(s)
                    too_large_result.append(l)

    return {
        "correct": correct,
        "too_small_result": too_small_result,
        "too_large_result": too_large_result,
    }


print(len(all_problems()["correct"]))
