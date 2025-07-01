import sys
import time
import signal
from pyzbar.pyzbar import decode
from picamera2 import MappedArray, Picamera2, Preview
from libcamera import Transform, controls

captured_QR = False
captured_data = "Empty"

def alarm_handler(signum, frame):
	picam2.stop()
	sys.exit("No QR-code found")
	
def read_QR(request):	
	with MappedArray(request, "main") as m:
		for b in QRcodes:
			captured_data = b.data.decode('utf-8')
			completeNameQRfile = "/home/user1/secure/QRsignaturefile.txt"
			f2 = open(completeNameQRfile, 'w')
			f2.write(captured_data)
			f2.close()
			picam2.start_preview(Preview.NULL)
			picam2.stop()
			captured_QR = True

signal.signal(signal.SIGALRM, alarm_handler)
signal.alarm(40)

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL, x=600, y=430, width=640, height=480, transform=Transform(hflip=True, vflip=True))

QRcodes = []
picam2.post_callback = read_QR

picam2.start()

try:
	picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
except:
	print("No autofocus")

time.sleep(0.1)

while not captured_QR:
	rgb = picam2.capture_array("main")			
	QRcodes = decode(rgb)
