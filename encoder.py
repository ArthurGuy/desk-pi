import RPi.GPIO as GPIO
from time import sleep

# GPIO Ports
Enc_A = 23  # Encoder input A
Enc_B = 24  # Encoder input B

encoder_counter = 0
encoder_counter_max = 5


def init_encoder():
    GPIO.setwarnings(True)

    # Use the Raspberry Pi BCM pins
    GPIO.setmode(GPIO.BCM)

    # define the Encoder switch inputs
    GPIO.setup(Enc_A, GPIO.IN)
    GPIO.setup(Enc_B, GPIO.IN)

    # setup an event detection thread for the A encoder switch
    GPIO.add_event_detect(Enc_A, GPIO.FALLING, callback=rotation_decode, bouncetime=2)  # bouncetime in mSec


def rotation_decode(Enc_A):
    global encoder_counter

    # read both of the switches
    switch_a = GPIO.input(Enc_A)
    switch_b = GPIO.input(Enc_B)

    if (switch_a == 0) and (switch_b == 1):  # A then B ->
        encoder_counter += 1
        if encoder_counter > encoder_counter_max:
            encoder_counter = 0
        print("direction -> ", encoder_counter)
        while switch_b == 1:
            switch_b = GPIO.input(Enc_B)

        # now wait for B to drop to end the click cycle
        while switch_b == 0:
            switch_b = GPIO.input(Enc_B)
        return

    elif (switch_a == 0) and (switch_b == 0):  # B then A <-
        encoder_counter -= 1
        if encoder_counter < 0:
            encoder_counter = encoder_counter_max
        print("direction <- ", encoder_counter)
        while switch_a == 0:
            switch_a = GPIO.input(Enc_A)
        return

    else:  # discard all other combinations
        return None


def encoder_count():
    return encoder_counter


def encoder_cleanup():
    GPIO.cleanup()


def main():
    try:

        init_encoder()
        while True:
            # wait for an encoder click
            sleep(1)

    except KeyboardInterrupt:  # Ctrl-C to terminate the program
        encoder_cleanup()


if __name__ == '__main__':
    main()
