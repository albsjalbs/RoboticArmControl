import math
import cv2
import mediapipe as mp
import cvzone
from cvzone.SerialModule import SerialObject
import serial
import logging
import serial.tools.list_ports

class SerialObject:
    """
    Allow to transmit data to a Serial Device like Arduino.
    Example send $255255000
    """

    def __init__(self, portNo="COM6", baudRate=9600, digits=1, max_retries=5):
        """
        Initialize the serial object.

        :param portNo: Port Number
        :param baudRate: Baud Rate
        :param digits: Number of digits per value to send
        :param max_retries: Maximum number of retries to connect
        """
        self.portNo = portNo
        self.baudRate = baudRate
        self.digits = digits
        self.max_retries = max_retries

        if self.portNo is None:
            for retry_count in range(1, self.max_retries + 1):
                print(f"Attempt {retry_count} of {self.max_retries} to connect...")
                connected = False
                ports = list(serial.tools.list_ports.comports())
                for p in ports:
                    if "Arduino" in p.description:
                        print(f'{p.description} Connected')
                        self.ser = serial.Serial(p.device)
                        self.ser.baudrate = baudRate
                        connected = True
                        break
                if connected:
                    break
                else:
                    print(f"Attempt {retry_count} failed. Retrying...")

            if not connected:
                logging.warning("Arduino Not Found. Max retries reached. Please enter COM Port Number instead.")
        else:
            for retry_count in range(1, self.max_retries + 1):
                print(f"Attempt {retry_count} of {self.max_retries} to connect...")
                try:
                    self.ser = serial.Serial(self.portNo, self.baudRate)
                    print("Serial Device Connected")
                    break
                except:
                    print(f"Attempt {retry_count} failed. Retrying...")
                    if retry_count >= self.max_retries:
                        logging.warning("Serial Device Not Connected. Max retries reached.")

    def sendData(self, data):
        """
        Send data to the Serial device
        :param data: list of values to send
        """
        myString = "$"
        for d in data:
            myString += str(int(d)).zfill(self.digits)
        try:
            self.ser.write(myString.encode())
            return True
        except:
            return False

    def getData(self):
        """
        Retrieve data from the serial device.

        :return: list of data received, or None if an error occurred
        """
        try:
            data = self.ser.readline()
            data = data.decode("utf-8")
            data = data.split('#')
            dataList = []
            [dataList.append(d) for d in data]
            return dataList[:-1]
        except serial.SerialException as se:
            logging.error(f"SerialException: {se}")
        except UnicodeDecodeError as ude:
            logging.error(f"UnicodeDecodeError: {ude}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        return None



    
class HandDetector:
    """
    Finds Hands using the mediapipe library. Exports the landmarks
    in pixel format. Adds extra functionalities like finding how
    many fingers are up or the distance between two fingers. Also
    provides bounding box info of the hand found.
    """

    def __init__(self, staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5):

        """
        :param mode: In static mode, detection is done on each image: slower
        :param maxHands: Maximum number of hands to detect
        :param modelComplexity: Complexity of the hand landmark model: 0 or 1.
        :param detectionCon: Minimum Detection Confidence Threshold
        :param minTrackCon: Minimum Tracking Confidence Threshold
        """
        self.staticMode = staticMode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.staticMode,
                                        max_num_hands=self.maxHands,
                                        model_complexity=modelComplexity,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)

        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []

    def findHands(self, img, draw=True, flipType=True):
        """
        Finds hands in a BGR image.
        :param img: Image to find the hands in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                ## lmList
                mylmList = []
                xList = []
                yList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)

                ## bbox
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), \
                         bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                if flipType:
                    if handType.classification[0].label == "Right":
                        myHand["type"] = "Left"
                    else:
                        myHand["type"] = "Right"
                else:
                    myHand["type"] = handType.classification[0].label
                allHands.append(myHand)

                ## draw
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (255, 0, 255), 2)
                    cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                                2, (255, 0, 255), 2)

        return allHands, img

    def fingersUp(self, myHand):
        """
        Finds how many fingers are open and returns in a list.
        Considers left and right hands separately
        :return: List of which fingers are up
        """
        fingers = []
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]
        if self.results.multi_hand_landmarks:

            # Thumb
            if myHandType == "Right":
                if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img=None, color=(255, 0, 255), scale=5):
        """
        Find the distance between two landmarks input should be (x1,y1) (x2,y2)
        :param p1: Point1 (x1,y1)
        :param p2: Point2 (x2,y2)
        :param img: Image to draw output on. If no image input output img is None
        :return: Distance between the points
                 Image with output drawn
                 Line information
        """

        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), scale, color, cv2.FILLED)
            cv2.circle(img, (x2, y2), scale, color, cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), color, max(1, scale // 3))
            cv2.circle(img, (cx, cy), scale, color, cv2.FILLED)

        return length, info, img


def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)
    mySerial = SerialObject(portNo="COM6", baudRate=9600, digits=1, max_retries=10)

    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)
        if hands:
            hand1= hands[0]
            lmList1 = hand1["lmList"]
            bbox1 = hand1["bbox"]
            centerPoint1 = hand1["center"]
            handType = hand1["type"]
            fingers1 = detector.fingersUp(hand1)
            mySerial.sendData(fingers1)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
        
if __name__ == "__main__":
    main()
