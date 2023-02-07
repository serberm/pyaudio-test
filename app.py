from flask import Flask, Response, render_template
import pyaudio
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', headers={'Content-Type': 'text/html'})

def generate_wav_header(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')
    o += (datasize + 36).to_bytes(4,'little')
    o += bytes("WAVE",'ascii')
    o += bytes("fmt ",'ascii')
    o += (16).to_bytes(4,'little')
    o += (1).to_bytes(2,'little')
    o += (channels).to_bytes(2,'little')
    o += (sampleRate).to_bytes(4,'little')
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')
    o += (bitsPerSample).to_bytes(2,'little')
    o += bytes("data",'ascii')
    o += (datasize).to_bytes(4,'little')
    return o

def get_sound(InputAudio):

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    CHUNK = 1024
    SAMPLE_RATE = 44100
    BITS_PER_SAMPLE = 16

    wav_header = generate_wav_header(SAMPLE_RATE, BITS_PER_SAMPLE, CHANNELS)

    stream = InputAudio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=1,
        frames_per_buffer=CHUNK
    )

    first_run = True
    while True:
       if first_run:
           data = wav_header + stream.read(CHUNK)
           first_run = False
       else:
           data = stream.read(CHUNK)
       yield(data)


@app.route('/audio_feed')
def audio_feed():

    return Response(
        get_sound(pyaudio.PyAudio()),
        content_type = 'audio/wav',
    )

if __name__ == '__main__':
    app.run(debug=True)
