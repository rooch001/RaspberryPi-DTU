import RPi.GPIO as GPIO
import time
up  = 2
down = 3
select = 4
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(up,GPIO.IN)
    GPIO.setup(down,GPIO.IN)

    GPIO.setup(select,GPIO.IN, pull_up_down = GPIO.PUD_UP)

    
def loop():
    while True:
        upstate = GPIO.input(up)
        downstate = GPIO.input(down)
        selectstate = GPIO.input(select)
        if upstate == False:
            print("Button up")
            
        elif downstate == False:
            print("Button down")
        
        elif selectstate == False:
            print("Button select")
        
        time.sleep(0.2)
            

def endprogram():
    GPIO.cleanup()
if __name__ == "__main__":
    
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        print("Keyboard ")
        endprogram()
