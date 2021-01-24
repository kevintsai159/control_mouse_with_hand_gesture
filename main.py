"""
Created on 1/12/2021  10:37 PM

@author: kevin
"""

import cv2
import mediapipe as mp
import pyautogui

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# pyautogui.FAILSAFE = False

# Get your main screen resolution
resolution = pyautogui.size()
screen_width = resolution.width
screen_height = resolution.height

# Load MediaPipe 'hands' model
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.9, max_num_hands=1)
cap = cv2.VideoCapture(0)  # Use the first webcam from your PC
cap.set(3, screen_width)
cap.set(4, screen_height)
cap_width = int(cap.get(3))
cap_height = int(cap.get(4))

# Set Variables
cap_boundary = 150  # Set a boundary from the edge of the frame since the hand detection accuracy is low around the edge
mouse_ptr = np.array([50, 50], dtype=np.int)  # Mouse x,y position
mouse_ptr_pre = mouse_ptr.copy()
mouse_ptr_diff = np.array([0, 0], dtype=np.int)
mouse_stable_count = 0

# Debugging
record_test_x = []
record_test_y = []

# stable mark
stable_count = 5
stable_lamda = 0.8
stable_discount = [stable_lamda]
stable_remain = 1
for i in range(stable_count - 2):
    stable_remain -= stable_discount[-1]
    stable_discount += [stable_remain * stable_lamda]
stable_discount += [1 - sum(stable_discount)]
stable_discount.reverse()
stable_ptr = []

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

    # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to pass by reference.
    image.flags.writeable = False
    results = hands.process(image)
    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        # Index fingertip pointer [x,y]
        ft_index = [results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x,
                    results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y]
        # Stabilize the pointer
        stable_ptr += [ft_index]
        stable_ptr = stable_ptr[-stable_count:]
        ft_index = [0, 0]
        for i in range(len(stable_ptr)):
            ft_index[0] += stable_ptr[-i - 1][0] * stable_discount[-i - 1]
            ft_index[1] += stable_ptr[-i - 1][1] * stable_discount[-i - 1]
        ft_index[0] += stable_ptr[-len(stable_ptr)][0] * (1 - sum(stable_discount[-len(stable_ptr):]))
        ft_index[1] += stable_ptr[-len(stable_ptr)][1] * (1 - sum(stable_discount[-len(stable_ptr):]))
        results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x = ft_index[0]
        results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y = ft_index[1]

        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        # Set a boundary for finger detection range since when hand(s) is at position near the edge,
        # hand detection accuracy drops. We have to make sure the algorithm detects the hand.
        ft_index = [min(max(ft_index[0] * cap_width - cap_boundary, 0),
                        cap_width - 2 * cap_boundary) / (cap_width - 2 * cap_boundary),
                    min(max(ft_index[1] * cap_height - cap_boundary, 0),
                        cap_height - 2 * cap_boundary) / (cap_height - 2 * cap_boundary)]
        mouse_ptr[:] = [ft_index[0] * screen_width, ft_index[1] * screen_height]
        mouse_ptr_diff += mouse_ptr - mouse_ptr_pre
        if np.where(abs(mouse_ptr - mouse_ptr_pre) > 10)[0].size == 0 and np.where(mouse_ptr_diff > 10)[0].size == 0:
            mouse_stable_count += 1
            if mouse_stable_count == 20:
                mouse_stable_count = 0
                mouse_ptr_diff[:] = [0, 0]
                # pyautogui.click(x=mouse_x, y=mouse_y)     # Mouse click
        else:
            mouse_ptr_diff[:] = [0, 0]
            mouse_stable_count = 0

        mouse_ptr_pre[:] = mouse_ptr[:]
        pyautogui.moveTo(mouse_ptr[0], mouse_ptr[1], _pause=False)

    # Show the boundary with a red rectangle
    cv2.rectangle(image, (cap_boundary, cap_boundary), (cap_width - cap_boundary, cap_height - cap_boundary),
                  color=(0, 0, 255), thickness=5)
    cv2.imshow('Hands Gesture Detection', image)
    if cv2.waitKey(1) & 0xFF == 27:
        break
hands.close()
cap.release()
