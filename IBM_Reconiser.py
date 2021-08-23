from flask import Flask,request, Response,jsonify,send_file,make_response,render_template,redirect,url_for,session
import youtube_dl
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import json
import subprocess
from googletrans import Translator
import googletrans
from gtts import gTTS
import json
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

app = Flask(__name__)
app.secret_key = "your secret secret key"

apikey = "Enter your api key"
url = "Enter youe api url"

authenticator = IAMAuthenticator(apikey)
stt = SpeechToTextV1(authenticator=authenticator)
stt.set_service_url(url)

translator = Translator()
r = sr.Recognizer()

@app.route('/')
def home():
    a=googletrans.LANGUAGES
    return render_template('demo.html',sdata=a.items())

@app.route('/home')
def home1():
    a=googletrans.LANGUAGES
    return render_template('demo.html',sdata=a.items())
@app.route('/feed')
def feedback():
    return render_template('demo4.html')

@app.route('/about')
def about():
    return render_template('demo5.html')


def get_large_audio_transcription():
    command = 'ffmpeg -i song.m4a -vn -ar 44100 -ac 2 -b:a 192k -y song.mp3'
    subprocess.call(command,shell=True)
    results = []
    with open('./song.mp3' , 'rb') as f:
        res = stt.recognize(audio =f, content_type='audio/mp3' , model='en-US_BroadbandModel', continuous=True, \
                            inactivity_timeout=180).get_result()
        results.append(res)
    text = []
    for file in results:
        for result in file['results']:
            text.append(result['alternatives'][0]['transcript'].rstrip())
    print("text :",text)
    whole_text=' '.join([str(item) for item in text if item !='[' or item !=']' ])
    print("whole_text :",whole_text)
    if session['lang'] == 'en' or session['lang'] == 'english':
        return whole_text
    else:
        t = translator.translate(whole_text,src='en',dest=session['lang'])
        print('google text ',t.text)
        return t.text

@app.route('/ekl',methods=['POST','GET'])
def download():
    f = session['f']
    t=session['t']
    if f == 'voice':
        mytext = t
        language = session['lang']
        myobj = gTTS(text=mytext,slow=True)
        myobj.save("welcome.mp3")
        resp = make_response(send_file("./welcome.mp3", mimetype='audio/wav', as_attachment=True, attachment_filename="converted.mp3"))
        return resp
    elif f == 'text':
        res = Response(t,mimetype="text/csv",headers={"Content-disposition":"attachment; filename=converted.txt"})
        return res

def get_mp3(url):
  try:
    os.remove('song.m4a')
  except:
    pass  
  file_name = "song.m4a"
  options = {'format': 'bestaudio/best','keepvideo': False,'outtmpl': file_name,'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'm4a','preferredquality': '192',}]}
  with youtube_dl.YoutubeDL(options) as download:
    download.download([url])
  return file_name

@app.route('/down',methods=['POST','GET'])
def down():
    url = session['url']
    mp3_file_name = get_mp3(url)
    t=get_large_audio_transcription()
    session['t']=t
    return jsonify(t)

@app.route('/audio', methods=['POST','GET'])
def download_mp3():
    session['url'] = request.form['link']
    session['f'] = request.form['for']
    session['lang'] = request.form['lang']
    return render_template('demo3.html')

if __name__ == '__main__':
    app.run(debug=True)
