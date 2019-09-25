#!/usr/bin/env bash

echo jupyter lab --no-browser --ip 10.60.1.141 --port 8888
nohup jupyter lab --no-browser --ip 10.60.1.141 --port 8888 >log-jupyter-lab.txt 2>&1 &