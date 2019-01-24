"""
.. module:: OC05

***************
 OC05 Module
***************

This is a Module for the `OC05 <https://wiki.xinabox.cc/OC05_-_Servo_Driver>`_ 8-channel Servo Driver.
The xChip is based off the PCA9685 LED controller manufactured by NXP Semiconductors.
The board uses I2C for communication.

Data Sheets:

-  `PCA9685 <https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf>`_
-  `BU33SD5 <http://rohmfs.rohm.com/en/products/databook/datasheet/ic/power/linear_regulator/buxxsd5wg-e.pdf>`_

    """
import i2c
import math

PCA9685_I2C_ADDR        = 0x78
PCA9685_PRESCALE        = 0xFE
PCA9685_MODE_1          = 0x00
PCA9685_MODE_1_DEF      = 0x01
PCA9685_MODE_2          = 0x01
PCA9685_MODE_2_DEF      = 0x04
PCA9685_SLEEP           = PCA9685_MODE_1_DEF | 0x10
PCA9685_WAKE            = PCA9685_MODE_1_DEF & 0xEF
PCA9685_RESTART         = PCA9685_WAKE | 0x80
PCA9685_ALL_LED_ON_L    = 0xFA
PCA9685_ALL_LED_ON_H    = 0xFB
PCA9685_ALL_LED_OFF_L   = 0xFC
PCA9685_ALL_LED_OFF_H   = 0xFD
PinRegDistance          = 4
PCA9685_LED8_ON_L       = 0x26
PCA9685_LED8_ON_H       = 0x27
PCA9685_LED8_OFF_L      = 0x28
PCA9685_LED8_OFF_H      = 0x29

class OC05(i2c.I2C):
    '''

===============
OC05 class
===============

.. class:: OC05(self, drvname, addr=0x78, clk=100000)

        Create an instance of the OC05 class.

        :param drvname: I2C Bus used '( I2C0, ... )'
        :param addr: Slave address, default 0x78
        :param clk: Clock speed, default 100kHz

    '''
    frequency=0
    def __init__(self, drvname=I2C0, addr=PCA9685_I2C_ADDR, clk=100000):
        i2c.I2C.__init__(self,drvname,addr,clk)
        self._addr=addr
        try:
            self.start()
        except PeripheralError as e:
            print(e)

    def init(self, outFreq=60):
        '''
.. method:: init(outFreq)
        
        Configures the registers of PCA9685 and sets the frequency of modulation.
        Call before using OC05

        :param outFreq: Frequency of servo motor, default 60 for typical analogue servos

        ''' 
        if outFreq > 1000:
            self.frequency = 1000
        elif outFreq < 40:
            self.frequency = 40
        else:
            self.frequency = outFreq
        prescaler = self.calcFreqPrescaler(self.frequency)
        try:
            self.write_bytes(PCA9685_MODE_1, PCA9685_SLEEP)
            self.write_bytes(PCA9685_PRESCALE, prescaler)
            self.write_bytes(PCA9685_LED8_ON_L, 0x00)
            self.write_bytes(PCA9685_LED8_ON_H, 0x00)
            self.write_bytes(PCA9685_LED8_OFF_L, 0x00)
            self.write_bytes(PCA9685_LED8_OFF_H, 0x00)
            self.write_bytes(PCA9685_MODE_1, PCA9685_WAKE)
            sleep(1000)
            self.write_bytes(PCA9685_MODE_1, PCA9685_RESTART)
        except Exception as e:
            print(e)
            raise e

    def setServoPosition(self, channelNum, degrees):
        '''
.. method:: setServoPosition(channelNum, degrees)
        
        Positions a servo on a selected channel by the desired degrees.

        :param channelNum: Number of the channel. Corresponds to channel numbers on OC05 (1-8)
        :param degrees: Desired rotational distance in degrees

        '''
        channelNum = max(1, min(8, channelNum))
        degrees = max(0, min(180, degrees))
        pwm = self.degrees180ToPWM(self.frequency, degrees, 5, 25)

        return self.setPinPulseRange(channelNum, 0, pwm)

    def setPinPulseRange(self, pinNum, onStep=0, offStep=2048):
        '''
.. method:: setPinPulseRange(pinNum, onStep, offStep)
        
        Sets the PWM output on a selected pin.

        :param pinNum: Number of the channel. Corresponds to channel numbers on OC05 (1-8)
        :param onStep: The point at which to turn the PWM output ON (0-4095)
        :param offStep: The point at which to turn the PWM output OFF (0-4095)

        '''
        pinNumber = max(1, min(8, pinNum))
        pinOffset = (PinRegDistance * (pinNumber -1))
        onStep = max(0, min(4095, onStep))
        offStep = max(0, min(4095, offStep))
        try:
            # Low byte of onStep
            self.write_bytes(pinOffset + PCA9685_LED8_ON_L, onStep & 0xFF)

            # High byte of onStep
            self.write_bytes(pinOffset + PCA9685_LED8_ON_H, (onStep >> 8))

            # Low byte of offStep
            self.write_bytes(pinOffset + PCA9685_LED8_OFF_L, offStep & 0xFF)

            # High byte of offStep
            self.write_bytes(pinOffset + PCA9685_LED8_OFF_H, (offStep >> 8))
        except PeripheralError as e:
            print(e)
            raise e
            
    def setCRServoPosition(self, channelNum, speed):
        '''
.. method:: setCRServoPosition(channelNum, speed)
        
        Used to set the rotation speed of a continous rotation servo from -100% to 100%.

        :param channelNum: Number of the channel. Corresponds to channel numbers on OC05 (1-8)
        :param speed: speed [-100-100] The speed (-100-100) to turn the servo at

        '''
        isReverse=False
        pwm=0
        channelnum = max(1, min(8, channelNum))
        offsetStart = self.calcFreqOffset(self.freqency, 5)
        offsetMid = self.calcFreqOffset(self.freqency, 15)
        offsetEnd = self.calcFreqOffset(self.freqency, 25)
        if speed == 0:
            return self.setPinPulseRange(channelnum, 0, offsetMid)
        
        if speed<0:
            isReverse = True
        if isReverse:
            spread=offsetMid - offsetStart
        else:
            spread=offsetEnd - offsetMid

        
        speed = math.abs(speed)
        calcOffset = ((speed * spread) / 100)
        
        if isReverse:
            pwm = offsetMid - calcOffset
        else:
            pwm = offsetMid + calcOffset
        return self.setPinPulseRange(channelnum, 0, pwm)

    def calcFreqPrescaler(self, freq):
        return int(math.floor((25000000 / (freq * 4096))) - 1)

    def calcFreqOffset(self, freq, offset):
        return ((offset * 1000) / (1000 / freq) * 4096) / 10000

    def degrees180ToPWM(self, freq, degrees, offsetStart, offsetEnd):
        offsetEnd = self.calcFreqOffset(freq, offsetEnd)
        offsetStart = self.calcFreqOffset(freq, offsetStart)
        spread = offsetEnd - offsetStart
        calcOffset = ((degrees * spread) / 180) + offsetStart
        return int(max(offsetStart, min(offsetEnd, calcOffset)))