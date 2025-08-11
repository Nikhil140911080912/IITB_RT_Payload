from machine import UART, Pin
import time

# UART1 uses GPIO4 (TX), GPIO5 (RX)
uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

print("Listening on UART1...")

while True:
    if uart1.any():
        msg = uart1.readline()
        #print(list(msg))
        if msg:
            try:
                decoded = msg.decode()
                print("Received:", decoded)
        time.sleep(0.1)
