import dlib
import cv2
import numpy as np
from numpy.linalg import norm



def mid_line_distance(p1 ,p2, p3, p4):
    p5 = np.array([int((p1[0] + p2[0])/2), int((p1[1] + p2[1])/2)])
    p6 = np.array([int((p3[0] + p4[0])/2), int((p3[1] + p4[1])/2)])
    return norm(p5 - p6)
def aspect_ratio(landmarks, eye_range):
    eye = np.array(
        [np.array([landmarks.part(i).x, landmarks.part(i).y]) 
         for i in eye_range]
        )
    B = norm(eye[0] - eye[3])
    A = mid_line_distance(eye[1], eye[2], eye[5], eye[4])
    ear = A / B
    return ear


def checkBlink(number_blinks_required):
    blinks = 0
    threshold = 0.2
    eye_closed = False
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    vs = cv2.VideoCapture(1)
    print("SONO NUMERI", number_blinks_required)
    while True:
        _, frame = vs.read()
        frame = cv2.resize(frame, (600, 450))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        for rect in rects:
            landmarks = predictor(gray, rect)
            left_aspect_ratio = aspect_ratio(landmarks, range(42, 48))
            right_aspect_ratio = aspect_ratio(landmarks, range(36, 42))
            ear = (left_aspect_ratio + right_aspect_ratio) / 2.0

            if ear < threshold:
                        eye_closed = True
            elif ear >= threshold and eye_closed:
                        blinks += 1
                        
                        eye_closed = False

            for n in range(36, 48):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(frame, (x, y), 4, (255, 0, 0), -1)

            cv2.putText(frame, "Blinks: {}".format(blinks), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press a to confirm".format(ear), (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press w to reset".format(ear), (300, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) == ord ("w"):
            blinks = 0
        if cv2.waitKey(1) == ord ("a"):
            if int(blinks) == int(number_blinks_required):
                vs.release()
                cv2.destroyWindow("Frame")
                print("Exit")
                return  True
            else: 
                vs.release()
                cv2.destroyWindow("Frame")
                return False
        if cv2.waitKey(1) == ord("q"):
            vs.release()
            cv2.destroyWindow("Frame")
            return False 