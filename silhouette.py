import cv2
import sys
import os

# read
img = cv2.imread(sys.argv[1])

# crop
cx = 1536
cy = 960
cw = 176
ch = 48
img = img[cy:cy+ch,cx:cx+cw]

# grayscale
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# binarization
img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)[1]

# masking
mx = [0 , 134]
my = [45, 38 ]
mw = [88, 42 ]
mh = [3 , 10 ]
for x, y, w, h in zip(mx, my, mw, mh):
    img[y:y+h,x:x+w] = 0

# saving
cv2.imwrite(os.path.join("ApexGunControl-LS", "apex", "silhouettes", sys.argv[1]), img)