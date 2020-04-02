import RPi.GPIO as GPIO
from time import sleep

# GPIO Ports
Enc_A = 23  # Encoder input A
Enc_B = 24  # Encoder input B
Enc_LED_R = 5
Enc_LED_G = 6
Enc_LED_B = 13
Enc_SW = 22

encoder_counter = 0
encoder_counter_max = 4


def init_encoder():
    GPIO.setwarnings(True)

    # Use the Raspberry Pi BCM pins
    GPIO.setmode(GPIO.BCM)

    # define the Encoder switch inputs
    GPIO.setup(Enc_A, GPIO.IN)
    GPIO.setup(Enc_B, GPIO.IN)

    GPIO.setup(Enc_SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Setup the LED outputs and turn off
    GPIO.setup(Enc_LED_R, GPIO.OUT)
    GPIO.setup(Enc_LED_G, GPIO.OUT)
    GPIO.setup(Enc_LED_B, GPIO.OUT)
    GPIO.output(Enc_LED_R, True)
    GPIO.output(Enc_LED_G, True)
    GPIO.output(Enc_LED_B, True)


    # setup an event detection thread for the A encoder switch
    GPIO.add_event_detect(Enc_A, GPIO.FALLING, callback=rotation_decode, bouncetime=3)  # bouncetime in mSec
    # GPIO.add_event_detect(Enc_SW, GPIO.RISING, callback=switch_pressed, bouncetime=5)  # bouncetime in mSec


def rotation_decode(Enc_A):
    global encoder_counter

    # read both of the switches
    switch_a = GPIO.input(Enc_A)
    switch_b = GPIO.input(Enc_B)

    if (switch_a == 0) and (switch_b == 1):  # A then B ->
        encoder_counter += 1
        if encoder_counter > encoder_counter_max:
            encoder_counter = 0
        # print("direction -> ", encoder_counter)
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
        # print("direction <- ", encoder_counter)
        while switch_a == 0:
            switch_a = GPIO.input(Enc_A)
        return

    else:  # discard all other combinations
        return None


def switch_pressed(Enc_SW):
    set_led('B', True)
    switch = GPIO.input(Enc_SW)
    while switch == 1:
        switch = GPIO.input(Enc_SW)
    set_led('B', False)


def set_led(colour, state):
    if colour is 'R':
        GPIO.output(Enc_LED_R, not state)
    elif colour is 'G':
        GPIO.output(Enc_LED_G, not state)
    elif colour is 'B':
        GPIO.output(Enc_LED_B, not state)


def encoder_count():
    return encoder_counter


def set_encoder_count(count):
    global encoder_counter
    encoder_counter = count


def set_encoder_count_max(count):
    global encoder_counter_max
    encoder_counter_max = count


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
