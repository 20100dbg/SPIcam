from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import datetime

import pyaudio
import wave
import config
import mail



def log(mystr):
	with open("log/spicam.log", "a") as log:
		log.write("["+ str(datetime.datetime.now()) +"] " + mystr + "\n")

def callback(in_data, frame_count, time_info, status):
	frames.append(in_data)
	return (in_data, pyaudio.paContinue)

#init audio
p = pyaudio.PyAudio()
frames = []
stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024, stream_callback=callback)


starttime = datetime.datetime.now()
gdhLastDetect = ""
detected = False
cPicture = 0
cFrame = 0
mailsent = False

#args
videoFile = "" #"test.avi"
min_area = 2000 #defaut : 500

if videoFile == "":
	#vs = VideoStream(src=0).start()
	#time.sleep(2.0)
	
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

		if not detected:
			#init video writer
			writer = cv2.VideoWriter('data/output.avi',cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640,480))
			stream.start_stream()
			detected = True
			log("Init videowriter + audio")
		
		gdhLastDetect = datetime.datetime.now()
		cFrame += 1

		if not mailsent:
			
			if cFrame % 50 == 0 and cPicture <= config.CONF['nb_picture']:
				cPicture += 1
				cv2.imwrite('images/image-'+ str(cPicture) +'.jpg', frame)
				log("Save picture " + str(cPicture))

			if cPicture == config.CONF['nb_picture']:
				mail.sendmail(True)
				mailsent = True
				log("Envoi mail debut intrusion")
	
	elif detected:
		delta = gdhLastDetect + datetime.timedelta(seconds=config.CONF['detect_timeout'])
		
		if datetime.datetime.now() > delta:
			mail.sendmail(False)
			log("Envoi mail fin intrusion")
			
			detected = False
			mailsent = False
			cFrame = 0
			writer.release()
			stream.stop_stream()
			log("Fermeture video writer et stream audio")


	if text == "Occupied" or detected:
		if writer: 
			cv2.putText(origFrame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, origFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
			writer.write(origFrame)


	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	
	# show the frame and record if the user presses a key
	cv2.imshow("Security Feed", frame)
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", frameDelta)

	key = cv2.waitKey(1) & 0xFF
	# if the `q` key is pressed, break from the lop

	if key == ord("q"):
		break
	
	if datetime.datetime.now() > starttime + datetime.timedelta(seconds=60):
		log("Fin du timer")
		break

# cleanup the camera and close any open windows
#vs.stop() if videoFile == "" else vs.release()
vs.release()
cv2.destroyAllWindows()

stream.close()
p.terminate()
log("Ressources fermées")

waveFile = wave.open("data/audio.wav", 'wb')
waveFile.setnchannels(2)
waveFile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
waveFile.setframerate(44100)
waveFile.writeframes(b''.join(frames))
waveFile.close()

log("Fichier son enregistré")

