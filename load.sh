#!/bin/bash

s=$(head -n 1 log2.txt)
while [[ $s != 10000 ]]
do
  python3 loader.py "$s"
  windscribe disconnect > /dev/null
  windscribe connect > /dev/null
  s=$(head -n 1 log2.txt)
done
