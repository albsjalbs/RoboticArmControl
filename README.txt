This Python program takes Cvzone's hand detector and serial module to send and receive data from the Arduino and uses the hand detector for input.
It will send serial data that looks something like this: $00000. If your fingers were extended, the serial input would look like $11111.
Please refer to Murtaza's video which will greatly benefit your progress in computer vision. https://www.youtube.com/watch?v=7KV5489rL3c&t=817s .
This Python code is for those with errors importing or implementing the CV zone into their project. This Python code is the same thing as importing the module but instead using source code:)
I apologize if this didn't make any sense, I am not so experienced and I am exploring the route of computer vision with some experience in Python.
For the hand itself, I have used this 3d printed hand from Thingiverse: https://www.thingiverse.com/thing:2269115.
For assembling and info about the hand: https://www.youtube.com/watch?v=O-9RETaBMVw&t=1s and https://www.youtube.com/watch?v=L2ddw3MQl9g
I have used these servo motors: https://www.amazon.com/dp/B0BZ4N367M/ref=twister_B0BZ4LVH4J?_encoding=UTF8&psc=1 and I have used a small sg90 motor for controlling the thumb
I would recommend a PSU for powering the servos as they are heavy duty and the Arduino cannot supply enough power to all of them at once.
For software you will need Arduino IDE, A python interpreter (I am using Jupyter Notebook with Anaconda), Mediapipe python package (https://pypi.org/project/mediapipe/), cvzone python package (https://pypi.org/project/cvzone/), and lastly opencv python package (https://pypi.org/project/opencv-python/). I would recommend installing the Python packages in a virtual environment using Python virtualenv (https://pypi.org/project/virtualenv/) and how to use virualenv: (https://docs.python.org/3/library/venv.html).


All thanks to Cvzone, Murtaza, and Ryan Goss for providing code and parts for this project that can make it easier for the development of this project.
Ryan Goss Youtube Channel: https://www.youtube.com/@ryangross6886
Murtaza Youtube Channel: https://www.youtube.com/@murtazasworkshop
Murtaza github: https://github.com/murtazahassan
CVzone website: https://www.computervision.zone/
CVzone github: https://github.com/cvzone/cvzone



If you have any questions please feel free to let me know by commenting on this repo and I will do the best I can to help you:)

By: Alby Jacob
