#!/bin/sh

mkdir -p small/

for file in *.png *.jpg; do
    convert -resize 128x90 $file small/$file
done
