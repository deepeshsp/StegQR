import sys,io, os.path, subprocess, qrcode, cv2
from PIL import Image
import numpy as np 
from numpy import random 
import matplotlib.pyplot as plt
import matplotlib.cm as cm

class Encoder:

    def __init__(self, delimiter = "$%$"):
        self.outputDir = self.getOutputDirectory()
        self.delimiter = delimiter

    def makePlainQR(self, data, show=False):
        try:
            _qr = qrcode.QRCode( box_size=10, version=1, border=1 ) 
            _qr.add_data(data)
            _qr.make(fit=True)
            qr = _qr.make_image(fill_color="black", back_color="white")
             
        except Exception as e:
            raise ValueError(e)
 
        return qr  

    def hideDataInXOR(self, imagePath, secret_message):

        plainImg=cv2.imread(imagePath, flags=cv2.IMREAD_GRAYSCALE) 

        #https://github.com/daQuincy/Image-Steganography-using-LSB-and-XOR-Operation-on-MSB/blob/master/Image%20Steganography.ipynb
        secret_message += self.delimiter  
        #binary_secret_msg = list(self.messageToBinary(secret_message))
        binary_secret_msg = self.messageToBinary(secret_message)
        
        binary_secret_msgarr = [1 for _ in range(plainImg.size)]
        binary_secret_msgarr[:] = [binary_secret_msgarr[i:i + plainImg.shape[0]] for i in range(0, plainImg.size, plainImg.shape[1])]

        mainx = 0
        breaker = plainImg.shape[1]
        for i in range(0, len(binary_secret_msg), breaker):
            # slicing the bin_data from index range [0, 6]
            # and storing it in temp_data
            if(len(binary_secret_msg[i:]) < breaker):
                temp_data1 = list(binary_secret_msg[i:])
                temp_data2 = [int(x) for x in temp_data1]
                temp_data2 = temp_data2 + binary_secret_msgarr[mainx][len(binary_secret_msg[i:]):]
            else:
                temp_data1 = list(binary_secret_msg[i:i + breaker])
                temp_data2 = [int(x) for x in temp_data1]
            #temp_data1 = list(temp_data)
            binary_secret_msgarr[mainx] = temp_data2
            mainx += 1
             
        plt.imsave(self.outputDir+'/secret.png', np.array(binary_secret_msgarr).reshape(plainImg.shape[0],plainImg.shape[1]), cmap=cm.gray)
        secretImg=cv2.imread(self.outputDir+'/secret.png', flags=cv2.IMREAD_GRAYSCALE) 
        secretImg[secretImg>0] = 1

        c_flatten = plainImg.flatten()
        m_flatten = secretImg.flatten()

        #print(c_flatten.shape)
        #print(m_flatten.shape)

        out = []
        for a, b in zip(c_flatten, m_flatten):
            a = np.binary_repr(a, width=8) 

            # step 3: perform XOR operations on the 7th and on the 6th bit    
            xor_a = int(a[1]) ^ int(a[2])
            
            # step 4: perform XOR operations on 8th bit with xor_a
            xor_b = int(a[0]) ^ xor_a
            
            # step 5: perform XOR operations on message bits with 3 MSB
            xor_c = int(b) ^ xor_b 
            
            # step 6: save xor_c, convert back to uint8
            save = a[:-1] + str(xor_c)
            
            out.append(int(save, 2))


        stego_img = np.array(out)
        stego_img = np.reshape(stego_img, (plainImg.shape[0], plainImg.shape[1]))

        cv2.imwrite(self.outputDir + "/" + "steggedXOR.png", stego_img) 
        return
    
    def hideDataInLSB(self, image, secret_message):
         # calculate the maximum bytes to encode
        n_bytes = image.size[0] * image.size[1] * 3 // 8
        #print("Maximum bytes to encode:", n_bytes)

        #Check if the number of bytes to encode is less than the maximum bytes in the image
        if len(secret_message) > n_bytes:
            raise ValueError("Error encountered insufficient bytes, need bigger image or less data !!")
        
        secret_message += self.delimiter # you can use any string as the delimeter

        # convert input data to binary format using messageToBinary() fucntion
        binary_secret_msg = self.messageToBinary(secret_message)
        #print("binary_secret_msg = " + binary_secret_msg)

        data_index = 0
        data_len = len(binary_secret_msg) #Find the length of data that needs to be hidden
        
        pix = image.convert('RGB')
        pixel_map = pix.load()
        width, height = image.size 
        
        #if image.mode == "RGB":
        #    channels = 3
        #elif image.mode == "L":
        #    channels = 1
        #else:
        #    channels = 1
        #ra, ga, ba = im.getpixel((1, 1))
        #pixel_values = np.array(pixel_values).reshape((width, height, channels))

        for x in range(width):
            for y in range(height):
                # convert RGB values to binary format
                r, g, b = pixel_map[x, y] #pix.getpixel((x, y)) #self.messageToBinary(pix[x][y])
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
                # if data is encoded, just break out of the y loop
                if data_index >= data_len:
                    break
    
                pixel_map[x, y] = (r, g, b)
    
            # if data is encoded, just break out of the x loop
            if data_index >= data_len:
                break
        return pix
    
    def encodeInLSB(self, data, secretData, fileName):
        print("encoding....")
        print("plain Message : " + data)
        print("secret Message : "+ secretData)
        print("output Directory : " + self.outputDir)
        
        qrcod = self.makePlainQR(data) 
        qrcod.save(self.outputDir + "/" + fileName) 

        image = Image.open(self.outputDir + "/" + fileName)
        newimg = self.hideDataInLSB(image, secretData)
        #newimg.save(self.outputDir + "/" + "steggedInLSB.png") 
        
        self.hideDataInXOR(self.outputDir + "/" + fileName, secretData)
        #self.embedByLSB(self.outputDir + "/" + fileName, "this is a secret message")
        return

    def messageToBinary(self, message):
        if type(message) == str:
            return ''.join([ format(ord(i), "08b") for i in message ])
        elif type(message) == bytes or type(message) == np.ndarray:
            return [ format(i, "08b") for i in message ]
        elif type(message) == int or type(message) == np.uint8:
            return format(message, "08b")
        else:
            raise TypeError("Input type not supported")
            
    def getOutputDirectory(self):
        basePath = "./output/"
        for i in range(100):
            if not os.path.exists(basePath + str(i) + "/"):
                basePath = basePath + str(i) + "/"
                os.makedirs(basePath)
                return basePath
        return ""

    def encode(self, data, secretData, fileName="original.png", save=True, show_input=False, show_qr=True, show_result=False):

        self.encodeInLSB(data,secretData, fileName)
        if show_qr == True:
            os.system(f'start {os.path.realpath(self.outputDir)}') 
        return
 
    def testLab():
        textArr = []
        #a_binary_string = "0123456789012345678901234567890123456789"
        a_binary_string ="01100001 01100010 01100011"

        binary_values = a_binary_string.split()
        ascii_string = ""
        for binary_value in binary_values:
            an_integer = int(binary_value, 2)

            ascii_character = chr(an_integer)
            ascii_string += ascii_character
        print(ascii_string)

        a_binary_string = "0111010001101000011010010111001100100000011010010111001100100000011101000110100001100101001000000110100001101001011001000110010001100101011011100010000001101101011001010111001101110011011000010110011101100101001000000010001100100011001000110010001100100011"
        for i in range(0, len(a_binary_string), 8):
            # slicing the bin_data from index range [0, 6]
            # and storing it in temp_data
            temp_data = a_binary_string[i:i + 8]
            charText = chr(int(temp_data,2))
            textArr.append(charText)
            #print("[{},{}] = {} => {}".format(i, (i+8) , temp_data, charText ))
            
        print("hidden message is :" + "".join(textArr))
        #print(int(temp_data, 2))

        #return
        #Split string on whitespace
        binary_values = a_binary_string.split()

        ascii_string = ""
        for binary_value in binary_values:
            #Convert to base 2 decimal integer
            an_integer = int(binary_value, 2)

            # Convert to ASCII character
            ascii_character = chr(an_integer)

            #Append character to `ascii_string`
            ascii_string += ascii_character


        print(ascii_string) 

def test_qr():
     Encoder().encode("This is a sample text form test_qr", "secretData", show_input=True, show_result=True)
    
if __name__ == "__main__":
    test_qr()