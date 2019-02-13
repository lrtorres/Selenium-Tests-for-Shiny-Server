#!/bin/sh
#
# Kill any lingering X virtual framebuffer processes stemming from the headless Google Chrome session.
#

for i in $(pgrep -f Xvfb); do echo ${i}; kill -9 ${i}; done
for i in $(pgrep -f /opt/google/chrome/chrome); do echo ${i}; kill -9 ${i}; done
for i in $(pgrep -f chromedriver); do echo ${i}; kill -9 ${i}; done
