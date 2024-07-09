# __Multiple VL6180X sensors on the same I2C bus__
This repo is a fork of the https://gitlab.com/vitus133/vl6180x_multi repository, upgrade and addition of new features

# Introduction

This module allows operating several VL6180X Time Of Flight sensors on the same I2C bus. This is achieved by reallocating each sensor' address.
The project is intended to run on RaspberryPi. Specifically, it was tested on RaspberryPi 4 with Python 3.7

# Prerequisites
The example below is using Raspberry PI default I2C bus and two GPIOs to control two sensors:

<img src="images/connections.png">

# Running the example
1. Clone the repository:
```bash
git clone https://github.com/alfiTH/vl6180x_multi.git && cd vl6180x_multi
```
2. Create and activate Python virtual environment, install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```
3. Install the package
```bash
pip install -e .
```
4. Run the example
```bash
cd example/
python range.py
```




