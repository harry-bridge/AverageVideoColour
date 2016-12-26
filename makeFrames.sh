#!/bin/bash

YELLOW='\033[93m'
GREEN='\033[0;32m'
NC='\033[0m' # No Colour


while [[ "$#" > 1 ]]; do case $1 in
    --outFolder) outFolder="$2";;
    --video) video="$2";;
    --start) start="$2";;
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

echo -e "${YELLOW}Splitting Frames (from" $start")"

ffmpeg -i $video -r 0.4 -start_number $start $outFolder/frames/image-%06d.jpeg -loglevel quiet

echo -e "${GREEN}Done Frame Splitting ${NC}"
