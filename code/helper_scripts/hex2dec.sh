#!/bin/bash

# Read from specified file, or from standard input
infile="${1:-/dev/stdin}"
while read line; do
    for number in $line; do
        printf "%f " "$number" >> ${infile}_temp 
    done
    printf '\n' >> ${infile}_temp 
done < $infile
mv $infile ${infile}_bak
mv ${infile}_temp $infile