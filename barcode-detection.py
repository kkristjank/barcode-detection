from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2
import pymongo

# Andmebaasiga ühendamine
myclient = pymongo.MongoClient("mongodb://localhost:27017")
db = myclient["Andmed"]
col = db["Barcodes"]

# Info, mis salvestatakse andmebaasi
def tulemus():
    andmed = {
        "Info":barcodeData,
        "Type":barcodeType,
        "Time":barcodeTime,
        }
    return(andmed)

print("Alustan!")

# IP kaamera(telefon)
#vs = cv2.VideoCapture('http://192.168.213.8:8080/video')

# Arvuti kaamera
vs = cv2.VideoCapture(0)

# FPS määramine
frame_rate = 10
prev_time = 0

while True:
    time_elapsed = time.time() - prev_time
    
    # loeb kaamera kaadri
    ret, frame = vs.read()
    frame = imutils.resize(frame, width = 200)
    
    if time_elapsed > 1./frame_rate:
        prev_time = time.time()
        print(time_elapsed)

        # QR- ja võõtkoodi dekooder
        barcodes = pyzbar.decode(frame)
        
        for barcode in barcodes:
            # QR- või võõtkoodi info
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            # Kuvab videoedastusel olevale QR- või võõtkoodile kasti ümber
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Kasti ülesse kuvab QR- või võõtkoodi info
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # QR- või võõtkoodi tuvastamise aeg
            barcodeTime = time.localtime()
            barcodeTime = time.strftime("%Y-%m-%d %H:%M:%S", barcodeTime)

            # Salvestab vastuvõetud info andmebaasi
            if col.count_documents({"Info": barcodeData}) > 0:
                print("Olemas!")
            else:
                save = col.insert_one(tulemus())
                print("Uus info lisatud!")

    # Edastab pildi
    cv2.imshow("Barcode Scanner", frame)

    # Kui vajutada q tähte, lõpetab video edastuse
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# Lõpetab video edastuse
print("Lõpetan!")
cv2.destroyAllWindows()
vs.release()
