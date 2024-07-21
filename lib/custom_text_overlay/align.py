from enum import IntEnum
from typing import Tuple

class Position(IntEnum):
  TOP_LEFT = 1
  TOP_CENTER = 2
  TOP_RIGHT = 3
  CENTER_LEFT = 4
  CENTER = 5
  CENTER_RIGHT = 6
  BOTTOM_LEFT = 7
  BOTTOM_CENTER = 8
  BOTTOM_RIGHT = 9

def align(bounds: Tuple[int, int], inner_box: Tuple[int, int], position: Position, padding: int = 0) -> Tuple[int, int]:
  x, y = 0, 0
  if position in (Position.TOP_LEFT, Position.TOP_CENTER, Position.TOP_RIGHT):
    y = padding
  elif position in (Position.BOTTOM_LEFT, Position.BOTTOM_CENTER, Position.BOTTOM_RIGHT):
    y = bounds[1] - inner_box[1] - padding
  else:
    y = (bounds[1] - inner_box[1]) // 2
  if position in (Position.TOP_LEFT, Position.CENTER_LEFT, Position.BOTTOM_LEFT):
    x = padding
  elif position in (Position.TOP_RIGHT, Position.CENTER_RIGHT, Position.BOTTOM_RIGHT):
    x = bounds[0] - inner_box[0] - padding
  else:
    x = (bounds[0] - inner_box[0]) // 2
  return (x, y)

def getTextAlignFromPosition(position: Position) -> str:
  if position in (Position.TOP_RIGHT, Position.CENTER_RIGHT, Position.BOTTOM_RIGHT):
    return 'right'
  if position in (Position.TOP_CENTER, Position.CENTER, Position.BOTTOM_CENTER):
    return 'center'
  return 'left'
