from PIL import Image, ImageDraw
import numpy
import os
import sys
import subprocess
import json


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


def createColourBars(aveArray):
  print('Creating Picture')

  height = 2000
  out = Image.new('RGB', [len(aveArray), height], (255, 255, 255))

  bars = ImageDraw.Draw(out)
  for i, ave in enumerate(aveArray):
    bars.line((i, 0, i, height), fill=ave)

  out.save('output/bars.png', 'PNG')

  print('Done Picture')


def readFramesFolder(folder):
  print("Creating Average Array")

  total = 0
  for file in os.listdir(folder):
    if not file.startswith("."):
      total += 1

  aveArray = []
  for i, file in enumerate(os.listdir(folder)):
    if not file.startswith("."):
      aveArray.append(averageFrameColour(folder + '/' + file))
      sys.stdout.write("\rDone %d of %d" % (i, total))
      sys.stdout.flush()

  with open('output/aveArray.json', 'w') as outfile:
    json.dump(aveArray, outfile)

  print("\nDone Average Array")

  createColourBars(aveArray)


def splitVideo(filename):
  outFolder = 'output/frames'
  subprocess.check_call(
      './makeFrames.sh --outFolder {} --video {}'.format(outFolder, filename), shell=True)

  readFramesFolder(outFolder)


if __name__ == '__main__':
  if len(sys.argv) > 1 and ('-v' in sys.argv):
    splitVideo(sys.argv[2])

  elif len(sys.argv) > 1 and ('-f' in sys.argv):
    readFramesFolder('output/frames')

  elif len(sys.argv) > 1 and ('-a' in sys.argv):
    with open('output/aveArray.json') as data_file:
      data = json.load(data_file)

    aveArray = []
    for array in data:
      aveArray.append(tuple(array))

    createColourBars(aveArray)

  else:
    print 'usage: averageColour.py -v VIDEO for an unprocessed video file'
    print 'averageColour.py -f create picture from frames folder'
    print 'averageColour.py -a to provide a colour array'
    print 'prints the average colour of each frame of video in a picture.'
