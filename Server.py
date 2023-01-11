import os

from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, request, send_file
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
    return f'{{"response": "{number}", "text": "{text}", "error": "{error}"}}'


def is_contains(operand, words):
    for word in words:
        if word in operand:
            return True
    return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/configuration/', methods=['POST', 'GET'])
def configuration():
    if request.method == 'POST':
        file = request.files['file']
        try:
            config = json.load(file.stream)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'files/config.json'), "w", encoding='utf8') as outfile:
                json.dump(config, outfile, ensure_ascii=False)
            return render_template('upload.html', result=str(config))
        except:
            return 'invalid json'

    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'files/config.json'), encoding='utf8') as jsonfile:
        grammar = json.load(jsonfile)
    return render_template('upload.html', result=str(grammar))


@app.route('/download_configuration/')
def download_configuration():
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'files/config.json'), as_attachment=True)


@app.route('/voice/', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.webm'))

    os.system(f"ffmpeg -loglevel quiet -y -i {os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.webm')} -ac 1 -f wav {os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.wav')}")

    wf = wave.open(os.path.join(app.config['UPLOAD_FOLDER'], 'audio/raw.wav'), 'rb')
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
        return get_response_json('0', '', 'invalid audio')

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

    with open('static/files/config.json', encoding='utf8') as jsonfile:
        grammar = json.load(jsonfile)

    for word in recognized_words:
        word_text = word['word']
        for key in grammar.keys():
            if is_contains(word_text, grammar[key]):
                return get_response_json(key, recognized_text, 0)

    return get_response_json('0', recognized_text, 'failed to recognize command')


if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 8000), app, keyfile='rootCA.key',
                             certfile='rootCA.cer')
    http_server.serve_forever()
