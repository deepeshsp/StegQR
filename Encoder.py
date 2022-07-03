import sys, os.path, subprocess, qrcode
from PIL import Image
import numpy as np 
from numpy import random 

class Encoder:

    def __init__(self):
        self.outputDir = self.getOutputDirectory()

    def fetch_qr(self, data, show=False):
        try:
            _qr = qrcode.QRCode( box_size=10, version=1, border=1 ) 
            _qr.add_data(data)
            _qr.make(fit=True)
            qr = _qr.make_image(fill_color="black", back_color="white")
             
        except Exception as e:
            raise ValueError(e)
 
        return qr 

    def hideData(self, image, secret_message):
         # calculate the maximum bytes to encode
        n_bytes = image.size[0] * image.size[1] * 3 // 8
        print("Maximum bytes to encode:", n_bytes)

        #Check if the number of bytes to encode is less than the maximum bytes in the image
        if len(secret_message) > n_bytes:
            raise ValueError("Error encountered insufficient bytes, need bigger image or less data !!")
        
        secret_message += "#####" # you can use any string as the delimeter

        data_index = 0
        # convert input data to binary format using messageToBinary() fucntion
        binary_secret_msg = self.messageToBinary(secret_message)

        data_len = len(binary_secret_msg) #Find the length of data that needs to be hidden
        
        #pix = image.load()

        pix = image.convert('RGB')
        pixel_map = pix.load()
        width, height = image.size 
        if image.mode == "RGB":
            channels = 3
        elif image.mode == "L":
            channels = 1
        else:
            channels = 1
        
        #ra, ga, ba = im.getpixel((1, 1))
        #pixel_values = np.array(pixel_values).reshape((width, height, channels))

        for x in range(width):
            for y in range(height):
                # convert RGB values to binary format
                r, g, b = pixel_map[x, y]#pix.getpixel((x, y)) #self.messageToBinary(pix[x][y])
                # modify the least significant bit only if there is still data to store
                if data_index < data_len:
                    # hide the data into least significant bit of red pixel
                    r = int(bin(r)[:-1] + binary_secret_msg[data_index], 2)
                    data_index += 1
                if data_index < data_len:
                    # hide the data into least significant bit of green pixel
                    g = int(bin(g)[:-1] + binary_secret_msg[data_index], 2)
                    data_index += 1
                if data_index < data_len:
                    # hide the data into least significant bit of  blue pixel
                    b = int(bin(b)[:-1] + binary_secret_msg[data_index], 2)
                    data_index += 1
                # if data is encoded, just break out of the loop
                if data_index >= data_len:
                    break
                
                pixel_map[x, y] = (r, g, b)
        return pix
 
    def messageToBinary(self, message):
        if type(message) == str:
            return ''.join([ format(ord(i), "08b") for i in message ])
        elif type(message) == bytes or type(message) == np.ndarray:
            return [ format(i, "08b") for i in message ]
        elif type(message) == int or type(message) == np.uint8:
            return format(message, "08b")
        else:
            raise TypeError("Input type not supported")
            
    def embedByLSB(self, imgPath, secretMsg):
                
        # Encode the message in a series of 8-bit values
        b_message = ''.join(["{:08b}".format(ord(x)) for x in secretMsg ])
        b_message = [int(x) for x in b_message]

        b_message_length = len(b_message)

        # Get the image pixel arrays 
        with Image.open(imgPath) as img:
            width, height = img.size
            data = np.array(img)
            
        # Flatten the pixel arrays
        #data = np.reshape(data, width*height*3)

        # Overwrite pixel LSB
        data[:b_message_length] = data[:b_message_length] & ~1 | b_message

        # Reshape back to an image pixel array
        data = np.reshape(data, (height, width, 3))

        new_img = Image.fromarray(data)
        new_img.save(self.outputDir + "/" + "merged.png") 
        new_img.show()
                    
                    
    def getOutputDirectory(self):
        basePath = "./output/"
        for i in range(100):
            if not os.path.exists(basePath + "/" + str(i) + "/"):
                basePath = basePath + "/" + str(i) + "/"
                os.makedirs(basePath)
                return basePath
        return ""

    def encode(self, data, fileName="original.png", save=True, show_input=False, show_qr=False, show_result=False):
        qrcod = self.fetch_qr(data, show=show_qr) 

        qrcod.save(self.outputDir + "/" + fileName) 

        image = Image.open(self.outputDir + "/" + fileName)
        newimg = self.hideData(image, "this is a secret message")
        newimg.save(self.outputDir + "/" + "merged.png") 
        #self.embedByLSB(self.outputDir + "/" + fileName, "this is a secret message")

        if show_qr == True:
            os.system(f'start {os.path.realpath(self.outputDir)}') 
        return  qrcod
 
def test_qr():
     Encoder().encode("This is a sample text form test_qr", show_input=True, show_result=True)
    
if __name__ == "__main__":
    test_qr()