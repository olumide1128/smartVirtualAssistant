# Import required modules
import pyttsx3
import time
import speech_recognition as sr
import os
import screen_brightness_control as sbc
from string import punctuation
from pynput.keyboard import Key, Controller
import json
import requests
import base64
import wave
import pyaudio
  

  
# Creating class
class Main:
    
	def __init__(self):
		print("Starting AI up....")
		print()

		#Setting Up
		self.engine = pyttsx3.init('sapi5')

		#self.rate = self.engine.getProperty('rate')

		self.engine.setProperty('rate', 125)

		self.voices = self.engine.getProperty('voices')
		self.engine.setProperty('voice', self.voices[1].id) 

		#variables
		self.Query = ""

		#Add one or more paths to your vid directory
		#e.g [c:/Users/John/Videos]
		self.vidpath = []

		self.audioFilePath = "audioFiles/file.wav"
		self.shazamAPIresponse = {}


	# Method to give output commands
	def Speak(self, audio):
	    
	    self.engine.say(audio)
	    self.engine.runAndWait()
	  

	# Method to take input voice commands
	def takeCommand(self):

		# This method is for taking 
		# the commands and recognizing the command

		r = sr.Recognizer()
	    # from the speech_Recognition module 
	    # we will use the recongizer method 
	    # for recognizing
	    
		with sr.Microphone() as source:
		    # from the speech_Recognition module 
		    # we will use the Microphone module for 
		    # listening the command

		    print('Listening')
		    # seconds of non-speaking audio 
		    # before a phrase is considered complete
		    #r.pause_threshold = 1
		    r.adjust_for_ambient_noise(source)
		    print("Say something..")
		    audio = r.listen(source)

		    try:
		        print("Recognizing")
		        self.Query = r.recognize_google(audio, language='en-us')

		        # for listening the command 
		        # in indian english
		        print(f"the query is printed={self.Query}")

		        # for printing the query or the 
		        # command that we give
		    except Exception as e:

		        # this method is for handling 
		        # the exception and so that 
		        # assistant can ask for telling 
		        # again the command
		        print(e)
		        self.checkForWakeWord()


	def removePunc(self, text):
		for char in text:
			if char in punctuation:
				text = text.replace(char, "")

		return text 

	def vidFound(self):
		for path in self.vidpath:
			for resource in os.listdir(path):
				if resource.lower().endswith(".mp4") or resource.lower().endswith(".mkv"):
					if self.Query.lower() in self.removePunc(resource).lower():
						fullPath = os.path.join(path, resource)
						os.startfile(fullPath)

						time.sleep(3)
						keyboard = Controller()  

						keyboard.press("F")
						keyboard.release("F")

						return True

		return False


	def playVid(self):
		self.Speak("Which video should i play for you Boss?")
		self.takeCommand()

		if self.vidFound():
			self.Speak(f"Playing Video, {self.Query}")
			self.checkForWakeWord()
		else:
			self.Speak(f"Video not found! Do you want to play another one boss?")
			self.takeCommand()

			try:
				if "yes" in self.Query.lower():
					self.playVid()
				elif "no" in self.Query.lower():
					self.Speak("Okay Boss. I'm a call away!")
					self.checkForWakeWord()
				else:
					self.takeCommand()

			except Exception as e:
				print(e)
				self.takeCommand()



	def endVid(self):
		self.Speak("Okay Boss. Stopping Video!")

		time.sleep(3)
		control = Controller()  

		#event
		with control.pressed(Key.alt):
			control.press(Key.f4)

		self.Speak("Video Stopped Boss!")
		self.checkForWakeWord()


	def getAudioSample(self):

		# Setup channel info
		FORMAT = pyaudio.paInt16 # data type formate
		CHANNELS = 1 # Adjust to your number of channels
		RATE = 44100 # Sample Rate
		CHUNK = 1024 # Block Size
		RECORD_SECONDS = 5 # Record time
		WAVE_OUTPUT_FILENAME = self.audioFilePath

		# Startup pyaudio instance
		audio = pyaudio.PyAudio()

		# start Recording
		stream = audio.open(format=FORMAT, channels=CHANNELS,
		            rate=RATE, input=True,
		            frames_per_buffer=CHUNK)
		print("recording...")
		frames = []

		# Record for RECORD_SECONDS
		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
			data = stream.read(CHUNK)
			frames.append(data)
		
		print("finished recording")



		# Stop Recording
		stream.stop_stream()
		stream.close()
		audio.terminate()

		# Write your new .wav file with built in Python 3 Wave module
		waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
		waveFile.setnchannels(CHANNELS)
		waveFile.setsampwidth(audio.get_sample_size(FORMAT))
		waveFile.setframerate(RATE)
		waveFile.writeframes(b''.join(frames))
		waveFile.close()


	def matchFound(self):
		url = "https://shazam.p.rapidapi.com/songs/detect"

		payload = ""
		headers = {
		    'content-type': "text/plain",
		    'x-rapidapi-key': "--Put your rapidapi key here--",
		    'x-rapidapi-host': "shazam.p.rapidapi.com"
		    }

		path = self.audioFilePath
		#Get base64 String from audio
		with open(path, 'rb') as binary_file:
		        binary_file_data = binary_file.read()
		        encodedData = base64.b64encode(binary_file_data).decode('utf-8')
		        payload = encodedData


		response = requests.post(url, data=payload, headers=headers)

		responseDict = response.json()
		#Delete audio File After getting response
		os.remove(path)

		if len(responseDict['matches']) > 0:
			self.shazamAPIresponse = responseDict['track']
			return True

		else:
			return False 


	def findSong(self):
		self.Speak("Listening to song and trying to find a match boss!")
		self.getAudioSample()

		if self.matchFound():
			artiste_name = self.shazamAPIresponse['subtitle'].replace(" Feat. ", " Featuring ")
			song = self.shazamAPIresponse['title']
			print(artiste_name)
			print(song)

			self.Speak(f"Name of song is {song} by {artiste_name}")
			self.shazamAPIresponse = {}
			self.checkForWakeWord()

		else:
			self.Speak("No match found for song Boss! Do you want to check another song?")
			self.takeCommand()
			try:
				if 'yes' in self.Query.lower():
					self.Speak("Okay Boss!")
					self.findSong()
				elif 'no' in self.Query.lower():
					self.Speak("Okay Boss. I'm a call away!")
					self.checkForWakeWord()
				else:
					self.takeCommand()

			except Exception as e:
				print(e)
				self.takeCommand()



	def checkForWakeWord(self):

		self.takeCommand()

		try:
			if self.Query != "" and 'spiky' in self.Query.lower():
				self.Speak("Yes Boss, how may i help you?")
				self.bootspiky()
			else:
		    	#Do nothing
				self.checkForWakeWord()

		except Exception as e:
			print(e)
			self.checkForWakeWord()




	def bootspiky(self):


		self.takeCommand()
		
		try:
			if 'shutdown' in self.Query.lower():
				self.process('shutdown')

			elif 'restart' in self.Query.lower():
			    self.process('restart')

			elif 'reduce' in self.Query.lower():
				self.process('reduce')

			elif 'increase' in self.Query.lower():
				self.process('increase')

			elif 'play video' in self.Query.lower() or 'play me a video' in self.Query.lower() or 'play a video' in self.Query.lower():
				self.process('playvideo')

			elif 'end' in self.Query.lower() or 'stop' in self.Query.lower() or 'stop video' in self.Query.lower():
				self.process('endVideo')

			elif 'what song' in self.Query.lower() or 'what is' in self.Query.lower() and 'song' in self.Query.lower():
				self.process('findSong')

			elif 'thanks' in self.Query.lower():
			    self.process('thanks')
			else:
				self.bootspiky()

		except Exception as e:
			print(e)
			self.bootspiky()


    # Method to restart PC
	def process(self, speech):

	    if speech == 'shutdown':
	        self.Speak("Okay Boss, Shutting down the computer")
	        print("Shutting down the computer")
	        os.system("shutdown /s /t 5")
	        
	    if speech == 'restart':
	        self.Speak("Okay Boss, Restarting the Computer!")
	        print("Restarting the Computer!")
	        os.system("shutdown /r /t 5")

	    if speech == 'reduce':
	        self.Speak("Okay Boss, reducing the brightness of the screen")
	        print("Reducing the brightness")
	        sbc.set_brightness('-10')
	        self.checkForWakeWord()
	    
	    if speech == 'increase':
	        self.Speak("Okay Boss, increasing the brightness of the screen")
	        print("increasing the brightness")
	        sbc.set_brightness('+10')
	        self.checkForWakeWord()

	    if speech == 'playvideo':
	        self.playVid()

	    if speech == 'endVideo':
	    	self.endVid()

	    if speech == 'findSong':
	    	self.findSong()

	    if speech == 'thanks':
	        self.Speak("Okay Boss. I'm a call away!")
	        print("Okay Mr Olu me day. I'm a call away!")
	        self.checkForWakeWord()
            
  
  

# Driver Code
if __name__ == '__main__':
    x = Main()
    #x.restart()
    x.Speak("Welcome back Boss. I am with you 2 4 7")
    x.checkForWakeWord()