"""
Created on 1/12/2021  10:37 PM

@author: kevin
"""

import cv2
import mediapipe as mp
import pyautogui

resolution = pyautogui.size()
screen_width = resolution.width
screen_height = resolution.height

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)
cap_width = cap.get(3)
cap_height = cap.get(4)
mouse_x = 50
mouse_y = 50
mouse_x_pre = 50
mouse_y_pre = 50
mouse_count = 0
mouse_avg_x = 0
mouse_avg_y = 0
mouse_avg_x_move = 0
mouse_avg_y_move = 0
mouse_locations = []
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        finger_x = min(max(results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x, 0), 1)
        finger_y = min(max(results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y, 0), 1)
        mouse_x = finger_x * screen_width
        mouse_y = finger_y * screen_height
        mouse_avg_x_move += mouse_x - mouse_x_pre
        mouse_avg_y_move += mouse_y - mouse_y_pre
        if abs(mouse_x - mouse_x_pre) <= 10 and abs(mouse_y - mouse_y_pre) <= 10 and mouse_avg_x_move<=10 and mouse_avg_y_move<=10:
            mouse_count += 1
            if mouse_count == 20:
                mouse_count = 0
                pyautogui.click(x=mouse_x, y=mouse_y)
                mouse_avg_x_move = 0
                mouse_avg_y_move = 0
        else:
            mouse_avg_x_move = 0
            mouse_avg_y_move = 0
            mouse_count = 0
        print(mouse_count, mouse_avg_x_move, mouse_avg_y_move)
        mouse_x_pre = mouse_x
        mouse_y_pre = mouse_y
        pyautogui.moveTo(mouse_x, mouse_y, _pause=False)

    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(1) & 0xFF == 27:
        break
hands.close()
cap.release()
