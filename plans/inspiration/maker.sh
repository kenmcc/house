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
# we should check in the untracked files

untracked=`git status --porcelain | grep "^??" | sed -e 's/^?? //'`
modified=`git status --porcelain | grep "^ M" | sed -e 's/^ M//'`
deleted=`git status --porcelain | grep "^D " | sed -e 's/^D //'`
echo "UNTRACKED: ADD"
for l in $untracked ; do
    echo $l
    git add "../../$l"
    git commit -m "added file $l" ../../$l
done

echo "MODIFIED, COMMIT"
for l in $modified ; do
    git commit -m "Auto commit of file $l" ../../$l
done

echo "DELETED, REMOVE"
for l in $deleted ; do
    git commit -m "DELETE FILE $l", ../../$l
done

