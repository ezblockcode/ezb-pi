#!/usr/bin/python3
from ezblock import PWM
from ezblock import Servo

pwm_P11 = PWM("P11")

Servo(pwm_P11).angle(0)


def forever():
  pass
