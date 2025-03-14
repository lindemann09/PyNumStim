import os
from pathlib import Path
from typing import List, Optional, Union

from sympy import preview

from ._math_problem import LaTex, MathProblem
from ._mplist import SimpleArithmeticList
from ._simple import LATEX_SYMBOL_NAMES, SimpleArithmetic
from ._two_step_problem import TwoStepArithmetic


def tex_to_image(
    source: Union[str, MathProblem],
    path: Optional[Union[Path, str]] = None,
    segmented=False,
    resolution: int = 400,
    fg: str = "White",
    bg: str = "Transparent",
):
    if path is None:
        if isinstance(source, MathProblem):
            path = source.label() + ".png"  # use label
        else:
            raise ValueError(
                f"Path is required, if you create images from {type(source)}"
            )

    if isinstance(source, MathProblem):
        return _from_problem(
            source,
            folder=path,
            segmented=segmented,
            resolution=resolution,
            fg=fg,
            bg=bg,
        )
    elif isinstance(source, str):
        return _from_tex(source, filename=path, resolution=resolution, fg=fg, bg=bg)


def problem_list_to_images(
    problems: SimpleArithmeticList | List[TwoStepArithmetic] | List[SimpleArithmetic],
    folder: Union[Path, str],
    segmented=False,
    resolution: int = 400,
    fg: str = "White",
    bg: str = "Transparent",
):
    """segmented: single files for each number and operation"""
    # make pictures
    os.makedirs(folder, exist_ok=True)
    if isinstance(problems, SimpleArithmeticList):
        problem_list = problems.list
    else:
        problem_list = problems

    if not segmented:
        done = set()
        for x in problem_list:
            print("png: ", x.label())
            if x.label() not in done:
                _from_problem(
                    x,
                    folder=folder,
                    segmented=False,
                    resolution=resolution,
                    fg=fg,
                    bg=bg,
                )
                done.add(x.label())
    else:
        _create_opertion_symbols(folder=folder, resolution=resolution, fg=fg, bg=bg)
        # problem_stimuli
        stim = set()
        for x in problem_list:
            stim.add((x.operand1.tex(), x.operand1.label()))
            stim.add((x.operand2.tex(), x.operand2.label()))
            if x.result is not None:
                stim.add((x.result.tex(), x.result.label()))

        for tex, label in stim:
            print("png: " + label)
            _from_tex(
                f"$${tex}$$",
                filename=os.path.join(folder, "n" + f"{label}.png"),
                resolution=resolution,
                fg=fg,
                bg=bg,
            )


def _from_tex(
    tex_str: str,
    filename: Union[Path, str],
    resolution: int = 400,
    fg: str = "White",
    bg: str = "Transparent",
):
    """latex to PNG"""
    return preview(
        tex_str,
        dvioptions=["-D", str(resolution), "-fg", fg, "-bg", bg],
        viewer="file",
        filename=filename,
        euler=False,
    )


def _from_problem(
    problem: MathProblem,
    folder: Union[Path, str],
    segmented: bool = False,
    resolution: int = 400,
    fg: str = "White",
    bg: str = "Transparent",
) -> str:
    """returns the filename, if not segmented"""

    os.makedirs(folder, exist_ok=True)
    if isinstance(problem, LaTex):
        flname = problem.label()
        tex_code = problem.tex()
    else:
        flname = f"p{problem.label()}"
        tex_code = f"$${problem.tex()}$$"
    flname = os.path.join(folder, f"{flname}.png")

    if not segmented:
        _from_tex(tex_code, filename=flname, resolution=resolution, fg=fg, bg=bg)
    else:
        # segmented
        if not isinstance(problem, SimpleArithmetic):
            raise ValueError(
                "Segmentation is only implemented for SimpleArithmetic problems, "
                + f"not for {type(problem)}"
            )

        os.makedirs(folder, exist_ok=True)
        _create_opertion_symbols(folder, resolution=resolution, fg=fg, bg=bg)
        stim = set()
        stim.add((problem.operand1.tex(), problem.operand1.label()))
        stim.add((problem.operand2.tex(), problem.operand2.label()))
        if problem.result is not None:
            stim.add((problem.result.tex(), problem.result.label()))
        for tex, label in stim:
            print("png: " + label)
            _from_tex(
                f"$${tex}$$",
                filename=os.path.join(folder, "n" + f"{label}.png"),
                resolution=resolution,
                fg=fg,
                bg=bg,
            )

    return flname


def _create_opertion_symbols(
    folder: Union[Path, str],
    resolution: int = 400,
    fg: str = "White",
    bg: str = "Transparent",
):
    # create symbols, segmented
    for symbol, name in LATEX_SYMBOL_NAMES.items():
        _from_tex(
            f"$${symbol}$$",
            filename=os.path.join(folder, f"{name}.png"),
            resolution=resolution,
            fg=fg,
            bg=bg,
        )
