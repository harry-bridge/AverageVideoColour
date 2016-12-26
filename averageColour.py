from PIL import Image, ImageDraw
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
  return str(times[inTime] - times[subTime]).split('.', 2)[0]


def displayTimes(times):
  times['finish'] = datetime.datetime.now()

  print(termcolours.PURPLE + 'Time to split to frames: ' + termcolours.LRED +
        calculateTimes('processFrames', 'startTime'))
  print(termcolours.PURPLE + 'Time to average frames: ' +
        termcolours.LRED + calculateTimes('averageColour', 'processFrames'))
  print(termcolours.PURPLE + 'Time to create colour timeline: ' +
        termcolours.LRED + calculateTimes('createBars', 'averageColour') + termcolours.NC)


def createColourBars(aveArray, folder, total=0):
  print(termcolours.YELLOW + 'Creating Picture' + termcolours.NC)
  folder = folder + '/images'

  if total == 0:
    total = len(aveArray)

  # Keep same aspect ration for all generated images
  height = total / 2

  baseImage = Image.new('RGBA', [total, height])

  bars = ImageDraw.Draw(baseImage)
  for i, ave in enumerate(aveArray):
    bars.line((i, 0, i, height), fill=ave)

    sys.stdout.write("\rDone bar %d of %d" % (i, total))
    sys.stdout.flush()

  name = folder.split('/')[1].lower()
  baseImage.save(folder + '/rawBars_' + name + '.png', 'PNG')

  # Use nearest neighbour interpolation to resize the image
  resizeImage = baseImage.resize((2000, 1000), Image.NEAREST)
  resizeImage.save(folder + '/resizeBars_' + name + '.png', 'PNG')

  # Extra spaces to overwrite previous output
  print(termcolours.GREEN + '\rDone Picture                     ' + termcolours.NC)

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
  foldername = re.split('\\.|\\/', filename)[1].title()
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


if __name__ == '__main__':
  times['startTime'] = datetime.datetime.now()
  if len(sys.argv) > 1 and ('-v' in sys.argv):
    processVideoDir(sys.argv[2])

  elif len(sys.argv) > 1 and ('-f' in sys.argv):
    folder = 'output/' + sys.argv[2]
    readFramesFolder(folder)

  elif len(sys.argv) > 1 and ('-a' in sys.argv):
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
