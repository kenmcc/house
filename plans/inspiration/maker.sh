#!/bin/bash

rm -rf *.aux
rm -rf *.toc
rm -rf *.tex
rm -rf *.toc


pullResult=`git pull`
statResult=`git status --porcelain`

if [ "$statResult" = "" ]; then
  if [ "$pullResult" = "Already up-to-date." ]; then
      echo "Nothing to do"
      exit 1
  fi
fi

echo "Doing stuff"



