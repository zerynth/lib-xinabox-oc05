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

    
===============
OC05 class
===============

.. class:: OC05(self, drvname, addr=0x78, clk=100000)

        Create an instance of the OC05 class.

        :param drvname: I2C Bus used '( I2C0, ... )'
        :param addr: Slave address, default 0x78
        :param clk: Clock speed, default 100kHz

    
.. method:: init(outFreq)
        
        Configures the registers of PCA9685 and sets the frequency of modulation.
        Call before using OC05

        :param outFreq: Frequency of servo motor, default 60 for typical analogue servos

        
.. method:: setServoPosition(channelNum, degrees)
        
        Positions a servo on a selected channel by the desired degrees.

        :param channelNum: Number of the channel. Corresponds to channel numbers on OC05 (1-8)
        :param degrees: Desired rotational distance in degrees

        
.. method:: setPinPulseRange(pinNum, onStep, offStep)
        
        Sets the PWM output on a selected pin.

        :param pinNum: Number of the channel. Corresponds to channel numbers on OC05 (1-8)
        :param onStep: The point at which to turn the PWM output ON (0-4095)
        :param offStep: The point at which to turn the PWM output OFF (0-4095)

        
.. method:: setCRServoPosition(channelNum, speed)
        
        Used to set the rotation speed of a continous rotation servo from -100% to 100%.

        :param channelNum: Number of the channel. Corresponds to channel numbers on OC05 (1-8)
        :param speed: speed [-100-100] The speed (-100-100) to turn the servo at

        
