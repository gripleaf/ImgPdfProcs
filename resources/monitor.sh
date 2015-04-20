#!/bin/sh

procs=$(ps -e -o 'pid,rsz,comm' | grep 'convert')
pids=$(echo $procs | cut -d ' ' -f 1,2)
IFS='\n'
for pid in $pids
do
    mem=$(echo $pid | cut -d ' ' -f2);
    pd=$(echo $pid | cut -d ' ' -f1);
    if test mem -ge 1094888
    then
        kill -9 $pd;
    fi
done

