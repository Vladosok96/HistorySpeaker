import os

from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, request
import wave
import sys
import json

from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bruhbruh'
app.config['UPLOAD_FOLDER'] = 'static'
ALLOWED_EXTENSIONS = {'wav'}


def get_response_json(number, text, error):
    return f'{{"response": {number}, "text": "{text}", "error": "{error}"}}'


def is_contains(operand, words):
    for word in words:
        if word in operand:
            return True
    return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route('/voice/', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.webm'))

    os.system(f"ffmpeg -loglevel quiet -y -i {os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.webm')} -ac 1 -f wav {os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.wav')}")

    wf = wave.open(os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.wav'), "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    model = Model(lang="ru")

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass
        else:
            pass

    result = json.loads(rec.FinalResult())
    recognized_words = result['result']
    recognized_text = result['text']

    for word in recognized_words:
        word_text = word['word']
        if is_contains(word_text, ['одинадцат', 'одиннадцат']):
            return get_response_json(11, recognized_text, 0)
        if is_contains(word_text, ['двенадцат', 'двеннадцат']):
            return get_response_json(12, recognized_text, 0)
        if is_contains(word_text, ['тринадцат', 'триннадцат']):
            return get_response_json(13, recognized_text, 0)
        if is_contains(word_text, ['четырнадцат']):
            return get_response_json(14, recognized_text, 0)
        if is_contains(word_text, ['пятнадцат']):
            return get_response_json(15, recognized_text, 0)
        if is_contains(word_text, ['один', 'перв']):
            return get_response_json(1, recognized_text, 0)
        if is_contains(word_text, ['два', 'втор']):
            return get_response_json(2, recognized_text, 0)
        if is_contains(word_text, ['три', 'трет']):
            return get_response_json(3, recognized_text, 0)
        if is_contains(word_text, ['четыре', 'четв']):
            return get_response_json(4, recognized_text, 0)
        if is_contains(word_text, ['пять', 'пят']):
            return get_response_json(5, recognized_text, 0)
        if is_contains(word_text, ['шест']):
            return get_response_json(6, recognized_text, 0)
        if is_contains(word_text, ['восемь', 'восьм']):
            return get_response_json(8, recognized_text, 0)
        if is_contains(word_text, ['семь', 'седьм']):
            return get_response_json(7, recognized_text, 0)
        if is_contains(word_text, ['девять', 'девят']):
            return get_response_json(9, recognized_text, 0)
        if is_contains(word_text, ['десять', 'десят']):
            return get_response_json(10, recognized_text, 0)

    return get_response_json(0, recognized_text, "failed to recognize command")


if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 8000), app, keyfile='rootCA.key',
                             certfile='rootCA.cer')
    http_server.serve_forever()
