from PIL import Image, ImageDraw
import numpy
import os
import sys
import subprocess
import json
import re


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


def createColourBars(aveArray, folder, total=0):
  print('Creating Picture')

  if total == 0:
    total = len(aveArray)

  # Keep same aspect ration for all generated images
  height = total / 2

  out = Image.new('RGB', [total, height])

  bars = ImageDraw.Draw(out)
  for i, ave in enumerate(aveArray):
    bars.line((i, 0, i, height), fill=ave)

    sys.stdout.write("\rDone bar %d of %d" % (i, total))
    sys.stdout.flush()

  name = folder.split('/')[1].lower()
  out.save(folder + '/bars_' + name + '.png', 'PNG')

  print('\nDone Picture')


def readFramesFolder(folder):
  print("Creating Average Array")
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

  print("\nDone Average Array")

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

  readFramesFolder(outFolder)


if __name__ == '__main__':
  if len(sys.argv) > 1 and ('-v' in sys.argv):
    processVideoDir(sys.argv[2])

  elif len(sys.argv) > 1 and ('-f' in sys.argv):
    readFramesFolder('output/frames')

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
    print 'usage: averageColour.py -v VIDEO for an unprocessed video file'
    print 'averageColour.py -f create picture from frames folder'
    print 'averageColour.py -a to provide a colour array'
    print 'prints the average colour of each frame of video in a picture.'
