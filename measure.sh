#!/bin/sh
mkdir -p logs/
while true
do
sox -q -t alsa plughw:CARD=UA22,DEV=0 -r 48000 -b 32 -c 1 -t raw -e float -b 32 - | ./measurement.py
sleep 1
done
