//
//  ViewController.swift
//  CVClient
//
//  Created by Luca Angioloni on 23/09/2016.
//  Copyright © 2016 Luca Angioloni. All rights reserved.
//

import UIKit

class ViewController: UIViewController, UIImagePickerControllerDelegate, UINavigationControllerDelegate {

    var client:Client?
    var startTime:Int64=0
    var count = 0
    
    let imagePicker = UIImagePickerController()
    
    func getCurrentMillis()->Int64 {
        return Int64(Date().timeIntervalSince1970 * 1000)
    }
    
    @IBOutlet weak var ChooseButton: UIButton!
    @IBOutlet weak var ImageView: UIImageView!
    @IBOutlet weak var fpsLabel: UILabel!
    
    @IBAction func buttonPressed(_ sender: UIButton) {
        print("Button pressed")
        if client!.connOpen{
            //client?.send(msg: "newImage")
            imagePicker.allowsEditing = false
            imagePicker.sourceType = .photoLibrary
        
            present(imagePicker, animated: true, completion: nil)
        } else{
            displayConnectionError()
        }
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [String : Any]) {
        print("Image chosen")
        dismiss(animated: true, completion: nil)
        if let pickedImage = info[UIImagePickerControllerOriginalImage] as? UIImage {
            print("Image Sent")
            client!.sendImage(image: pickedImage)
            fpsLabel.isHidden = false
        }
        ChooseButton.isHidden = true
    }
    
    func linkClient(cli:Client){
        client = cli
        cli.controller = self
        startTime = getCurrentMillis()
    }
    override func viewDidLoad() {
        super.viewDidLoad()
        ImageView.image = UIImage(named: "Placeholder")
        imagePicker.delegate = self
        fpsLabel.isHidden = true
        ChooseButton.isHidden = false
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
        ChooseButton.isHidden = true
        return true
    }
    
    func displayConnectionError(){
        let alertController = UIAlertController(title: "Connection closed", message:
            "There is no connection with device", preferredStyle: UIAlertControllerStyle.alert)
        alertController.addAction(UIAlertAction(title: "Dismiss", style: UIAlertActionStyle.default,handler: nil))
        
        self.present(alertController, animated: true, completion: nil)
        ChooseButton.isHidden = false
    }
}

