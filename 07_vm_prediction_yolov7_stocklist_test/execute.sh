
#!/bin/bash

# $account = your linux account
cd /home/$account/prediction-test-yolov7-final/


# Step01
# python download_images.py
/usr/bin/python3 download_images.py
echo "run download_images.py done!"


# Step02
#python detect.py --weights best.pt --conf 0.25 --img-size 640 --source originalimages
/usr/bin/python3 detect.py --weights best.pt --conf 0.25 --img-size 640 --source originalimages
echo "run detect.py done!"


# Step03
#python upload_images.py
/usr/bin/python3 upload_images.py
echo "run upload_images.py done!"
