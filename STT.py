import speech_recognition as sr

audio = 'in.wav'

class SpeachRecognition:
	def __init__(self):
		self.r = sr.Recognizer()
		
		self.LANG = "ru-RU"
		self.TEXT = ""
	def extract(self, audiof):
		with sr.AudioFile(audiof) as source:
			audio = self.r.record(source)
			print ('Done! ', audiof)
		
		try:
			text = self.r.recognize_google(audio, language=self.LANG)
			#print (text)
			self.TEXT += text + "\n"
		except Exception as e:
			print ("Err: ", e)

			
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox,
	QInputDialog, QLineEdit, QFileDialog, QLabel, QPushButton, QFormLayout)
from PyQt5.QtGui import QIcon
import codecs

class App(QWidget):
	def __init__(self):
		super().__init__()
		
		self.title = 'Speach To Text'
		self.left = 100
		self.top = 100
		self.width = 250
		self.height = 50
		
		self.sr = SpeachRecognition()
		self.files = []
		self.DBFS = -45
		self.PAUSE = 100
		
		self.initUI()
	
	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
	
		self.lOpen = QLabel("Open audio files")
		self.lSave = QLabel("Save text")
		self.lLang = QLabel("Speech language")
		self.lExtract = QLabel("Extract text")
		self.lPause = QLabel("Pause")
		self.lDBFS = QLabel("DBFS")
		self.btnOpen = QPushButton("Open")
		self.btnOpen.setToolTip("Open files")
		self.btnOpen.clicked.connect(self.openFileNamesDialog)
		self.btnSave = QPushButton("Save")
		self.btnSave.setToolTip("Save text")
		self.btnSave.clicked.connect(self.saveFileDialog)
		self.btnExtract = QPushButton("Extract")
		self.btnExtract.setToolTip("Extract text")
		self.btnExtract.clicked.connect(self.extractText)
		self.comboLang = QComboBox(self)
		self.comboLang.addItems(["RU", "EN"])
		self.comboLang.currentIndexChanged.connect(self.changeLang)
		
		self.editPause = QLineEdit(self)
		self.editPause.textChanged[str].connect(self.onChangedPause)
		self.editPause.setText(str(self.PAUSE))
		self.editDBFS = QLineEdit(self)
		self.editDBFS.textChanged[str].connect(self.onChangedDBFS)
		self.editDBFS.setText(str(self.DBFS))
		
		self.grid = QFormLayout()
		self.grid.setSpacing(10)
	
		self.grid.addRow(self.lOpen, self.btnOpen)
		self.grid.addRow(self.lSave, self.btnSave)
		self.grid.addRow(self.lLang, self.comboLang)
		self.grid.addRow(self.lExtract, self.btnExtract)
		self.grid.addRow(self.lPause, self.editPause)
		self.grid.addRow(self.lDBFS, self.editDBFS)
		self.setLayout(self.grid)
		self.show()
	
	def onChangedPause(self, text):
		try:
			self.PAUSE = int(text)
		except ValueError:
			print("")
	def onChangedDBFS(self, text):
		try:
			self.DBFS = int(text)
		except ValueError:
			print("")
	
	def openFileNamesDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
		if files:
			#print(files)
			self.files = files
	
	def saveFileDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
		if fileName:
			#print("Save: ", fileName)
			STXTfile = codecs.open(fileName, "w", 'utf-8')
			STXTfile.write(self.sr.TEXT)
			STXTfile.close()
	
	def extractText(self):
		self.sr.TEXT = ""
		import os
		from pydub import AudioSegment
		from pydub.silence import split_on_silence
		
		i = 0
		for f in self.files:
			sound_file = AudioSegment.from_wav(f)
			chunks = split_on_silence(sound_file, 
				# must be silent for at least half a second
				min_silence_len=self.PAUSE,
				# consider it silent if quieter than -16 dBFS
				silence_thresh=self.DBFS
			)
			
			target_length = 8 * 1000
			output_chunks = [chunks[0]]
			
			for chunk in chunks[1:]:
				if len(output_chunks[-1]) < target_length:
					output_chunks[-1] += chunk
				else:
					if i <= 9:
						n = "0" + str(i)
					else:
						n = "" + str(i)
					out_file = "./data/chunk"+n+".wav"
					print("chunk: ", out_file)
					output_chunks[-1].export(out_file, format="wav")
					i+=1
					output_chunks.append(chunk)
			if i <= 9:
				n = "0" + str(i)
			else:
				n = "" + str(i)
			out_file = "./data/chunk"+n+".wav"
			print("chunk: ", out_file)
			output_chunks[-1].export(out_file, format="wav")
	
		fs = os.listdir("./data/")
		print(fs)
		for f in fs:
			self.sr.extract("./data/"+f)
	
	def changeLang(self, i):
		if self.comboLang.currentText() == 0:
			self.sr.LANG = "ru-RU"
		elif  self.comboLang.currentText() == 1:
			self.sr.LANG = "en-US"
	
	
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())