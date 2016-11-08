
from __future__ import print_function

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
GObject.threads_init()
Gst.init(None)

pipeline = Gst.parse_launch('uridecodebin name=source ! audioconvert !' +
                            ' audioresample ! pocketsphinx name=asr !' +
                            ' fakesink')
source = pipeline.get_by_name('source')
source.set_property('uri', 'http://ted.mielczarek.org/test.wav')
# If you want to configure the decoder:
#pocketsphinx = pipeline.get_by_name('asr')
#pocketsphinx.set_property('hmm', '/usr/local/share/pocketsphinx/model/en-us/en-us')
#pocketsphinx.set_property('lm', '/usr/local/share/pocketsphinx/model/en-us/en-us.lm.bin')
#pocketsphinx.set_property('dict', '/usr/local/share/pocketsphinx/model/en-us/cmudict-en-us.dict')
#pocketsphinx.set_property('configured', True)

bus = pipeline.get_bus()

# Start playing
while True:
    #print(pipeline.change_state())
    pipeline.set_state(Gst.State.NULL)
    msg = bus.timed_pop(Gst.CLOCK_TIME_NONE)
    pipeline.set_state(Gst.State.PLAYING)

    if msg:
        if msg.type == Gst.MessageType.EOS:
            break
        struct = msg.get_structure()
        if struct and struct.get_name() == 'pocketsphinx':
            if struct['final']:
                # final result
                print(struct['hypothesis'])
            elif struct['hypothesis']:
                # intermediate result
                #print(struct['hypothesis'])
                pass


# Free resources
pipeline.set_state(Gst.State.NULL)