raspistill
raspistill -o cam.jpg


sox -t alsa plughw:1 listeningnow.wav

raspivid -o - -t 0 -hf -w 640 -h 360 -fps 25 | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554}' :demux=h264