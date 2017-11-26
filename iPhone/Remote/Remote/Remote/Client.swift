//
//  Client.swift
//  CVClient
//
//  Created by Luca Angioloni on 23/09/2016.
//  Copyright © 2016 Luca Angioloni. All rights reserved.
//

import Foundation
import UIKit

// let address = "raspberrypi2.local"
//let address = "Lucas-MacBook.local"



class Client{
    
    let headerLenght:Int = 7
    var count = 0
    var address:String
    var port:Int
    
    var controller: ViewController?
    var client:TCPClient?
    var connOpen:Bool = true
    
    init(addr a:String, port p:Int) {
        address = a
        port = p
        client = TCPClient(addr: address, port: port)
    }
    
    func connect(timeout t:Int)->(Bool,String){
        print("Connecting")
        connOpen = true
        return client!.connect(timeout: t)
    }
    
    func close()->(Bool,String){
        connOpen = false
        return client!.close()
    }
    
    func send(msg:String){
        client?.send(str: msg)
    }
    
    func headerInfo(header:[UInt8]) -> (type: String, len: Int) {
        
        count = count+1
        //print(header)
        let typeArray:[UInt8] = Array(header[0..<3])
        let lenArray:[UInt8] = Array(header[3..<header.count])
        
        // get type String
        let typeStr = String(data: Data(bytes: typeArray), encoding: String.Encoding.utf8)
        
        // get length Int
        var lenUint: UInt32 = 0
        let data = NSData(bytes: lenArray, length: 4)
        data.getBytes(&lenUint, length: 4)
        lenUint = UInt32(bigEndian: lenUint)
        
        // return
        if let type = typeStr {
            return (type, Int(lenUint))
        } else{
            return ("err", Int(lenUint))
        }
    }
    
    func loop(){
        DispatchQueue.global(qos: DispatchQoS.userInteractive.qosClass).async { // new thr  ead to listen and receive raspberry images
            while(self.connOpen){
                let startreceived = self.client!.read(1)
                if let start = startreceived {
                    if let typeStr = String(data: Data(bytes: start), encoding: String.Encoding.utf8){
                        if typeStr == "S"{
                            let headerrec = self.client!.read(self.headerLenght)
                            if let header = headerrec {
                                let info = self.headerInfo(header: header)
                                print(info)
                                print(self.count)
                                if info.type == "img" {
                                    var received = 0
                                    var imgArray:[UInt8] = [UInt8]()
                                    while(received < info.len){
                                        if let tmpArray = self.client!.read(info.len - received) {
                                            received = received + tmpArray.count
                                            imgArray.append(contentsOf: tmpArray)
                                        }
                                    }
                                    if let image = UIImage(data: Data(bytes: imgArray)) {
                                        //print("Image Received")
                                        DispatchQueue.main.sync {
                                            // Code to update graphics
                                            // This queue is the only thread allowed to update your UI. This queue is the one to use for sending messages to UIView objects or posting notifications.
                                            //print("About to show image")
                                            if (self.controller?.showNewImage(image))! {
                                                print("Image show success")
                                            }
                                        }
                                    }
                                } else if info.type == "msg" {
                                    // maybe I need messages?
                                    let msgArray = self.client!.read(info.len)!
                                    if let message = String(data: Data(bytes: msgArray), encoding: String.Encoding.utf8) {
                                        print("The message was: " + message)
                                        print("info type: " + info.type)
                                        print("info len: " + String(info.len))
                                        if message == "closeConnection"{
                                            self.controller?.displayConnectionError()
                                            self.connOpen = false
                                            self.close()
                                            var error = true
                                            DispatchQueue.global(qos: DispatchQoS.userInteractive.qosClass).async {
                                                while(error){
                                                    let connection = self.connect(timeout: 10)
                                                    if connection.0 == true{
                                                        error = false
                                                        self.loop()
                                                    }
                                                }
                                            }
                                            
                                        }

                                    }
                                } else if info.type == "err" {
                                    print("Error")
                                    self.close()
                                    self.controller?.displayConnectionError()
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
