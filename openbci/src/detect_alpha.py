#!/usr/bin/env python

import rospy
from openbci.msg import BCIuVolts
from std_msgs.msg import Float32
from std_msgs.msg import Bool
from time import sleep
from stft import STFT
from movavg import MovAvg
import matplotlib.pyplot as plt
import numpy as np


class Ignore():
	def __init__(self, count):
		self.reset(count)

	def test(self):
		if self.count > 0:
			self.count -= 1
			return True
		else:
			return False

	def reset(self, count):
		self.count = count

class DetectAlpha():
	def __init__(self):

		# Initialize node
		rospy.init_node('detect_alpha', anonymous=True)

		# Get ros parameters
		sleep(10)
		fs = rospy.get_param("sampling_rate")
		#fs = 125
		print fs
		channel_count = rospy.get_param("eeg_channel_count")
		print channel_count

		# Initialize STFT
		self.stft = STFT(fs, 1.0, 0.25, channel_count)
		self.stft.remove_dc()
		self.stft.bandpass(5.0, 15.0)
		self.stft.window('hann')
		self.freq_bins = self.stft.freq_bins
		self.FFT = np.zeros((len(self.freq_bins), channel_count))

		# Choose channels
		self.channel_mask = np.full(channel_count, False, dtype = bool)
		self.channel_mask[7 -1] = True
		self.channel_mask[8 -1] = True

		# Define bands
		self.G1_mask = np.logical_and(5 < self.freq_bins, self.freq_bins < 7.5)
		self.Al_mask = np.logical_and(8.5 < self.freq_bins, self.freq_bins < 11.5)
		self.G2_mask = np.logical_and(12.5 < self.freq_bins, self.freq_bins < 15)

		# Initialize filters
		self.movavg = MovAvg(4)
		self.ignore = Ignore(0)

		# Setup publishers
		self.pub_guard1 = rospy.Publisher('guard1', Float32, queue_size=1)
		self.pub_alpha = rospy.Publisher('alpha', Float32, queue_size=1)
		self.pub_guard2 = rospy.Publisher('guard2', Float32, queue_size=1)
		self.pub_eyes = rospy.Publisher('eyes_closed', Bool, queue_size=1)

		# Subscribe
		rospy.Subscriber("eeg_channels", BCIuVolts, self.newSample)

	def newSample(self, msg):
		newFFT = self.stft.ingestSample(msg.data)
		if newFFT is not None:
			self.FFT = newFFT

			# Mask and average data
			guard1 = np.mean(newFFT[self.G1_mask, :][:, self.channel_mask])
			alpha = np.mean(newFFT[self.Al_mask, :][:, self.channel_mask])
			guard2 = np.mean(newFFT[self.G2_mask, :][:, self.channel_mask])

			detected = self.movavg.step(alpha > (guard1 + guard2)*1.1) > 0.5
			if detected and not self.ignore.test():
				self.movavg.reset()
				self.ignore.reset(4)
			else:
				detected = False
				
			# Publish messages
			msg = Float32()
			msg.data = guard1
			self.pub_guard1.publish(msg)

			msg = Float32()
			msg.data = alpha
			self.pub_alpha.publish(msg)

			msg = Float32()
			msg.data = guard2
			self.pub_guard2.publish(msg)

			msg = Bool()
			msg.data = detected
			self.pub_eyes.publish(msg)

	def updatePlot(self, line):
		line.set_ydata(np.sum(self.FFT[:,self.channel_mask], axis = 1))
		line.figure.canvas.draw()

if __name__ == '__main__':
    try:

		node = DetectAlpha()

		fig, ax = plt.subplots()
		li, = ax.plot(node.freq_bins, np.linspace(0, 10, len(node.freq_bins)))
		ax.set_xlim([0, 40])
		timer = fig.canvas.new_timer(interval=100)
		timer.add_callback(node.updatePlot, li)
		timer.start()
		plt.show()

		rospy.spin()
    except rospy.ROSInterruptException:
        pass
