from PIL import Image, ImageDraw, ImageFont
from time import strftime
import numpy
import os
import sys
import subprocess
import json
import re
import datetime


class termcolours:
  YELLOW = '\033[93m'
  LRED = '\033[1;31m'
  GREEN = '\033[0;32m'
  PURPLE = '\033[0;35m'
  NC = '\033[0m'  # No Colour


times = dict()
title = None


def averageFrameColour(frame):
  i = Image.open(frame).convert("RGB")
  h = i.histogram()

  # split into red, green, blue
  r = h[0:256]
  g = h[256:256 * 2]
  b = h[256 * 2: 256 * 3]

  # perform the weighted average of each channel:
  # the *index* is the channel value, and the *value* is its weight

  if r:
    aveR = sum(i * w for i, w in enumerate(r)) / sum(r)
  if g:
    aveG = sum(i * w for i, w in enumerate(g)) / sum(g)
  if b:
    aveB = sum(i * w for i, w in enumerate(b)) / sum(b)

  try:
    ave = (aveR, aveG, aveB)
    return (ave)
  except:
    Exception

  i.close()


def calculateTimes(inTime, subTime):
  try:
    return str(times[inTime] - times[subTime]).split('.', 2)[0]
  except KeyError:
    return 'None'


def displayTimes(times):
  times['finish'] = datetime.datetime.now()

  print(termcolours.PURPLE + 'Time to split to frames: ' + termcolours.LRED +
        calculateTimes('processFrames', 'startTime'))
  print(termcolours.PURPLE + 'Time to average frames: ' +
        termcolours.LRED + calculateTimes('averageColour', 'processFrames'))
  print(termcolours.PURPLE + 'Time to create colour timeline: ' +
        termcolours.LRED + calculateTimes('createBars', 'averageColour') + termcolours.NC)


def createColourBars(aveArray, folder, total=0, gradient_magnitude=0.9):
  print(termcolours.YELLOW + 'Creating Picture' + termcolours.NC)
  folder = folder + '/images'

  if not os.path.exists(folder):
    os.makedirs(folder)

  if total == 0:
    total = len(aveArray)

  # Keep same aspect ration for all generated images
  height = total / 2

  baseImage = Image.new('RGBA', [total, height])

  bars = ImageDraw.Draw(baseImage)
  for i, ave in enumerate(aveArray):
    bars.line((i, 0, i, height), fill=ave)

    # Progress counter
    sys.stdout.write("\rDone bar %d of %d" % (i, total))
    sys.stdout.flush()

  name = folder.split('/')[1].lower()
  baseImage.save(folder + '/rawBars_' + name + '.png', 'PNG')

  # Use nearest neighbour interpolation to resize the image
  resizeImage = baseImage.resize((2000, 1000), Image.NEAREST)
  resizeImage.save(folder + '/resizeBars_' + name + '.png', 'PNG')

  gradient_magnitude = 1 / gradient_magnitude

  width, height = resizeImage.size

  # Create gradient on image
  gradient = Image.new('L', (1, height), color=0xFF)

  for y in range(height):
    gradVal = max(255 - abs(y - height), 255 - y)
    gradient.putpixel((0, y), int(gradVal * (gradient_magnitude)))

  alpha = gradient.resize(resizeImage.size)
  blackImage = Image.new('RGBA', (width, height))  # Create a black image
  blackImage.putalpha(alpha)
  gradientImage = Image.alpha_composite(resizeImage, blackImage)
  gradientImage.save(folder + '/gradBars_' + name + '.png', 'PNG')

  # Create Borders
  # Side borders, bottom border
  border = [20, 100]
  borderImage = Image.new(
      'RGB', (width + (border[0] * 2), height + border[0] + border[1]), (250, 250, 250))
  borderImage.paste(gradientImage, (border[0], border[0], border[0] + width, border[0] + height))

  if title is None:
    titleText = name.title()
  else:
    titleText = title

  font = ImageFont.truetype("fonts/Roboto-Thin.ttf", 50)
  textImage = ImageDraw.Draw(borderImage)
  textSize = textImage.textsize(titleText, font)
  textImage.fontmode = '0'
  textImage.text(((borderImage.size[0] / 2) - (textSize[0] / 2), height +
                  border[0] + (border[1] / 2) - (textSize[1] / 2)), titleText, (0, 0, 0), font=font)
  borderImage.save(folder + '/borderedBars_' + name + '.png', 'PNG')

  # Extra spaces to overwrite previous output
  print(termcolours.GREEN + '\rDone Pictures                     ' + termcolours.NC)

  times['createBars'] = datetime.datetime.now()
  displayTimes(times)


def readFramesFolder(folder):
  print(termcolours.YELLOW + "Creating Average Array" + termcolours.NC)
  framesFolder = folder + '/frames'

  total = len([file for file in os.listdir(framesFolder) if not file.startswith('.')])

  aveArray = []
  for i, file in enumerate(os.listdir(framesFolder)):
    if not file.startswith("."):
      aveArray.append(averageFrameColour(framesFolder + '/' + file))
      sys.stdout.write("\rDone %d of %d" % (i, total))
      sys.stdout.flush()

  with open(folder + '/aveArray.json', 'w') as outfile:
    json.dump(aveArray, outfile)

  print(termcolours.GREEN + '\rDone Average Array' + termcolours.NC)

  times['averageColour'] = datetime.datetime.now()
  createColourBars(aveArray, folder, total)


def splitVideo(outFolder, filename, startNum):
  subprocess.check_call(
      './makeFrames.sh --outFolder {} --video {} --start {}'.format(outFolder, filename, startNum), shell=True)


def processVideoDir(filename):
  foldername = re.split('\\.|\\/', filename)[1].lower()
  outFolder = 'output/' + foldername
  startNum = 0

  if os.path.isdir(filename):
    for i, file in enumerate(os.listdir(filename)):
      if not file.startswith('.'):
        splitVideo(outFolder, filename + '/' + file, startNum)
        startNum = len([file for file in os.listdir(
            outFolder + '/frames') if not file.startswith('.')])

  else:
    splitVideo(outFolder, filename, startNum)

  times['processFrames'] = datetime.datetime.now()
  readFramesFolder(outFolder)


def checkTitle():
  if ('-t' in sys.argv):
    title = sys.argv[4]
  else:
    title = None

  return title


if __name__ == '__main__':
  times['startTime'] = datetime.datetime.now()
  if len(sys.argv) > 1 and ('-v' in sys.argv):
    title = checkTitle()
    processVideoDir(sys.argv[2])

  elif len(sys.argv) > 1 and ('-f' in sys.argv):
    title = checkTitle()
    folder = 'output/' + sys.argv[2]
    readFramesFolder(folder)

  elif len(sys.argv) > 1 and ('-a' in sys.argv):
    title = checkTitle()
    folder = 'output/' + sys.argv[2]
    with open(folder + '/aveArray.json') as data_file:
      data = json.load(data_file)

    aveArray = []
    for array in data:
      aveArray.append(tuple(array))

    print("Generated tuple array")

    createColourBars(aveArray, folder)

  else:
    print '\nusage: averageColour.py -v VIDEO for an unprocessed video file'
    print 'averageColour.py -f create picture from frames folder'
    print 'averageColour.py -a to provide a colour array'
    print 'prints the average colour of each frame of video in a picture.\n'
