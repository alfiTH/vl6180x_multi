from vl6180x_multi import MultiSensor
from time import sleep, time

if __name__ == "__main__":
    ms = MultiSensor(ids=list(range(3)), gpios=[10, 9, 11], new_i2c_addresses=[0x30, 0x31, 0x32], offsets=[100, 100, 100])
    while 1:
        t1 = time()
        print("\r", end="")
        for i in range(3):
           print(f"Sensor {i}: {ms.get_range(i)} | ", end="")
        print(f"Duration: {time()-t1:.5f}" , end="        ")
        sleep(0.04)


