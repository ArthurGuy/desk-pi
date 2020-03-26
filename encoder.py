import RPi.GPIO as GPIO
from time import sleep

# GPIO Ports
Enc_A = 23  # Encoder input A
Enc_B = 24  # Encoder input B

counter = 0
counter_max = 5


def init():
    '''
    Initializes a number of settings and prepares the environment
    before we start the main program.
    '''
    print("Rotary Encoder Test Program")

    GPIO.setwarnings(True)

    # Use the Raspberry Pi BCM pins
    GPIO.setmode(GPIO.BCM)

    # define the Encoder switch inputs
    GPIO.setup(Enc_A, GPIO.IN)
    GPIO.setup(Enc_B, GPIO.IN)

    # setup an event detection thread for the A encoder switch
    GPIO.add_event_detect(Enc_A, GPIO.FALLING, callback=rotation_decode, bouncetime=2)  # bouncetime in mSec
    #


def rotation_decode(Enc_A):
    global counter

    # read both of the switches
    Switch_A = GPIO.input(Enc_A)
    Switch_B = GPIO.input(Enc_B)

    if (Switch_A == 0) and (Switch_B == 1):  # A then B ->
        counter += 1
        if counter > counter_max:
            counter = 0
        print("direction -> ", counter)
        while Switch_B == 1:
            Switch_B = GPIO.input(Enc_B)

        # now wait for B to drop to end the click cycle
        while Switch_B == 0:
            Switch_B = GPIO.input(Enc_B)
        return

    elif (Switch_A == 0) and (Switch_B == 0):  # B then A <-
        counter -= 1
        if counter < 0:
            counter = counter_max
        print("direction <- ", counter)
        while Switch_A == 0:
            Switch_A = GPIO.input(Enc_A)
        return

    else:  # discard all other combinations
        return None


def main():
    try:

        init()
        while True:
            # wait for an encoder click
            sleep(1)

    except KeyboardInterrupt:  # Ctrl-C to terminate the program
        GPIO.cleanup()


if __name__ == '__main__':
    main()