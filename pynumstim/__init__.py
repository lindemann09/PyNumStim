""" Python library to create symbolic number and arithmetic stimuli for psychological experiments

creating math problem stimuli with latex formulas and dvipng
"""

__author__ = "Oliver Lindemann"
__version__ = "0.2.6"

from ._problem import MathProblem
from ._mplist import MathProblemList
from ._data_sets import Datasets
from ._number import Num, TNum, TPyNum