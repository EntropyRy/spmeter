#!/bin/sh
mkdir -p logs/
while true
do
# "remix 1" takes audio only from the left channel.
# Measurement microphone is connected there. Right channel is just noise.
sox -q \
 -t alsa -r 48000 -e signed -b 24 -c 2 hw:CARD=UA22,DEV=0 \
 -t raw -e float -b 32 -c 1 - \
 remix 1 \
| ./measurement.py
sleep 1
done
