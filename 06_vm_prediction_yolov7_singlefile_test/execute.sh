
#!/bin/bash

# $account = your linux account
cd /home/$account/prediction-test-yolov7/


#Step01
#python download_images.py
#/usr/bin/python3 /home/$account/prediction-test-yolov7/download_images.py
/usr/bin/python3 download_images.py
echo "download_images done."


#Step02
#python detect.py --weights best.pt --conf 0.25 --img-size 640 --source test/2303_2000-06-08.png
/usr/bin/python3 detect.py --weights best.pt --conf 0.25 --img-size 640 --source test/2303_2000-06-08.png
echo "detect storage bucket png done."


#Step03
mv runs/detect/exp/2303_2000-06-08.png runs/detect/exp/2303_2000-06-08_yolov7.png
echo "rename detect png."


#Step04
#python upload_images.py
/usr/bin/python3 upload_images.py


