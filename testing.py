"""
Created on 1/12/2021  10:40 PM

@author: kevin
"""
import pyautogui, sys

# print('Press Ctrl-C to quit.')
# try:
#     while True:
#         x, y = pyautogui.position()
#         positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
#         print(positionStr, end='')
#         print('\b' * len(positionStr), end='', flush=True)
# except KeyboardInterrupt:
#     print('\n')

# pyautogui.moveTo(100, 100, 2, pyautogui.easeInElastic)

x = 10
for i in range(100):
    x += 10
    pyautogui.moveTo(x, 35,_pause=False)

# resolution = pyautogui.size()
# print(resolution.width,resolution.height)
