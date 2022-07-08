#!/bin/bash
basepath=`pwd`
echo 'Basepath is' $basepath
declare -a SUBJECTS=("eddy" "danny")

cd $basepath/derivatives/resampled-isotropic-1mm
for sub in ${SUBJECTS[@]}; do
    echo ${sub}
    cd ./sub-${sub}
    for f in ./ses*; do
        echo ${f}
        if [ -d "$f/fmap" ]; then
            cd $f/fmap
            rename -v 's/__/_/g' *
            cd ../..
        fi
        if [ -d "$f/func" ]; then
            cd $f/fmap
            rename -v 's/__/_/g' *
            cd ../..
        fi
    done
done

cd $basepath/sourcedata
for sub in ${SUBJECTS[@]}; do
    echo ${sub}
    cd ./sub-${sub}
    for f in ./ses*; do
        echo ${f}
        if [ -d "$f/fmap" ]; then
            cd $f/fmap
            rename -v 's/__/_/g' *
            cd ../..
        fi
        if [ -d "$f/func" ]; then
            cd $f/fmap
            rename -v 's/__/_/g' *
            cd ../..
        fi
    done
done

for sub in ${SUBJECTS[@]}; do
    echo ${sub}
    cd $basepath/sub-${sub}
    for f in ./ses*; do
        echo ${f}
        if [ -d "$f/fmap" ]; then
            cd $f/fmap
            rename -v 's/__/_/g' *
            cd ../..
        fi
        if [ -d "$f/func" ]; then
            cd $f/fmap
            rename -v 's/__/_/g' *
            cd ../..
        fi
    done
done

cd $basepath