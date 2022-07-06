import cv2
import numpy as np
import matplotlib.pyplot as plt

# step 1: read the cover image and message image
c_img = cv2.imread("lena.png", 0)
c_img = cv2.resize(c_img, (256, 256))

m_img = cv2.imread("git.png", 0)
m_img = cv2.resize(m_img, (256, 256))
m_img[m_img>0] = 1

plt.subplot(121)
plt.axis("off")
plt.title("Cover Image")
plt.imshow(c_img, cmap="gray")

plt.subplot(122)
plt.axis("off")
plt.title("Message Image")
plt.imshow(m_img, cmap="gray")

plt.show()

c_flatten = c_img.flatten()
m_flatten = m_img.flatten()

print(c_flatten.shape)
print(m_flatten.shape)

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
    
    # https://stackoverflow.com/questions/8928240/convert-base-2-binary-number-string-to-int
    out.append(int(save, 2))

stego_img = np.array(out)
stego_img = np.reshape(stego_img, (256, 256))

plt.figure(figsize=(20,10))

plt.subplot(121)
plt.title("Cover Image")
plt.axis("off")
plt.imshow(c_img, cmap="gray")

plt.subplot(122)
plt.title("Stego Image")
plt.axis("off")
plt.imshow(stego_img, cmap="gray")

plt.show()