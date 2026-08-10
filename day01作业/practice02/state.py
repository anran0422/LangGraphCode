from typing import Annotated
from typing_extensions import TypedDict
import operator

class State(TypedDict):
    node_count: Annotated[int, operator.add]