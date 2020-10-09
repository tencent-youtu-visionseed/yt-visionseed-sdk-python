# -*- coding:utf-8 -*-
# author: chenliang @ Youtu Lab, Tencent
from visionseed import YtVisionSeed, YtDataLink
import serial
import time


vs = YtVisionSeed( serial.Serial("/dev/ttyACM0",115200,timeout=0.5) )

def main():
    print('[device]', vs.getDeviceInfo())
    print('[faceList]', vs.listFaceId())

if __name__ == '__main__':
    main()
