#!/bin/bash

s=$(head -n 1 log.txt)
while [[ $s != "finish" ]]
do
  windscribe disconnect
  windscribe connect
  python3 crawler.py "$s"
  s=$(head -n 1 log.txt)
done
