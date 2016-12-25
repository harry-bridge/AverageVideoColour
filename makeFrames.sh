#!/bin/bash

echo "Splitting Frames"

while [[ "$#" > 1 ]]; do case $1 in
    --outFolder) outFolder="$2";;
    --video) video="$2";;
    *) break;;
  esac; shift; shift
done

if [ ! -d 'output' ] ; then
  mkdir output
fi

if [ ! -d $outFolder ] ; then
  mkdir $outFolder
  mkdir $outFolder/frames
fi

ffmpeg -i $video -r 0.4 $outFolder/frames/image-%06d.jpeg &> /dev/null

echo "Done Frame Splitting"
