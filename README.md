#Average Video Colour

Takes each frame of a given video and compresses its average color into a single vertical line, creating a timeline of the spectrum of colors used throughout each video

##Installation

Installation is very simple. First install the pip requirements with:

`pip install -r requirements.txt`

It may be helpful to create a virtual env for this to live in, instructions on doing that can be found on the [virtualenv site](https://virtualenv.pypa.io/en/stable/installation/).

You will also need the *'ffmpg'* library which for mac users can be installed with HomeBrew:

`brew install ffmpg`

##Usage

To generate a colour timeline place a video in the **'video'** folder and run:

`python averageColour.py -v *video*`

This will run through the video and place each frame of the video in **'output/frames'**, it will also create a json file containing the average colour of each frame.

If you already have a set of frames, or a set of images you want to get the colour timeline of then you can place your frames or images in the **'output/frames'** folder and run:

`python averageColour.py -f`

You can also remake the image from the json file of frame averages by running:

`python averageColour.py -a`

This is useful if, for example, you want to change the height of the output image and therefore means you don't have to compute the frame averages again, which can take a while for a long video.
