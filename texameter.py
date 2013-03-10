import os, pwmcalibrate, wiringpi, scrapelib



class Texameter(object):
	"""Controls the meter bought at Uncommon Objects"""

	GPIO_RED = 5
	GPIO_YELLOW = 4
	GPIO_METER = 1
	GPIO_LIST = (GPIO_RED, GPIO_YELLOW, GPIO_METER)

	def __init__(self):
		self.yellow = False
		self.red = False
		self.meter = 0
		
		self.wp = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
		self.wp.pinMode(self.GPIO_YELLOW, wiringpi.OUTPUT)
		self.wp.pinMode(self.GPIO_RED, wiringpi.OUTPUT)

		self.pwm_calibrator = pwmcalibrate.PWMCalibrator(smoothing=0.005, wiringpi_obj=self.wp)
		self.pwm_calibrator.load()

		self.set_meter(self.meter)
		self.set_yellow(self.yellow)
		self.set_red(self.red)

	def set_yellow(self, status):		
		self.wp.digitalWrite(self.GPIO_YELLOW, status and self.wp.HIGH or self.wp.LOW)
		self.yellow = status

	def set_red(self, status):		
		self.wp.digitalWrite(self.GPIO_RED, status and self.wp.HIGH or self.wp.LOW)
		self.red = status

	def set_meter(self, value):
		self.pwm_calibrator.setPWM(value)

def main():
	pass

if __name__ == '__main__':
	main()
