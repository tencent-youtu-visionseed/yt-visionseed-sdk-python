import visionseed as vs
import serial
import matplotlib
import matplotlib.pyplot as plt


datalink = vs.YtDataLink( serial.Serial("/dev/ttyACM0",115200,timeout=0.5) )

def recvMsg():
    while True:
        msg = datalink.recvRunOnce()
        if msg:
            # print(msg)
            if msg.result.HasField('faceDetectionResult'):
                return msg

x = []
data = []
plt.ion()
fig, ax = plt.subplots()
ax.set(xlabel='frame', ylabel='degree',
       title='Pose')
ax.grid()
line, = ax.plot([], [], 'r-') # Returns a tuple of line objects, thus the comma

while True:
    msg = recvMsg()
    if (len(msg.result.faceDetectionResult.face) > 0):
        face = msg.result.faceDetectionResult.face[0]
        if (face.HasField('pose')):
            # Data for plotting
            if (len(data) > 100):
                data.pop(0)
            else:
                x.append(len(data))
            data.append(face.pose.yaw)
            # print(data)

            line.set_xdata(x)
            line.set_ydata(data)
            ax.relim()        # Recalculate limits
            ax.autoscale_view(True,True,True) #Autoscale

            fig.canvas.draw()

    fig.canvas.flush_events()
