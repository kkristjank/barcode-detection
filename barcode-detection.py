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
        }
    return(andmed)

print("Alustan!")

# IP kaamera(telefon)
#vs = cv2.VideoCapture('http://192.168.1.115:8080/video', cv2.CAP_DSHOW)

# Arvuti kaamera
vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Frame rate muutmine ( ei tööta )
vs.set(cv2.CAP_PROP_FPS, 10)
fps = vs.get(cv2.CAP_PROP_FPS)
print(fps)

while True:
    # loeb kaamera kaadri
    ret, frame = vs.read()
    #frame = imutils.resize(frame, width = 400)

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