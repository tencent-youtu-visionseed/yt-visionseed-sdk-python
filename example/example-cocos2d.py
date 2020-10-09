# -*- coding:utf-8 -*-
# author: chenliang @ Youtu Lab, Tencent
from visionseed import YtVisionSeed, YtDataLink
import serial

import cocos
from cocos import director
from pyglet import clock

import cv2
import numpy as np
import math

import pyglet
from pyglet.gl import *

import matplotlib

vs = YtVisionSeed( serial.Serial("/dev/ttyACM0",115200,timeout=0.5) )
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_CONVERT_RGB, False)

if (cap.isOpened() == False):
    print("Unable to read camera feed")
    exit(0)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
window_width = frame_width
window_height = frame_height

class VisionSeedLayer(cocos.layer.Layer): #实现一个layer类（图层）
    def __init__(self):
        super(VisionSeedLayer, self).__init__()
        self.skipSync = 0
        self.frame = None
        self.msg = None
        self.sprite = None

        vs.setDebugDrawing(1)

    def drawImage(self, frame, drawRects):
        if (len(drawRects) == 0):
            return
        rect = drawRects[0]
        if rect.y < 0 or rect.x < 0:
            return
        frame = frame[rect.y:rect.y+rect.h, rect.x:rect.x+rect.w]
        c0,c1,c2 = cv2.split(frame)
        alpha = np.zeros((frame.shape[0], frame.shape[1],1), np.uint8)
        steps = 20
        for i in range(1,1+steps):
            cv2.circle(alpha,(frame.shape[0]>>1, frame.shape[1]>>1), int(frame.shape[0]/2 * (1 - i/steps*0.2)), int(i/steps*255), cv2.FILLED)

        frame = cv2.merge((c0,c1,c2,alpha))
        rows,cols,channels = frame.shape
        number_of_bytes = rows*cols*channels
        raw_img = bytes((frame.ravel()).astype('byte'))
        top_to_bottom_flag = -1
        bytes_per_row = channels*cols
        pyimg = pyglet.image.ImageData(width=cols,
                                       height=rows,
                                       format='BGRA',
                                       data=raw_img,
                                       pitch=top_to_bottom_flag*bytes_per_row)
        if self.sprite:
            self.remove(self.sprite)
        self.sprite = cocos.sprite.Sprite(pyimg)
        self.sprite.position = ((rect.x+rect.w/2), window_height - (rect.y+rect.h/2))
        # self.sprite.position = (window_width/2, window_height/2)
        self.add(self.sprite)

        # cv2.imshow('frame', frame)
        # cv2.waitKey(1)

    def I420ToBgr(self, frame):
        p = 0
        len = frame_height
        Y = frame[p:p+len]

        p += len
        len = frame_height>>2
        U = []
        for i in range(p, p+len):
            U.append( frame[i][:frame_width>>1] )
            U.append( frame[i][frame_width>>1:frame_width] )
        U = np.array(U)
        U = cv2.resize(U, (frame_width, frame_height))


        p += len
        V = []
        for i in range(p, p+len):
            V.append( frame[i][:frame_width>>1] )
            V.append( frame[i][frame_width>>1:frame_width] )
        V = np.array(V)
        V = cv2.resize(V, (frame_width, frame_height))

        YUV = cv2.merge([Y, U, V])
        dst = cv2.cvtColor(YUV, cv2.COLOR_YUV2BGR)
        return dst

    def recvMsg(self):
        while True:
            result, msg = vs.recvRunOnce()
            if msg:
                # print(msg)
                if msg.result.HasField('frameId'):
                    self.msg = {'msg':msg, 'result':result, 'frameId':msg.result.frameId}
                    break
                elif msg.result.HasField('systemStatusResult'):
                    #print(msg)
                    pass
    def recvFrame(self):
        ret, frame = cap.read()
        if ret == True:
            # On Windows, cv2 give us a 1-D array
            if frame.shape[0] == 1:
                frame = np.reshape(frame, (-1, frame_width))
            seq = 0
            seq |= frame[0][0]
            seq <<= 8
            seq |= frame[0][frame_width-1]
            seq <<= 8
            seq |= frame[frame_height-1][0]
            seq <<= 8
            seq |= frame[frame_height-1][frame_width-1]
            # print('seq =', seq)

            bgr = self.I420ToBgr(frame)
            self.frame = {'frame':bgr, 'frameId':seq}

    def callback(self, dt):
        #print('%f seconds since last callback' % dt)

        # 根据frameId同步
        while self.msg == None:
            self.recvMsg()
        while self.frame == None:
            self.recvFrame()
        if abs(self.frame['frameId'] - self.msg['frameId']) > 3600:
            self.skipSync += 1
            if (self.skipSync >= 10):
                print('Your VisionSeed may running old firmware! %d != %d' % (self.frame['frameId'], self.msg['frameId']))
            self.msg = None
            self.frame = None
            return

        while self.frame['frameId'] > self.msg['frameId']:
            # print('seq =', self.frame['frameId'], self.msg['frameId'])
            self.recvMsg()
        while self.frame['frameId'] < self.msg['frameId']:
            # print('seq =', self.frame['frameId'], self.msg['frameId'])
            self.recvFrame()
        if self.frame['frameId'] != self.msg['frameId']:
            print('miss =', self.frame['frameId'], self.msg['frameId'])
            return

        self.on_frame(self.frame['frame'], self.msg['result'])

        self.msg = None
        self.frame = None

    def on_enter( self ):
        super(VisionSeedLayer,self).on_enter()
        clock.schedule(self.callback)

    def on_exit( self ):
        super(VisionSeedLayer,self).on_exit()
        clock.unschedule(self.callback)

    def on_frame(self, frame, result):
        pass


class GameBegin(VisionSeedLayer): #实现一个layer类（图层）
    def __init__(self):
        super(GameBegin, self).__init__()

        self.label = cocos.text.Label('O',font_name = 'Time New Noman',font_size = 32,anchor_x = "center",anchor_y = "center")
        self.label.position = (window_width/2, window_height/2)
        # self.add(self.label, z=100)

        self.mouth = []
        for i in range(2):
            mouth = cocos.sprite.Sprite('mouth%d.png' % i)
            mouth.position = (window_width/2, window_height/2)
            self.add(mouth, z=200)
            mouth.opacity = 0
            self.mouth.append(mouth)

    def on_enter( self ):
        super(GameBegin,self).on_enter()
        self.cnt = 0

    def on_frame(self, frame, result):
        #清除上一帧的avatar
        if self.sprite:
            self.remove(self.sprite)
            self.sprite = None

        # print(''.join('{:02x} '.format(x) for x in buf))

        drawRects = []

        YtVisionSeedModel = YtDataLink.YtVisionSeedModel
        count = result.getResult([YtVisionSeedModel.FACE_DETECTION])
        # 打印信息
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

        # 绘制
        for i in range(count):
            # 获取检测框
            rect = result.getResult([YtVisionSeedModel.FACE_DETECTION, i])
            if (rect):
                drawRects.append(rect)
                # cv2.rectangle(frame, (rect.x, rect.y), (rect.x+rect.w, rect.y+rect.h), (255), 5)

            # 嘴巴贴图
            if i == 0:
                # 获取90点关键点
                shape = result.getResult([YtVisionSeedModel.FACE_DETECTION, i, YtVisionSeedModel.FACE_LANDMARK])
                if (shape):
                    shape = shape.faceShape
                    # 计算嘴巴姿态
                    dia = (shape.mouth[0] - shape.mouth[6])
                    dia_y = ((shape.mouth[3] - shape.mouth[9]) + (shape.mouth[14] - shape.mouth[19])) / 2
                    scale = max(0.25, dia_y.length()/dia.length()) * 4 + 0.1
                    # print(dia_y.length()/dia.length())
                    # 计算嘴巴中点
                    p = (shape.mouth[0] + shape.mouth[6] + shape.mouth[14] + shape.mouth[19])/4
                    for i, mouth in enumerate(self.mouth):
                        mouth.position = ((rect.x + p.x)/frame_width*window_width, (1-(rect.y + p.y)/frame_height)*window_height)
                        mouth.rotation = math.atan2(-dia.y, -dia.x) * 180 / math.pi
                        mouth.scale_x = dia.length() / 512 * scale
                        if i==0:
                            mouth.scale_y = mouth.scale_x
                        else:
                            mouth.scale_y = (dia_y.length() + 10) / 512 * scale
                    if (scale <= 1.2):
                        self.mouth[0].opacity = 250
                        self.mouth[1].opacity = 0
                    else:
                        self.mouth[0].opacity = 0
                        self.mouth[1].opacity = 250
                else:
                    self.mouth[0].opacity = 0
                    self.mouth[1].opacity = 0

        self.drawImage(frame, drawRects)


if __name__ == '__main__':
    director.director.init(width=window_width, height=window_height) #初始化导演类，一个应用程序只有一个导演类（全局）
    # director.director.set_show_FPS(True)
    hello_layer = GameBegin() #实例化一个图层
    main_scene = cocos.scene.Scene(hello_layer) #初始化一个场景，并将图层加入到场景中
    cocos.director.director.run(main_scene) #用导演类来运行第一个场景
