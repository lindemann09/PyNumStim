"""Python library to create symbolic number and arithmetic stimuli for psychological experiments

creating math problem stimuli with latex formulas and dvipng
"""

__author__ = "Oliver Lindemann"
__version__ = "0.3-dev"

from ._data_sets import Datasets
from ._mplist import SimpleArithmeticList
from ._number import Num, TNum, TPyNum
from ._problem import MathProblem, SimpleArithmetic
from ._two_step_problem import TwoStepArithmetic
