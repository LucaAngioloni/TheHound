//
//  AppDelegate.swift
//  CVClient
//
//  Created by Luca Angioloni on 23/09/2016.
//  Copyright © 2016 Luca Angioloni. All rights reserved.
//

import UIKit
import Foundation
import NetworkExtension

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    var window: UIWindow?
    var cvClient:Client?
    
    var clientCreated = false
    
    let address = "raspberrypi2.local"
    //let address = "raspberrypi7.local"
    //let address = "Lucas-MacBook.local"
    //let address = "172.20.10.2"
    let port = 50001
    var ip:String?
    
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        DispatchQueue.global(qos: DispatchQoS.userInteractive.qosClass).async {
            let controller: ViewController = self.window!.rootViewController as! ViewController
            self.cvClient = Client(addr: self.address, port: self.port)
            self.clientCreated = true
            controller.linkClient(cli: self.cvClient!)
            var error = true
            while(error){
                let connection = self.cvClient!.connect(timeout: 10)
                if connection.0 == true{
                    error = false
                    print("Connected: " + connection.1)
                    self.cvClient!.loop()
                }
            }
        }
        return true
    }
    
    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
        // Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
        if clientCreated {
            if cvClient!.connOpen{
                cvClient!.close()
            }
        }
    }
    
    func applicationDidEnterBackground(_ application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
        // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
        if clientCreated {
            if cvClient!.connOpen{
                cvClient!.close()
            }
        }
    }
    
    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
        if clientCreated {
            if !cvClient!.connOpen {
                var error = true
                DispatchQueue.global(qos: DispatchQoS.userInteractive.qosClass).async {
                    while(error){
                        let connection = self.cvClient!.connect(timeout: 10)
                        if connection.0 == true{
                            error = false
                            self.cvClient!.loop()
                        }
                    }
                }
            }
        }
    }
    
    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
        if clientCreated {
            if !cvClient!.connOpen {
                var error = true
                DispatchQueue.global(qos: DispatchQoS.userInteractive.qosClass).async {
                    while(error){
                        let connection = self.cvClient!.connect(timeout: 10)
                        if connection.0 == true{
                            error = false
                            self.cvClient!.loop()
                        }
                    }
                }
            }
        }
    }
    
    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
        if clientCreated {
            if cvClient!.connOpen{
                cvClient!.close()
            }
        }
    }
    
    
}

