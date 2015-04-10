#!/bin/bash

rm -rf *.aux *.log *.out
rm -rf *.toc *.tex 
rm email.txt

pullResult=`git pull`
statResult=`git status --porcelain | grep -v "maker"`

if [ "$statResult" = "" ]; then
  if [ "$pullResult" = "Already up-to-date." ]; then
      echo "Nothing to do"
      exit 1
  fi
fi

echo "Doing stuff"
# we should check in the untracked files
echo "PULL" $pullResult
echo "STAT" $statResult
#exit 1

untracked=`git status --porcelain | grep "^??"  | sed -e 's/^?? //'`
modified=`git status --porcelain | grep "^ M" | grep -v $0 | sed -e 's/^ M//'`
deleted=`git status --porcelain | grep "^D " | sed -e 's/^D //'`

python pdfmaker.py
rm -rf *.aux *.log *.out
rm -rf *.toc *.tex

untracked=`git status --porcelain | grep "^??"  | sed -e 's/^?? //'`
modified=`git status --porcelain | grep "^ M" | grep -v $0 | sed -e 's/^ M//'`
deleted=`git status --porcelain | grep "^D " | sed -e 's/^D //'`

echo "New document generated with the following moderations \n" > email.txt

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
git push > /dev/null

cat email.txt | mutt -s "BuildInspirations" ken.mccullagh@s3group.com -a inspirations.pdf
rm email.txt


 

