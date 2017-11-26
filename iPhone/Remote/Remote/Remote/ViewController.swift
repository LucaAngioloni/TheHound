//
//  ViewController.swift
//  CVClient
//
//  Created by Luca Angioloni on 23/09/2016.
//  Copyright © 2016 Luca Angioloni. All rights reserved.
//

import UIKit

class ViewController: UIViewController {
    
    var client:Client?
    var startTime:Int64=0
    var count = 0
    var timer: Timer!
    
    func getCurrentMillis()->Int64 {
        return Int64(Date().timeIntervalSince1970 * 1000)
    }
    
    @IBOutlet weak var ImageView: UIImageView!
    @IBOutlet weak var fpsLabel: UILabel!
    
    
    
    @IBAction func buttonFDown(_ sender: Any) {
        foreward()
        timer = Timer.scheduledTimer(timeInterval: 0.3, target: self, selector: #selector(ViewController.foreward), userInfo: nil, repeats: true)
    }
    
    @IBAction func buttonFUp(_ sender: AnyObject) {
        timer.invalidate()
    }
    
    func foreward() {
        client?.send(msg: "F")
    }
    
    
    @IBAction func buttonLDown(_ sender: AnyObject) {
        left()
        timer = Timer.scheduledTimer(timeInterval: 0.3, target: self, selector: #selector(ViewController.left), userInfo: nil, repeats: true)
    }
    
    @IBAction func buttonLUp(_ sender: AnyObject) {
        timer.invalidate()
    }
    
    func left() {
        client?.send(msg: "L")
    }
    
    
    @IBAction func buttonRDown(_ sender: AnyObject) {
        right()
        timer = Timer.scheduledTimer(timeInterval: 0.3, target: self, selector: #selector(ViewController.right), userInfo: nil, repeats: true)
    }
    
    @IBAction func buttonRUp(_ sender: AnyObject) {
        timer.invalidate()
    }
    
    func right() {
        client?.send(msg: "R")
    }
    
    
    @IBAction func buttonBDown(_ sender: AnyObject) {
        back()
        timer = Timer.scheduledTimer(timeInterval: 0.3, target: self, selector: #selector(ViewController.back), userInfo: nil, repeats: true)
    }
    
    @IBAction func buttonBUp(_ sender: AnyObject) {
        timer.invalidate()
    }
    
    func back() {
        client?.send(msg: "B")
    }
    
    
    @IBAction func buttonStopPressed(_ sender: Any) {
        client?.send(msg: "S")
    }
    
    
    func linkClient(cli:Client){
        client = cli
        cli.controller = self
        startTime = getCurrentMillis()
    }
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func showNewImage(_ img:UIImage) -> Bool{
        count = count + 1
        ImageView.image = img
        //print("Image Showed")
        let new = getCurrentMillis()
        if(new - startTime >= 1000){
            startTime = new
            fpsLabel.text = "\(count) fps"
            count = 0
        }
        return true
    }
    
    func displayConnectionError(){
        let alertController = UIAlertController(title: "Connection closed", message:
            "There is no connection with device", preferredStyle: UIAlertControllerStyle.alert)
        alertController.addAction(UIAlertAction(title: "Dismiss", style: UIAlertActionStyle.default,handler: nil))
        
        self.present(alertController, animated: true, completion: nil)
    }
}

