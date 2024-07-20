from enum import Enum, IntEnum
from typing import Tuple
from PIL import ImageDraw, ImageFont, Image

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

def draw_text(img: Image.Image, text: str, font_size: int, font_color: str, position: Position) -> Image.Image:
    draw = ImageDraw.Draw(img)

    margin = 0
    padding = 4
    font = ImageFont.truetype("D:/ai/automatic1111/repositories/generative-models/data/DejaVuSans.ttf", font_size)  # Use a specific font file

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    box_width = text_width + padding * 2
    box_height = text_height + padding * 2

    box_position = align(img.size, (box_width, box_height), position, margin)
    text_position = (box_position[0] + padding, box_position[1] + padding)

    img = img.convert('RGBA')
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((box_position[0], box_position[1], box_position[0] + box_width, box_position[1] + box_height), fill=(0, 0, 0, 127))
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    img_draw = ImageDraw.Draw(img)
    img_draw.text(text_position, text, font=font, fill=font_color)

    return img
