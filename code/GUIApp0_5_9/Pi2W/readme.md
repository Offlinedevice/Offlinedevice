## Offline device with Raspberry Pi 2 W and graphical interface:
### Raspberry Pi Zero 2 W configuration:
 - Raspberry Pi Zero 2 W
 - Real Time Clock (RTC DS1307 with rechargeable battery)
 - RC522 RFID module
 - Pi camera module 1 (ov5647), or module 2 (imx219) or module 3 (imx708)

### Wiring schematics Raspberry Pi Zero 2 W:
Make sure to use the correct 3D file for the lid as the camera modules differ in height. Use 2 mm screws with the right lenght during assembly. 

<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/344116e8c903bb7597abc3f70e1aaa833e193e92/3D/PiZero2W/Schematic_Pi2W_wiring.JPG"></p>

### Software and operating system
The full image can be burned to a microSD- card with minimum 32 gb storage. Make sure you use a high quality SD- card.
Note, the image is only operational with specified hardware stated above. The RFID module is optional.
The GUIApp.py version 0.5.9 can be installed using GUIApp0_5_9_Pi2W.tar.gz. It needs the the full image (the operating system) version 0.5.9 or later to be installed first. 
