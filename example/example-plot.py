# -*- coding:utf-8 -*-
# author: chenliang @ Youtu Lab, Tencent
from visionseed import YtVisionSeed, YtDataLink
import serial
import matplotlib
import matplotlib.pyplot as plt


vs = YtVisionSeed( serial.Serial("/dev/ttyACM0",115200,timeout=0.5) )

class Chart:
    def __init__(self, maxlen=100, title='', xlabel='frame', ylabel=''):
        self.maxlen = maxlen
        self.x = []
        self.data = []
        self.labels = []

        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
        self.ax.grid()
        self.line, = self.ax.plot([], [], 'r-') # Returns a tuple of line objects, thus the comma

    def onData(self, value, label=''):
        # Data for plotting
        if (self.maxlen > 0 and len(self.data) > self.maxlen):
            self.data.pop(0)
            self.labels.pop(0)
        else:
            self.x.append(len(self.data))

        self.data.append(value)
        self.labels.append(label)
        # print(self.data)

        self.ax.set_xticklabels(self.labels)
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.data)
        self.ax.relim()        # Recalculate limits
        self.ax.autoscale_view(True,True,True) #Autoscale

        self.fig.canvas.draw()

    def idle(self):
        self.fig.canvas.flush_events()

def main():
    chart = Chart(100, 'mouth', 'frame', 'openess')
    while True:
        result, msg = vs.recvRunOnce()

        if result:
            YtVisionSeedModel = YtDataLink.YtVisionSeedModel
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

                # 获取90点关键点
                shape = result.getResult([YtVisionSeedModel.FACE_DETECTION, i, YtVisionSeedModel.FACE_LANDMARK])
                if (shape):
                    faceShape = shape.faceShape
                    l1 = (faceShape.mouth[0] - faceShape.mouth[6]).length()
                    l2 = (faceShape.mouth[3] - faceShape.mouth[9]).length()
                    ratio = (l2 / (l1 + 0.01))
                    line += 'mouth: ' + ('open' if ratio > 1 else 'close')
                    chart.onData(ratio)

                print(line)

        chart.idle()

if __name__ == '__main__':
    main()
