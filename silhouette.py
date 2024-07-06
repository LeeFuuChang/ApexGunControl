import cv2
import sys
import os


def silhouettilize(img):
    # crop region
    w = img.shape[1]
    h = img.shape[0]
    b = h//6
    img = img[h-b:h,w-b*3:w]

    # resize region
    defaultB = 1080 // 6
    img = cv2.resize(img, (defaultB*3, defaultB), interpolation=cv2.INTER_NEAREST)

    # crop weapon
    cx = 156
    cy = 60
    cw = 176
    ch = 48
    img = img[cy:cy+ch,cx:cx+cw]

    # grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # binarization
    img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)[1]

    # masking
    img[img.shape[0]- 3:img.shape[0], 0              :88          ] = 0
    img[img.shape[0]-10:img.shape[0], img.shape[1]-42:img.shape[1]] = 0

    # output
    return img


if __name__ == "__main__":
    if(len(sys.argv) > 1):
        # read
        img = cv2.imread(sys.argv[1])

        # silhouettilize
        img = silhouettilize(img)

        # saving
        cv2.imwrite(os.path.join("ApexGunControl-LS", "apex", "silhouettes", sys.argv[1]), img)