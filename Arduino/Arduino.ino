//MIT License
//
//Copyright (c) 2016 Luca Angioloni
//
//Permission is hereby granted, free of charge, to any person obtaining a copy
//of this software and associated documentation files (the "Software"), to deal
//in the Software without restriction, including without limitation the rights
//to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//copies of the Software, and to permit persons to whom the Software is
//furnished to do so, subject to the following conditions:
//
//The above copyright notice and this permission notice shall be included in all
//copies or substantial portions of the Software.
//
//THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//SOFTWARE.

#include <ArduinoJson.h>
#include <AFMotor.h>

//Software wheel convergence
//Values between 0(stop) e 255(max speed)
#define DX 165
#define SX 165
//Do not use too high speeds otherwise the car is going to move
//too fast and will not recognise the objects

const long viewAngleTime = 100; //Turning time
// Higher -> bigger curvature angle

String a;
AF_DCMotor Motor1(1, MOTOR12_64KHZ);
AF_DCMotor Motor2(4, MOTOR12_64KHZ);

void forward(){
  Motor1.setSpeed(SX);
  Motor2.setSpeed(DX); // they sould be equal, but one engine is less powerful
  Motor1.run(FORWARD);
  Motor2.run(FORWARD);
}

void right(double x){
  Motor1.setSpeed(0);
  Motor2.setSpeed(0);
  Motor1.run(BRAKE);
  Motor2.run(BRAKE);
  Motor1.setSpeed(SX);
  Motor2.setSpeed(DX);
  Motor1.run(FORWARD);
  Motor2.run(BACKWARD);
  delay(viewAngleTime * x + 1);
  Motor1.setSpeed(0);
  Motor2.setSpeed(0);
  Motor1.run(BRAKE);
  Motor2.run(BRAKE);
}

void left(double x){
  Motor1.setSpeed(0);
  Motor2.setSpeed(0);
  Motor1.run(BRAKE);
  Motor2.run(BRAKE);
  Motor1.setSpeed(SX);
  Motor2.setSpeed(DX);
  Motor2.run(FORWARD);
  Motor1.run(BACKWARD);
  delay(viewAngleTime * (x * -1) + 1);
  Motor1.setSpeed(0);
  Motor2.setSpeed(0);
  Motor1.run(BRAKE);
  Motor2.run(BRAKE);
}

void brake(){
  Motor1.setSpeed(0);
  Motor2.setSpeed(0);
  Motor1.run(BRAKE);
  Motor2.run(BRAKE);
}

void back(){
  Motor1.setSpeed(SX);
  Motor2.setSpeed(DX); // they sould be equal, but one engine is less powerful
  Motor1.run(BACKWARD);
  Motor2.run(BACKWARD);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5);
}

void loop() {
  if(Serial.available() > 0){
     a = Serial.readString(); 
     char json[100];
     a.toCharArray(json, 100);
     StaticJsonBuffer<100> jsonBuffer;
     JsonObject& root = jsonBuffer.parseObject(json);
     if(root.success()){
       if(root.containsKey("coordinates")){
        double x = root["coordinates"]["x"];
        if(x > 0){
          // go right
          right(x);
        } else{
          // go left
          left(x);
        }
       }
       brake();
       if(root.containsKey("back")){
        bool bck = root["back"];
        if(bck){
          back();
        }
       }
       if(root.containsKey("found")){
        bool found = root["found"];
        if(found){
          forward();
        } else{
          brake();
        }
       }
     }
     Serial.println("F"); // if we ever need confirmation
  }
}
