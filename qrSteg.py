from Encoder import Encoder
from Decoder import Decoder

def main():
    e = Encoder()
    #d = Decoder()
    e.encode("this is the original message I am going to make a QR code with. ", fileName="original.png", save=True, show_qr=False)
    e.encode("this is the secret message I am going to hide in the original QR code. ", fileName="secret.png", save=True, show_qr=True)

if __name__ == "__main__":
    main()