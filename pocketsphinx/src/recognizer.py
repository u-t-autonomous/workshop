#!/usr/bin/env python

from os import environ, path


from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

import roslib; roslib.load_manifest('pocketsphinx')
import rospy
from std_msgs.msg import String
from std_srvs.srv import *


MODELDIR = "/home/sahabi/pocketsphinx-5prealpha/model" # for default pocketsphinx models and files
DATADIR = "/home/sahabi/pocketsphinx-5prealpha/test/data"


rospy.init_node("recognizer")
_device_name_param = "~mic_name"  # Find the name of your microphone by typing pacmd list-sources in the terminal
_lm_param = "~lm"
_dic_param = "~dict"
_activation_key_param = "~activation_key" # might be used in the future
if rospy.has_param(_lm_param):
    lm = rospy.get_param(_lm_param)

if rospy.has_param(_dic_param):
    dic = rospy.get_param(_dic_param)


config = Decoder.default_config()
config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
#config.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.bin'))
config.set_string('-lm', lm)
config.set_string('-dict', dic)
#config.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
config.set_string('-logfn', '/dev/null')
#config.set_string('-lifter', '22')
decoder = Decoder(config)

import pyaudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
stream.start_stream()

in_speech_bf = False
decoder.start_utt()



#rospy.on_shutdown(shutdown)
pub = rospy.Publisher('~output', String)
pub2 = rospy.Publisher('cmd', String)

while not rospy.is_shutdown():
    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
        if decoder.get_in_speech() != in_speech_bf:
            in_speech_bf = decoder.get_in_speech()
            if not in_speech_bf:
                msg = ''
                decoder.end_utt()
                hypothesis = decoder.hyp()
                logmath = decoder.get_logmath()
                print ('Best hypothesis: ', hypothesis.hypstr, " model score: ", logmath.exp(hypothesis.best_score), " confidence: ", logmath.exp(hypothesis.prob))

                msg += 'Best hypothesis segments: '
                #print ('Best hypothesis segments: ')
                total_prob = 1
                for seg in decoder.seg():
                    total_prob *= logmath.exp(seg.prob)
                    msg += str(seg.word) + " " + str(logmath.exp(seg.prob)) + " "
                    #print(seg.word, logmath.exp(seg.prob))
                #print ('Best hypothesis segments: ', [seg.word, (logmath.exp(seg.prob)) for seg in decoder.seg()])
                #print ('Total seg prob: ' + str(total_prob))
                msg += 'Total seg prob: ' + str(total_prob)
                pub.publish(msg)
                pub2.publish(hypothesis.hypstr.lower())
                decoder.start_utt()
    else:
        break
decoder.end_utt()