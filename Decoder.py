import qrcode 
from PIL import Image
import numpy as np
import os.path
import sys
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
 
class Decoder: 
    def __init__(self, output_path=None, delimiter = None):
        self.outputDir = output_path
        self.delimiter = delimiter

    @property
    def image(self):
        return self.img

    @image.setter
    def image(self, new):
        self._img = new
        self._init_file_info()
        self._init_img()

    @image.deleter
    def image(self):
        self.img = self.default

    def _init_file_info(self):
        try:
            self._img = self.default if self._img is None else self._img
            self._name, self._ext = os.path.splitext(self._img)
        except:
            raise Exception("Path invalid.")

    def _init_img(self):
        try:
            self.img = Image.open(self._img)
        except:
            raise FileNotFoundError(f"'{self._name+self._ext}' was not found in {sys.path}.\nPlease check if the file exists.")

    def BinaryToDecimal(self,binary):
        
        # Using int function to convert to
        # string  
        string = int(binary, 2)
        
        return string
        
    def decode(self, dest_dir="", save=None, show=False):
        #decodedMessage = self.decodeFromLSB(self)
        decodedMessage = self.decodeUsingXOR(self)
        return
  
    def decodeUsingXOR(self, dest_dir="", save=None, show=False):
        stego_img = cv2.imread(self.outputDir + "/steggedXOR.png", 0)
        stego_flatten = stego_img.flatten()

        out = []
        for x in stego_flatten:
            # step 2: change pixel value to binary
            x = np.binary_repr(x, width=8)
            # step 3: perform XOR on 7th and 6th bits
            xor_a = int(x[1]) ^ int(x[2])
            # step 4: perform XOR operation on 8th bit with xor_a
            xor_b = int(x[0]) ^ xor_a
            # step 5: perform XOR operations on message bits with 3 MSB
            xor_c = int(x[-1]) ^ xor_b
            
            out.append(int(xor_c))

        recover_img = np.reshape(np.array(out), (stego_img.shape[0],stego_img.shape[1]))
        recover_img[recover_img==1] = 255
        plt.imsave(self.outputDir + "/recoveredSecret.png",recover_img, cmap="gray")
        recover_img[recover_img>1] = 1
        
        binary_secret_msg = ""
        str_data = []
        binary_secret_msgarr = recover_img
        
        mainx = 0
        breaker = stego_img.shape[1]
        for i in range(0, (stego_img.shape[0] * stego_img.shape[1]), breaker):
            binary_secret_msg += "".join(str(x) for x in list(recover_img[mainx]))
            mainx += 1

        for i in range(0, len(binary_secret_msg), 8):
            # slicing the bin_data from index range [0, 6]
            # and storing it in temp_data
            temp_data = binary_secret_msg[i:i + 8]
            # to get decimal value of corresponding temp_data
            charText = int(temp_data,2)
            # character for given ASCII value
            charText = chr(charText)
            # append it to str_data
            str_data.append(charText)
            #print("[{},{}] = {} => {}".format(i, (i+8) , temp_data, charText ))
        
        strData = "".join(str_data) 

        if self.delimiter != None:
            strData = strData.split(self.delimiter)[0]
        
        print("decoded hidden message (LSB) :" + strData)

        return

        
    def decodeFromLSB(self, dest_dir="", save=None, show=False):
        stegImage = Image.open(self.outputDir + "/" + "steggedInLSB.png")
        
        # calculate the maximum bytes to encode
        n_bytes = stegImage.size[0] * stegImage.size[1] * 3 // 8
        binary_secret_msg = ""
        str_data= []
 
        #pix = image.convert('RGB')
        width, height = stegImage.size 
        pixel_map = stegImage.load()
        
        for x in range(width):
            for y in range(height):
                # convert RGB values to binary format
                r, g, b = pixel_map[x, y] #pix.getpixel((x, y)) #self.messageToBinary(pix[x][y])
                
                binary_secret_msg+= (bin(r)[-1])
                binary_secret_msg+= (bin(g)[-1])
                binary_secret_msg+= (bin(b)[-1])

        #print("decoded binary_secret_msg = " + binary_secret_msg)

        for i in range(0, len(binary_secret_msg), 8):
            # slicing the bin_data from index range [0, 6]
            # and storing it in temp_data
            temp_data = binary_secret_msg[i:i + 8]
            # to get decimal value of corresponding temp_data
            charText = int(temp_data,2)
            # character for given ASCII value
            charText = chr(charText)
            # append it to str_data
            str_data.append(charText)
            #print("[{},{}] = {} => {}".format(i, (i+8) , temp_data, charText ))
        
        strData = "".join(str_data) 

        if self.delimiter != None:
            strData = strData.split(self.delimiter)[0]
        
        print("decoded hidden message (LSB) :" + strData)
        return strData

def test_qr():
    #img, name = Encoder().encode("temp encoding text", show_input=True, show_result=True)
    qr = Decoder().decode(None, show=True)[0]

if __name__ == "__main__":
    test_qr()