### python-sdk for VisionSeed - a camera module with AI ability

[![License](https://img.shields.io/github/license/tencent-youtu-visionseed/yt-visionseed-sdk-python)](https://raw.githubusercontent.com/tencent-youtu-visionseed/yt-visionseed-sdk-python/master/LICENSE)

---

# install
```shell
pip3 install --upgrade visionseed
```

# run example
```shell
python3 example/example.py
```

# run example-cocos2d
```shell
pip3 install opencv-python
pip3 install matplotlib
pip3 install cocos2d
python3 example/example-cocos2d.py
```

# run example on Windows
You need to modify the line in example.py, and replace "/dev/ttyACM0" to your VisionSeed's virtual port number, e.g. "COM3":
```python
datalink = vs.YtDataLink( serial.Serial("/dev/ttyACM0",115200,timeout=0.5) )
```

# more
Homepage: https://visionseed.youtu.qq.com

技术交流QQ群: 684338220(超多大佬)
