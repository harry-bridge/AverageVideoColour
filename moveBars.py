import os
import sys
import shutil


class termcolours:
  GREEN = '\033[0;32m'
  NC = '\033[0m'  # No Colour


def moveBars(outDir=None, prefix=None):
  inDir = 'output/'
  imagesDir = 'images/'

  if prefix is None:
    prefix = 'gradBars_'

  if outDir is None:
    outDir = 'bars'

  if not os.path.exists(outDir):
    os.makedirs(outDir)

  # Loop output folder
  for folder in os.listdir(inDir):
    if not folder.startswith('.'):

      imagesFolder = inDir + folder + '/' + imagesDir
      for file in os.listdir(imagesFolder):
        if not file.startswith('.'):
          if file.startswith(prefix):
            shutil.copy(imagesFolder + file, outDir)

  print(termcolours.GREEN + '\rDone' + termcolours.NC)


if __name__ == '__main__':
  if len(sys.argv) > 1:
    if '-o' and not '-p' in sys.argv:
      moveBars(sys.argv[2])
    elif '-p' and not '-o' in sys.argv:
      moveBars(None, sys.argv[2])
    elif '-o' and '-p' in sys.argv:
      moveBars(sys.argv[2], sys.argv[4])

  elif ('-h' in sys.argv):
    print '\nusage: moveBars.py default is *gradBars_ and outputs to bars'
    print '-o to specify an output directory'
    print '-p to specify an image prefix other than gradBars_\n'

  else:
    moveBars()
