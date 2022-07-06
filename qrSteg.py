import sys, string
from Encoder import Encoder
from Decoder import Decoder

def main():
    plainMsg = "this is the original message I am going to make a QR code with. "
    secretMsg = " start this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message this is the hidden message "
    secretMsg += secretMsg
    secretMsg += secretMsg
    secretMsg += secretMsg
    secretMsg += secretMsg
    secretMsg += " end"

    delimiter = "####"
    e = Encoder(delimiter)
    d = Decoder(e.outputDir, delimiter)
    e.encode(plainMsg, secretMsg)
    out = d.decode() 
    #e.encode("this is the secret message I am going to hide in the original QR code. ", fileName="secret.png", save=True, show_qr=True)

if __name__ == "__main__":
    main()