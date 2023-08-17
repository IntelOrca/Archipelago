#!/bin/bash
set -e
rm -rf output
python3.11 ./Generate.py
cd output
unzip *.zip
cat *_Spoiler.txt
