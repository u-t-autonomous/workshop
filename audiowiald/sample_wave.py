#!/usr/bin/env python
import wave
import houndify
import sys
import time

# The code below will demonstrate how to use streaming audio through Hound
#
if __name__ == '__main__':
  # We'll accept WAV files but it should be straightforward to 
  # use samples from a microphone or other source

  BUFFER_SIZE = 512

  if len(sys.argv) < 4:
    print "Usage: %s <client ID> <client key> <wav file> [ <more wav files> ]" % sys.argv[0]
    sys.exit(0)
  
  CLIENT_ID = sys.argv[1]
  CLIENT_KEY = sys.argv[2]

  #
  # Simplest HoundListener; just print out what we receive.
  #
  # You can use these callbacks to interact with your UI.
  #
  class MyListener(houndify.HoundListener):
    def onPartialTranscript(self, transcript):
      print "Partial transcript: " + transcript
    def onFinalResponse(self, response):
      print "Final response: " + str(response)
    def onError(self, err):
      print "Error: " + str(err)

  client = houndify.StreamingHoundClient(CLIENT_ID, CLIENT_KEY, "test_user")
  
  ## Pretend we're at SoundHound HQ.  Set other fields as appropriate
  client.setLocation(37.388309, -121.973968)

  ## Uncomment the lines below to see an example of using a custom
  ## grammar for matching.  Use the file 'turnthelightson.wav' to try it.
  # clientMatches = [ {
  #   "Expression" : '([1/100 ("can"|"could"|"will"|"would")."you"].[1/10 "please"].("turn"|"switch"|(1/100 "flip"))."on".["the"].("light"|"lights").[1/20 "for"."me"].[1/20 "please"])|([1/100 ("can"|"could"|"will"|"would")."you"].[1/10 "please"].[100 ("turn"|"switch"|(1/100 "flip"))].["the"].("light"|"lights")."on".[1/20 "for"."me"].[1/20 "please"])|((("i".("want"|"like"))|((("i".["would"])|("i\'d")).("like"|"want"))).["the"].("light"|"lights").["turned"|"switched"|("to"."go")|(1/100"flipped")]."on".[1/20"please"])"',
  #   "Result" : { "Intent" : "TURN_LIGHT_ON" },
  #   "SpokenResponse" : "Ok, I\'m turning the lights on.",
  #   "SpokenResponseLong" : "Ok, I\'m turning the lights on.",
  #   "WrittenResponse" : "Ok, I\'m turning the lights on.",
  #   "WrittenResponseLong" : "Ok, I\'m turning the lights on."
  # } ]
  # client.setHoundRequestInfo('ClientMatches', clientMatches)

  for fname in sys.argv[3:]:
    print "============== %s ===================" % fname
    audio = wave.open(fname)
    if audio.getsampwidth() != 2:
      print "%s: wrong sample width (must be 16-bit)" % fname
      break
    if audio.getframerate() != 8000 and audio.getframerate() != 16000:
      print "%s: unsupported sampling frequency (must be either 8 or 16 khz)" % fname
      break
    if audio.getnchannels() != 1:
      print "%s: must be single channel (mono)" % fname
      break

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
