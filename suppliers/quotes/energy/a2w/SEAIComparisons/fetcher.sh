for x in `seq 1 38` ; do wget "http://www.seai.ie/Your_Building/BER/BER_Assessors/Technical/HARP_Database/Heat_Pumps/?f=1&type=Air+to+water&p=$x" -O $x.html; done

for x in `seq 1 38` ; do cat $x.html | sed -n '/harptable2.*/,/\<\/table/p' >>data.txt; done

