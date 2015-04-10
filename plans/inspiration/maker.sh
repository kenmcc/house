#!/bin/bash

rm -rf *.aux *.log *.out
rm -rf *.toc *.tex *.pdf
rm email.txt

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

python pdfmaker.py
rm -rf *.aux *.log *.out
rm -rf *.toc *.tex



echo "UNTRACKED: ADD"
for l in $untracked ; do
    echo "ADDED $l \n" >> email.txt
    git add "../../$l"
    git commit -m "added file $l" ../../$l
done

echo "MODIFIED, COMMIT"
for l in $modified ; do
    echo "MODIFIED $l \n" >> email.txt
    git commit -m "Auto commit of file $l" ../../$l
done

echo "DELETED, REMOVE"
for l in $deleted ; do
    echo "REMOVED $l \n" >> email.txt
    git commit -m "DELETE FILE $l", ../../$l
done

# and now we push the changes to the system
git push

EMAILMSG=`cat email.txt`
echo $EMAILMSG

