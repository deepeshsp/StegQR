import qrcode 
from PIL import Image
import numpy as np
import os.path
import sys
 
class Decoder:
    default_dir = os.path.split(__file__)[0]
    default = default_dir + "\\default-hidden.png"
    _min_out_size = 500

    def __init__(self, img=None):
        self._img = img if (img is not None and not os.path.isfile(img)) else self.default
        self._init_file_info()
        self._init_img()

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

    def decode(self, dest_dir="", save=None, show=False):
        if not os.path.isdir(dest_dir):
            dest_dir = self.default_dir

        # scrapes top line of pixels form input, converts to binary from least significant bit to find dimensions of qr code
        qr_dim = int("".join((np.array(self.img.crop((0, 0, self.img.size[0], 1)))[:, :, 0][0] % 2).astype(str)), 2)

        # min size of qr = 500 (defined as base attr)
        # if qr_dim > 500, scale_factor will always be 1
        scale_factor = int(np.ceil(self._min_out_size/qr_dim))

        # get qr code, and parse for lsb
        try:
            qr = Image.fromarray((np.insert(np.array(self.img.crop((0, 0, qr_dim, qr_dim)))[1:], 0, np.ones((1, qr_dim, 3)), 0)[:, :, 0] % 2 * 255).astype("uint8"), mode="L")
        except:
            raise ValueError("Unformatted file, retry with encoded file.")

        # NOTE: update to use python 3.8 walrus operator
        # resize to min size (as defined in base attrs)
        if qr.size[0] < 500:
            qr = qr.resize(list(map(lambda i: int(np.ceil(self._min_out_size/i)) * i, qr.size)))

        full = f"{self._name if save is None else save}{'-qr' * (1-bool(save))}{self._ext}"
        qr.save(full)

        if show:
            qr.show()

        return qr, full

def test_qr():
    img, name = Encoder().encode("https://duckduckgo.com/", show_input=True, show_result=True)
    qr = Decoder().decode(name, show=True)[0]

if __name__ == "__main__":
    test_qr()