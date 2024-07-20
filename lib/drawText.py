from PIL import Image, ImageDraw, ImageFont, ImageColor
from lib.align import align, Position
from lib.logger import logger

def drawText(img: Image.Image, text: str, fontSize: int, textColor: str, position: Position, backgroundColor: str, backgroundOpacity: int, margin: int = 0, padding: int = 8, outline: int = 0, outlineColor: str = '#000000', outlineOpacity: int = 255) -> Image.Image:
  draw = ImageDraw.Draw(img)
  font = ImageFont.truetype("D:/ai/automatic1111/modules/Roboto-Regular.ttf", fontSize)
  multilineAlign = 'left'
  if position == 4 or position == 5 or position == 6:
    multilineAlign = 'center'
  elif position == 7 or position == 8 or position == 9:
    multilineAlign = 'right'
  drawTextArgs = {
    'text': text,
    'font': font,
    'spacing': 0,
    'align': multilineAlign,
    'stroke_width': outline,
  }

  textBounds = draw.multiline_textbbox((0, 0), **drawTextArgs)
  textWidth = textBounds[2] - textBounds[0]
  textHeight = textBounds[3] - textBounds[1]
  boxWidth = textWidth + padding * 2
  boxHeight = textHeight + padding * 2

  boxPosition = align(img.size, (boxWidth, boxHeight), position, margin)
  textPosition = (boxPosition[0] + padding, boxPosition[1] + padding)

  logger.debug(f'Text bounds: [x: {textPosition[0]}, y: {textPosition[1]}, width: {textWidth}, height: {textHeight}]')
  logger.debug(f'Background bounds: [x: {boxPosition[0]}, y: {boxPosition[1]}, width: {boxWidth}, height: {boxHeight}]')

  img = img.convert('RGBA')
  overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
  overlayDraw = ImageDraw.Draw(overlay)
  backgroundInkSolid = ImageColor.getrgb(backgroundColor)
  backgroundInk = (*backgroundInkSolid, backgroundOpacity)
  overlayDraw.rectangle((boxPosition[0], boxPosition[1], boxPosition[0] + boxWidth, boxPosition[1] + boxHeight), fill=backgroundInk)
  img = Image.alpha_composite(img, overlay)
  img = img.convert('RGB')
  imgDraw = ImageDraw.Draw(img)

  outlineColorSolid = ImageColor.getrgb(outlineColor)
  outlineColor = (*outlineColorSolid, outlineOpacity)
  imgDraw.multiline_text(textPosition, fill=textColor, **drawTextArgs, stroke_fill=outlineColor)

  return img
