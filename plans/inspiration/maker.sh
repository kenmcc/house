#!/bin/bash

rm -rf *.aux
rm -rf *.toc
rm -rf *.tex
rm -rf *.toc


pullResult=`git pull`
statResult=`git status --porcelain`

if [ "$statResult" != "" ];
  then echo "UNTRACKED FILES!!"
fi
