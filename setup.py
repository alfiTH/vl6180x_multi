import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vl6180x-multi",
    version="1.0.3",
    author="Alejandro Torrejon Harto",
    author_email="atorrejon@unex.es",
    description="Multiple VL6180X time of flight distance sensors on the same I2C bus.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alfiTH/vl6180x_multi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "adafruit-circuitpython-vl6180x",
        "RPi.GPIO",
    ],
)
