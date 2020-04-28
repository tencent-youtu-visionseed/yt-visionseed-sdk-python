# -*- coding:utf-8 -*-
# author: chenliang @ Youtu Lab, Tencent
import visionseed as vs
import serial
import time


datalink = vs.YtDataLink( serial.Serial("/dev/ttyACM0",115200,timeout=0.5) )

def main():
    while True:
        result, msg = datalink.recvRunOnce()

        if result:
            YtVisionSeedModel = vs.YtDataLink.YtVisionSeedModel
            count = result.getResult([YtVisionSeedModel.FACE_DETECTION])
            for i in range(count):
                line = ''
                # 获取检测框
                rect = result.getResult([YtVisionSeedModel.FACE_DETECTION, i])
                if (rect):
                    line += 'rect: (%d, %d, %d, %d) ' % (rect.x, rect.y, rect.w, rect.h)

                # 获取人脸识别结果
                faceName = result.getResult([YtVisionSeedModel.FACE_DETECTION, i, YtVisionSeedModel.FACE_RECOGNITION])
                if (faceName):
                    line += 'name: %s (confidence: %.3f) ' % (faceName.str, faceName.conf)

                # 获取轨迹ID
                traceId = result.getResult([YtVisionSeedModel.FACE_DETECTION, i, YtVisionSeedModel.DETECTION_TRACE])
                if not (traceId is None):
                    line += 'traceId: %d ' % traceId

                # 获取人脸姿态
                pose = result.getResult([YtVisionSeedModel.FACE_DETECTION, i, YtVisionSeedModel.FACE_POSE])
                if not (pose is None):
                    line += 'pose(roll,yaw,pitch): (%5.1f, %5.1f, %5.1f) ' % (pose.array[0], pose.array[1], pose.array[2])

                # 获取90点关键点
                shape = result.getResult([YtVisionSeedModel.FACE_DETECTION, i, YtVisionSeedModel.FACE_LANDMARK])
                if (shape):
                    faceShape = shape.faceShape
                    l1 = (faceShape.mouth[0] - faceShape.mouth[6]).length()
                    l2 = (faceShape.mouth[3] - faceShape.mouth[9]).length()
                    ratio = (l2 / (l1 + 0.01))
                    line += 'mouth: ' + ('open' if ratio > 1 else 'close')
                print(line)

if __name__ == '__main__':
    main()
