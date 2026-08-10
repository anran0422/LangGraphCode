from typing import Annotated
from typing_extensions import TypedDict
import operator

class State(TypedDict):
    step: Annotated[list[str], operator.add]