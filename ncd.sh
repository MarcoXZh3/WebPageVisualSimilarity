#!/bin/bash

# https://github.com/DavyLandman/ncd
#./ncds.py TestCases/ImgSet01/*.tif > TestCases/ncd-results01.txt

max=10
output=TestCases/ncd-results.txt;

for ((i = 1; i <= $max; i++)); do
    path=$(printf "TestCases/ImgSet%02d/*.tif" "$i")
    output=$(printf "TestCases/ncd-results%02d.txt" "$i")
    echo Subset -- $i
    ./ncds.py $path > $output
    echo
done
