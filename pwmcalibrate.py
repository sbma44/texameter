import time, json, curses, wiringpi

SOFTPWM_SUPPORT = True
try:
	import wiringpi2 as wiringpi
except Exception, e:
	SOFTPWM_SUPPORT = False
finally:
	import wiringpi as wiringpi

PWM_MAX = 1023
SOFT_PWM_MAX = 100
DEFAULT_PIN = 1
WIRINGPI_PWM_PIN = 1 # only pin 1 can handle hardware PWM
DEFAULT_CALIBRATION_FILENAME = "calibration.json"

class PWMCalibrator(object):
	"""Helper class for calibrating PWM-driven VU meters"""
	def __init__(self, pin=DEFAULT_PIN, calibration_file=None, smoothing=None, wiringpi_obj=None):
		super(PWMCalibrator, self).__init__()
		
		if not SOFTPWM_SUPPORT and pin!=WIRINGPI_PWM_PIN:
			raise Exception("No soft PWM support (is wiringpi2 installed?). Only pin 1 may be used.")

		self.pin = pin

		if wiringpi_obj is not None:
			self.wp = wiringpi_obj
		else:
			self.wp = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
		
		# PWM: hardware or software?
		if (not SOFTPWM_SUPPORT) or (self.pin==WIRINGPI_PWM_PIN):
			self.wp.pinMode(self.pin, self.wp.PWM_OUTPUT)
			self.pwm_write = self.wp.pwmWrite
			self.pwm_max = PWM_MAX
		else:
			self.wp.softPwmCreate(self.pin, 0, SOFT_PWM_MAX)
			self.pwm_write = self.wp.softPwmWrite
			self.pwm_max = SOFT_PWM_MAX

		self.pwm_value = 0
		self.calibration = []
                if smoothing is True:
                        self.smoothing = 0.005
                else:	
		        self.smoothing = smoothing

		if calibration_file is not None:
			self.load(calibration_file)

	def load(self, filename=DEFAULT_CALIBRATION_FILENAME):
		f = open(filename, 'r')
		self.calibration = json.load(f)
		f.close()

	def _calculatePWM(self,value):
		bottom_step = 0
                pwm_value = 0

		if value<self.calibration[0][0] or value>self.calibration[-1][0]:
			raise Exception("Requested value is outside of calibration range [%d, %d]" % (self.calibration[0][0], self.calibration[-1][0]))

                # check for an exact value match & return it if found
                for x in self.calibration:
                        if x[0]==value:
                                return x[1]

		for i in range(0, len(self.calibration)-1):
			if value>=self.calibration[i][0] and value<self.calibration[i+1][0]:
				bottom_step = i

		pct_diff = (value - self.calibration[bottom_step][0]) / (1.0 * (self.calibration[bottom_step + 1][0] - self.calibration[bottom_step][0]))
		pwm_value = int(self.calibration[bottom_step][1] + round(pct_diff * (self.calibration[bottom_step + 1][1] - self.calibration[bottom_step][1])))
		return pwm_value

	def setPWM(self, value):
		target_pwm_value = self._calculatePWM(value)
		if self.smoothing is not None:
			while self.pwm_value!=target_pwm_value:
				delta = self.pwm_value>target_pwm_value and -1 or 1				
				self.pwm_write(self.pin, self.pwm_value + delta)
				self.pwm_value = self.pwm_value + delta
				time.sleep(self.smoothing)
		else:
			self.pwm_write(self.pin, target_pwm_value)
			self.pwm_value = target_pwm_value



	def calibrate(self, steps=None):
		# clear the calibration list
		self.calibration = []

		# max the display, ask for trim pot adjustment
		self.pwm_write(self.pin, self.pwm_max)
		if steps==None:
			steps = int(raw_input("Calibrate the trim pot until the meter is at maximum, then enter the desired number of steps and press <enter>: "))
		else:
			raw_input("Calibrate the trim pot until the meter is at maximum (%d), then press <enter>" % steps)
		
		# set the top step
		self.calibration.append((steps, self.pwm_max))

		# init curses, preventing delay on keypress
		stdscr = curses.initscr()
		curses.cbreak()
		stdscr.nodelay(1)

		# step down through the PWM range
		current_step = steps - 1
		for i in range(self.pwm_max, 0, -1):			
			self.pwm_write(self.pin, i)

			stdscr.addstr(0,0,"Press the spacebar when the meter reads %d" % (current_step))
			
			stdscr.addstr(2,0,"=== Captured Calibration Values ===")
			stdscr.addstr(3,0,"      step      |        value     ")
			stdscr.addstr(4,0,"-----------------------------------")
			for (j,x) in enumerate(self.calibration):
				stdscr.addstr(5+j, 7 - len(str(x[0])), str(x[0]))
				stdscr.addstr(5+j, 16, "|")
				stdscr.addstr(5+j, 30 - len(str(x[1])), str(x[1]))
			stdscr.refresh()

			key = stdscr.getch()
			if key==ord(' '):
				self.calibration.append((current_step, i))
				current_step = current_step - 1
				if current_step<0:
					break
			time.sleep(0.1)

		# append an entry for zero if one wasn't recorded
		found_zero = False
		for x in self.calibration:
			if x[0]==0:
				found_zero = True
		if not found_zero:
			self.calibration.append((0,0))

		# end the curses session
		curses.endwin()

		# sort the calibration list
		self.calibration.sort(key=lambda x: x[0])


	def save(self, filename=DEFAULT_CALIBRATION_FILENAME):
		f = open(filename, 'w')
		json.dump(self.calibration, f)
		f.close()



def main():
	c = PWMCalibrator()
	c.calibrate()
	c.save()

if __name__ == '__main__':
	main()
