#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import pyaudio
import wave
import wave
import houndify
import sys
import time
# create a node
# publish your command to /cmd
command = ''

class MyListener(houndify.HoundListener):
    def onPartialTranscript(self, transcript):
        pass# "Partial transcript: " + transcript
    def onFinalResponse(self, response):
        global command
        command = str(response['AllResults'][0]['WrittenResponse'])
      #print "Final response: " + str(response['AllResults'][0]['WrittenResponse'])
    def onTranslatedResponse(self, response):
        pass# "Translated response: " + response
    def onError(self, err):
        print "ERROR"


# start Recording

def get_input(client):

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 3

    BUFFER_SIZE = 512

    audio = pyaudio.PyAudio()

    WAVE_OUTPUT_FILENAME = "file.wav"
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,input_device_index=5)
    print "recording..."
    frames = []
     
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print "finished recording"

    stream.stop_stream()
    stream.close()
    audio.terminate()
     
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    time.sleep(.32) 

    fname = WAVE_OUTPUT_FILENAME
    audio = wave.open(fname)
    if audio.getsampwidth() != 2:
        print "%s: wrong sample width (must be 16-bit)" % fname

    if audio.getframerate() != 8000 and audio.getframerate() != 16000:
        print "%s: unsupported sampling frequency (must be either 8 or 16 khz)" % fname

    if audio.getnchannels() != 1:
        print "%s: must be single channel (mono)" % fname


    client.setSampleRate(audio.getframerate())
    samples = audio.readframes(BUFFER_SIZE)
    finished = False
    client.start(MyListener())
    while not finished:
      finished = client.fill(samples)
      time.sleep(0.032)     ## simulate real-time so we can see the partial transcripts
      samples = audio.readframes(BUFFER_SIZE)
      if len(samples) == 0:
        break
    client.finish()

def main():
    global command
    rospy.init_node('audio_talker', anonymous=True)
    pub = rospy.Publisher('cmd', String, queue_size=10)
    rate = rospy.Rate(10) # 10hz
    CLIENT_ID = "hdKwZUmJRsWt1JZ7diilRw=="  # Houndify client IDs are Base64-encoded strings
    CLIENT_KEY = "-agR6tLJpEjPuYGmxMNN1n6byUPOW8c1vPXYxHqHyZ6-hFwJDl-LEuSFNXGN-YKsjdvIJNyFTWu1nm--ac-ljg=="  # Houndify client keys are Base64-encoded strings
    client = houndify.StreamingHoundClient(CLIENT_ID, CLIENT_KEY, "test_user")
    ## Pretend we're at SoundHound HQ.  Set other fields as appropriate
    client.setLocation(37.388309, -121.973968)
    while not rospy.is_shutdown():
        get_input(client)
        cmd = command.lower()
        cmd = cmd.split(' ')[-1]
        print command
        pub.publish(cmd)
        rate.sleep()

if __name__ == '__main__':
    main()

#!/usr/bin/env python


# The code below will demonstrate how to use streaming audio through Hound
#

# We'll accept WAV files but it should be straightforward to 
# use samples from a microphone or other source


#
# Simplest HoundListener; just print out what we receive.
#
# You can use these callbacks to interact with your UI.
#




