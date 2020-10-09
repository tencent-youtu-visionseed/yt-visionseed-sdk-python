# /**
#  * SDK interface of the VisionSeed
#  * author: chenliang @ Youtu Lab, Tencent
#  */
from .YtMsg_pb2 import *
from . import YtFaceAlignment
from .YtDataLink import YtDataLink
from .CameraExposureParams_pb2 import *
from .FlasherParams_pb2 import *
from .FaceDetectionResult_pb2 import *
from .SystemStatusResult_pb2 import *
from .FileListResult_pb2 import *
from .FilePart_pb2 import *
from .RegisterFaceIdWithPicParams_pb2 import *
import numpy as np
import struct

class YtVisionSeed:
    def __init__(self, port):
        self.datalink = YtDataLink( port )

    def recvRunOnce (self):
        return self.datalink.recvRunOnce()

    # Camera
    def setCamAutoExposure (self, camId):
        rpc = YtRpc()
        rpc.func = (rpc.setExposure)
        cameraExposureParams = CameraExposureParams()
        cameraExposureParams.type = (1)
        cameraExposureParams.camId = (camId)
        rpc.cameraExposureParams.CopyFrom(cameraExposureParams)
        self.datalink.sendRpcMsg(rpc)

    def setCamManualExposure (self, camId, timeUs, gain):
        rpc = YtRpc()
        rpc.func = (rpc.setExposure)
        cameraExposureParams = CameraExposureParams()
        cameraExposureParams.type = (0)
        cameraExposureParams.timeUs = (timeUs)
        cameraExposureParams.gain = (gain)
        cameraExposureParams.camId = (camId)
        rpc.cameraExposureParams.CopyFrom(cameraExposureParams)
        self.datalink.sendRpcMsg(rpc)

    def setFlasher (self, flasherIR):
        rpc = YtRpc()
        rpc.func = (rpc.setFlasher)
        flashParams = FlasherParams()
        flashParams.ir = (flasherIR)
        rpc.flasherParams.CopyFrom(flashParams)
        self.datalink.sendRpcMsg(rpc)

    def setMainCamId (self, value):
        rpc = YtRpc()
        rpc.func = (rpc.setMainCamera)
        rpc.intParams = (value)
        self.datalink.sendRpcMsg(rpc)

    def setRotation (self, value):
        rpc = YtRpc()
        rpc.func = (rpc.setCameraRotation)
        rpc.intParams = (value)
        self.datalink.sendRpcMsg(rpc)

    def setDebugDrawing (self, value):
        rpc = YtRpc()
        rpc.func = (rpc.setDebugDrawing)
        rpc.intParams = (value)
        self.datalink.sendRpcMsg(rpc)


    # Files
    def listFile (self, path):
        rpc = YtRpc()
        rpc.func = (rpc.listFile)
        rpc.strParams = (path)
        result = self.datalink.sendRpcMsg(rpc)
        if (result.response):
            return result.response.fileListResult.files

        return None

    def deleteFile (self, path, auth = ''):
        rpc = YtRpc()
        rpc.func = (rpc.deleteFile)
        rpc.strParams = (path)
        rpc.auth = (auth)
        self.datalink.sendRpcMsg(rpc)


    def getConfig (self, domain):
        rpc = YtRpc()
        rpc.func = (rpc.getConfig)
        rpc.strParams = (domain)
        result = self.datalink.sendRpcMsg(rpc)
        if (result.response):
            return str(result.response.filePart.data, encoding = "utf-8")

        return None


    def setConfig (self, domain, content):
        data = bytes(content, encoding = "utf8")
        rpc = YtRpc()
        rpc.func = (rpc.setConfig)
        params = FilePart()
        params.path = (domain)
        params.totalLength = len(content)
        params.offset = (0)
        params.data = (data)
        rpc.filePart.CopyFrom(params)
        self.datalink.sendRpcMsg(rpc)


    def resetConfig (self, domain):
        rpc = YtRpc()
        rpc.func = (rpc.resetConfig)
        rpc.strParams = (domain)
        self.datalink.sendRpcMsg(rpc)


    # Info
    def getDeviceInfo (self):
        rpc = YtRpc()
        rpc.func = (rpc.getDeviceInfo)
        result = self.datalink.sendRpcMsg(rpc)
        if (result.response):
          return result.response.strData.split(' ')



    # Face retrieve
    def getTracePic (self, traceId):
        rpc = YtRpc()
        rpc.func = (rpc.getTracePic)
        rpc.intParams = (traceId)
        resp = self.datalink.sendRpcMsg(rpc)
        return resp.response.filePart.data

    def getFacePic (self, faceId):
        rpc = YtRpc()
        rpc.func = (rpc.getFacePic)
        rpc.intParams = (faceId)
        resp = self.datalink.sendRpcMsg(rpc)
        return resp.response.filePart.data

    def clearFaceLib (self):
        rpc = YtRpc()
        rpc.func = (rpc.clearFaceLib)
        self.datalink.sendRpcMsg(rpc)

    def setFaceId (self, faceId, faceName):
        rpc = YtRpc()
        rpc.func = (rpc.setFaceId)
        params = SetFaceIdParams()
        params.faceId = (faceId)
        params.faceName = (faceName)
        rpc.setFaceIdParams.CopyFrom(params)
        self.datalink.sendRpcMsg(rpc)

    def registerFaceIdFromCamera (self, faceName, timeoutMs):
        rpc = YtRpc()
        rpc.func = (rpc.registerFaceIdFromCamera)
        params = RegisterFaceIdFromCameraParams()
        params.timeoutMs = (timeoutMs)
        params.faceName = (faceName)
        rpc.registerFaceIdFromCameraParams.CopyFrom(params)
        result = self.datalink.sendRpcMsg(rpc)
        if (result.HasField('response') and result.response.HasField('intData')):
            return result.response.intData
        else:
            raise Exception('未知错误')


    def registerFaceIdWithRemotePic (self, remoteFile, faceName):
        rpc = YtRpc()
        rpc.func = (rpc.registerFaceIdWithPic)
        params = RegisterFaceIdWithPicParams()
        params.filePath = (remoteFile)
        params.faceName = (faceName)
        rpc.registerFaceIdWithPicParams.CopyFrom(params)
        result = self.datalink.sendRpcMsg(rpc)
        # print(result.response)
        if (result.HasField('response') and result.response.HasField('intData')):
            return result.response.intData
        else:
            raise Exception('未知错误')


    def registerFaceIdWithPic (self, localFile, faceName, progressCb = None):
        remoteFile = '/tmp/reg.jpg'
        self.datalink.sendFile(localFile, remoteFile, '', progressCb)
        faceId = self.registerFaceIdWithRemotePic(remoteFile, faceName)
        return faceId

    def deleteFaceId (self, faceId):
        rpc = YtRpc()
        rpc.func = (rpc.deleteFaceId)
        rpc.intParams = (faceId)
        self.datalink.sendRpcMsg(rpc)

    def deleteFaceName (self, faceName):
        rpc = YtRpc()
        rpc.func = (rpc.deleteFaceName)
        rpc.strParams = (faceName)
        resp = self.datalink.sendRpcMsg(rpc)
        return resp.response.intData

    def listFaceId (self):
        ret = []
        start = 0
        while (True):
            rpc = YtRpc()
            rpc.func = (rpc.listFaceId)
            params = ListFaceIdParams()
            params.start = (start)
            params.length = (100)
            rpc.listFaceIdParams.CopyFrom(params)
            result = self.datalink.sendRpcMsg(rpc)
            data = result.response.faceIdListData.faces
            if (len(data) == 0):
                break

            ret = ret + list(data)
            start = data[ len(data) - 1 ].faceId + 1

        return ret
