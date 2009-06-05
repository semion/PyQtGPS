#!/usr/bin/python
# -*- coding: UTF-8 -*-

import bluetooth

# bluetooth address of the GPS device.
addr = "00:0A:3A:27:14:3C" #"00:0D:B5:31:58:58"

# port to use.
port = 1

# create a socket and connect to it.
socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
socket.connect((addr, port))

olddata = ""
data = ""

while True:
  data = socket.recv(1024)
  
 # make sure we actually have some data.
  if len(data) > 0:
  
    # append the old data to the front of data.
    data = olddata + data

    # split the data into a list of lines, but make
    # sure we preserve the end of line information.
    lines = data.splitlines(1)

    # iterate over each line
    for line in lines:
    
      # if the line has a carriage return and a
      # linefeed, we know we have a complete line so
      # we can remove those characters and print it.
      if line.find("\r\n") != -1 :
        line = line.strip()
        print line

        # empty the olddata variable now we have
        # used the data.
        olddata = ""

      # else we need to keep the line to add to data
      else :
        olddata = line