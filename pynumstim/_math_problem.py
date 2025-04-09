from abc import ABCMeta, abstractmethod
from hashlib import md5


class MathProblem(metaclass=ABCMeta):
    @abstractmethod
    def tex(self, brackets: bool = True) -> str:
        pass

    @abstractmethod
    def label(self) -> str:
        pass

    def hash(self) -> str:
        md5_object = md5(self.label().encode())
        return md5_object.hexdigest()


class LaTexProblem(MathProblem):
    def __init__(self, tex_code: str, label: str) -> None:
        self.code = tex_code
        self._label = label

    def tex(self, brackets: bool = True) -> str:
        return self.code

    def label(self) -> str:
        return self._label
