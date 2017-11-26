//
//  UIImageExtension.swift
//  CVClient
//
//  Created by Luca Angioloni on 28/09/2016.
//  Copyright © 2016 Luca Angioloni. All rights reserved.
//

import Foundation
import UIKit
import CoreGraphics

extension UIImage {
    
    func convertCIImageToCGImage(inputImage: CIImage) -> CGImage! {
        let context = CIContext(options: nil)
        if context != nil {
            return context.createCGImage(inputImage, from: inputImage.extent)
        }
        return nil
    }
    
    func convertUIImageToCIImage(uiImage: UIImage) -> CIImage {
        return CIImage(image: uiImage)!
    }
    
    func preloadedImage() -> UIImage {
        
        let cgImg = self.cgImage
        
        // make a bitmap context of a suitable size to draw to, forcing decode
        let width = cgImg!.width
        let height = cgImg!.height
        
        let colourSpace = CGColorSpaceCreateDeviceRGB()
        let imageContext =  CGContext(data: nil,
                                      width: width,
                                      height: height,
                                      bitsPerComponent: 8,
                                      bytesPerRow: width * 4,
                                      space: colourSpace,
                                      bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue)
        
        // draw the image to the context, release it
        imageContext!.draw(cgImg!, in: CGRect(x: 0, y: 0, width: width, height: height))
        
        // now get an image ref from the context
        if let outputImage = imageContext!.makeImage() {
            let cachedImage = UIImage(cgImage: outputImage)
            print("Image Cached")
            return cachedImage
        }
        
        print("Failed to preload the image")
        return self
    }
}
