# theHound
![theHoudPicture](./Images/CarPhoto.png)

## Introduction

This is an autonomous system capable of recognizing and follow arbitrary objects in the space surrounding the system, using modern embedded technologies and computer vision techniques.

The system is of small dimension , low energy consumption and reduced production costs. The small dimension allow the system to be autonomous and to be integrated in more complex projects, making it, at the same time, easily transportable and of simple usage.
A long autonomy is fundamental for a continuous and intensive usage, in fact, a lot of attention was directed to energy consumption.

Finally the reduced costs make this system a platform accessible to many more users than many production systems available on the market.

From a single input image, representing an object, the system is capable of extracting the necessary information for the following elaboration of a continuous stream of images captured from the integrated frontal camera. With the results of this elaboration the system can estimate and predict the position of the object (if present) in the surrounding space and operate the supplied actuators to track and follow the object.

## Software implementation

## The construction

## The workflow

## Requirements

### Hardware & Materials
- An Arduino Uno
- A RaspberryPi (v2 or v3)
- An iPhone (to control it otherwise it can work also on his own using ssh and a terminal)

And this material:
![Materials](./Images/Tools.png)

### Software

#### Arduino

| Library        | Verison        |
| -------------- |:--------------:|
|**ArduinoJson** |    >= 5.8.0    |
|**AFMotor**     |    >= 1.0.0    |

#### RaspberryPi

Any Debian based OS distribution should be fine.

| Software       | Verison        |
| -------------- |:--------------:|
| **Python**     |     >= 3.5     |
| **OpenCV**     |    == 3.1.0    |
| **Numpy**      |    >= v1.10    |
| **picamera**   |    >= 1.10     |
| **serial**     |    >= 0.0.20   |

#### iPhone

| Software       | Verison        |
| -------------- |:--------------:|
| **iOS**        |    >= iOS 10   |
| **Swift**      |   >= Swift 3   |

## License

Licensed under the term of [MIT License](http://en.wikipedia.org/wiki/MIT_License). See attached file LICENSE.
