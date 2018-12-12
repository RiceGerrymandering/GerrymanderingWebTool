import sys 
import base64

#open binary file in read mode and encode
image = open('../rice/new_map.png', 'rb') 
image_read = image.read() 
image_64_encode = base64.b64encode(image_read)
string = "data:image/png;base64," + image_64_encode

#Write base64 encoding
f = open("out.txt", "w")
f.write(string)
print(sys.argv)
