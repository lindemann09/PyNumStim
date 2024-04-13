import os
from pathlib import Path
from typing import Optional, Union
from sympy import preview

from ._problem import MathProblem, SYMBOL_NAMES
from ._mplist import MathProblemList

def from_tex(tex_str: str,
             filename: Union[Path, str],
             resolution: int = 400,
             fg: str = "White", bg: str = "Transparent"):
    """latex to PNG """
    return preview(tex_str,
                   dvioptions=['-D', str(resolution), "-fg", fg, "-bg", bg],
                   viewer='file', filename=filename, euler=False)


def from_problem(problem: MathProblem,
                 filename: Optional[Union[Path, str]] = None,
                 resolution: int = 400,
                 fg: str = "White",
                 bg: str = "Transparent"):
    if filename is None:
        filename = problem.label() + ".png"
    return from_tex(f'$${problem.tex()}$$',
                    filename=filename,
                    resolution=resolution,
                    fg=fg, bg=bg)


def from_problem_list(problems: MathProblemList,
                      folder: Union[Path, str],
                      segmented=False,
                      resolution: int = 400,
                      fg: str = "White",
                      bg: str = "Transparent"):
    """segmented: single files for each number and operation"""
    # make pictures
    os.makedirs(folder, exist_ok=True)
    if not segmented:
        done = set()
        for x in problems.list:
            print("png: ", x.label())
            flname = os.path.join(folder, "p" + x.label() + ".png")
            if flname not in done:
                from_problem(x, filename=flname, resolution=resolution,
                             fg=fg, bg=bg)
                done.add(flname)
    else:
        # create symbols
        for symbol, name in SYMBOL_NAMES.items():
            from_tex(f'$${symbol}$$',
                     filename=os.path.join(folder, f"{name}.png"),
                     resolution=resolution,
                     fg=fg, bg=bg)
        # problem_stimuli
        stim = set()
        for x in problems.list:
            stim.add((x.operant1.tex(), x.operant1.label()))
            stim.add((x.operant2.tex(), x.operant2.label()))

            if x.result is not None:
                stim.add((x.result.tex(), x.result.label()))

        for tex, label in stim:
            print("png: " + label)
            from_tex(f'$${tex}$$',
                    filename=os.path.join(folder, "n" + f"{label}.png"),
                    resolution=resolution,
                    fg=fg, bg=bg)
