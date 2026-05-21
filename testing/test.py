import requests

FILENAME = 'test_images/test_image.png'

with open(FILENAME, 'rb') as f:
    image_data = f.read()

files = {'image': (FILENAME, image_data)}
response = requests.post('http://localhost:5000/grayscale', files=files)
response2 = requests.post('http://localhost:5000/contours', files=files)
response3 = requests.post('http://localhost:5000/warp', files=files)
response4 = requests.post('http://localhost:5000/lighten', files=files)
response5 = requests.post('http://localhost:5000/pdf', files=files)

with open('results/grayscale_result.png', 'wb') as f:
    f.write(response.content)

with open('results/contours_result.png', 'wb') as f:
    f.write(response2.content)

with open('results/warp_result.png', 'wb') as f:
    f.write(response3.content)

with open('results/lighten_result.png', 'wb') as f:
    f.write(response4.content)

with open('results/document.pdf', 'wb') as f:
    f.write(response5.content)