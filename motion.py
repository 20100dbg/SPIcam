from imutils.video import VideoStream
import imutils, cv2
import datetime, time
import pyaudio, wave
import config, mail
import os, glob


def check_internet():
	try:
		#host = socket.gethostbyname("one.one.one.one")
		s = socket.create_connection(("1.1.1.1", 80), 2)
		s.close()
		return True
	except:
		pass
	return False


def saveWave(frames):
	waveFile = wave.open("data/"+ getStrTime() +"_audio.wav", 'wb')
	waveFile.setnchannels(2)
	waveFile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
	waveFile.setframerate(44100)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()

def getStrTime(dayOnly = False):
	myfilter = "%Y%m%d"	if dayOnly else "%Y%m%d_%H%M"
	return datetime.datetime.now().strftime(myfilter) 

def log(mystr, writeConsole = True):	
	mystr = "["+ datetime.datetime.now().strftime("%Y%m%d_%H%M%S") +"] " + mystr
	
	if writeConsole:
		print(mystr)

	with open("log/"+ getStrTime(True) +"_spicam.log", "a") as log:
		log.write(mystr + "\n")


def callback(in_data, frame_count, time_info, status):
	frames.append(in_data)
	return (in_data, pyaudio.paContinue)

#clean dossier data + images
def clean(fData = True, fImages = True):
	if fData:
		files = glob.glob('./data/*')
		for f in files:
			os.remove(f)
	
	if fImages:
		files = glob.glob('./images/*')
		for f in files:
			os.remove(f)


log("Script started")

with open("work", "r") as f:
	if f.read() != "1":
		log("!!! work file != 1")

log("internet access ok") if check_internet() else log("internet access failed")

time.sleep(config.CONF['wait_start'])

#init audio
p = pyaudio.PyAudio()
frames = []
stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024, stream_callback=callback)
log("Audio initialized")

starttime = datetime.datetime.now()
gdhLastDetect, gdhBeginWatching, gdhLastPicture = "", "", ""
mailsent, watching = False, False
cPicture, cFrame = 0, 0

videoFile = "" #"test.avi"
min_area = 1000 #defaut : 500

if videoFile == "":
	vs = cv2.VideoCapture(0)
	time.sleep(2.0)
	#vs.set(3,640)
	#vs.set(4,480)
else:
	vs = cv2.VideoCapture(videoFile)


# initialize the first frame in the video stream
firstFrame = None

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied text
	time.sleep(0.1)

	ret, frame = vs.read()
	frame = frame if videoFile == "" else frame[1]
	text = "Unoccupied"

	# if the frame could not be grabbed, then we have reached the end of the video
	if frame is None:
		break

	# resize the frame, convert it to grayscale, and blur it
	origFrame = frame
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue

	# compute the absolute difference between the current frame and first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
	
	# dilate the thresholded image to fill in holes, then find contours on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	
	# loop over the contours
	for c in cnts:
		if cv2.contourArea(c) < min_area:
			continue
	
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"


	if text == "Occupied":

		gdhLastDetect = datetime.datetime.now()
		cFrame += 1

		if not watching:
			#init video writer
			watching = True
			writer = cv2.VideoWriter('data/'+ getStrTime() +'_video.avi',cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640,480))
			stream.start_stream()

			gdhBeginWatching = datetime.datetime.now()
			gdhLastPicture = datetime.datetime.now()
			log("Init videowriter + audio")


		if not mailsent:
			
			delta = gdhBeginWatching + datetime.timedelta(seconds=config.CONF['delay_first_picture'])
			if datetime.datetime.now() > delta:

				delta = gdhLastPicture + datetime.timedelta(seconds=config.CONF['delay_between_picture'])
				if datetime.datetime.now() > delta:

					if cPicture <= config.CONF['nb_picture']:
						cPicture += 1
						cv2.imwrite('images/image-'+ str(cPicture) +'.jpg', frame)
						log("Save picture " + str(cPicture))
						gdhLastPicture = datetime.datetime.now()

			if cPicture == config.CONF['nb_picture']:
				mail.sendmail(True)
				mailsent = True
				log("Envoi mail debut intrusion")
				clean(False, True)
	
	elif watching:
		delta = gdhLastDetect + datetime.timedelta(seconds=config.CONF['detect_timeout'])
		
		if datetime.datetime.now() > delta:
			mail.sendmail(False)
			log("Envoi mail fin intrusion")
			
			watching, mailsent = False, False
			cFrame, cPicture = 0,0
			writer.release()
			stream.stop_stream()
			saveWave(frames)
			log("Fichier son enregistre")
			frames = []
			log("Fermeture video writer et stream audio")


	if text == "Occupied" or watching:
		if writer: 
			cv2.putText(origFrame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, origFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
			writer.write(origFrame)


	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	
	# show the frame and record if the user presses a key
	#cv2.imshow("Security Feed", origFrame)
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", frameDelta)
	
	#if datetime.datetime.now() > starttime + datetime.timedelta(seconds=60):
	#	log("Fin du timer")
	#	break

	with open("work", "r") as f:
		if f.read() != "1":
			break



# cleanup the camera and close any open windows
#vs.stop() if videoFile == "" else vs.release()
vs.release()
cv2.destroyAllWindows()

stream.close()
p.terminate()
log("Ressources fermees")

