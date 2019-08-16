import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="visionseed",
    version="1.1.0",
    description="python-sdk for VisionSeed - a camera module with AI ability",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://visionseed.youtu.qq.com",
    author="liang chen",
    author_email="chenliang@tencent.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["visionseed"],
    include_package_data=True,
    install_requires=["pyserial", "protobuf"],
)
