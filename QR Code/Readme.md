Create Your Own QR Codes on the Fly

I needed a good, simple QR Code recently without having to use one of those “suspicious” sites or having to pay for it.
Microsoft Edge does it, but the QR Codes it produces are massive and complex and including them in a slide deck or image means it can’t be resized without losing its effectiveness.
I thought - hey, shouldn’t a GenAI tool be able to do that? So, I tried the following popular options:
•	Copilot = said it created one for me but could never display the actual image.
•	Gemini = simply said it can’t create QR codes.
•	Grok = kept creating the QR Code included in a random image, but the QR code was unusable.
•	ChatGPT = Same as Copilot.
So, I ended up building my own QR Code generator with Python and thought I’d share.
Here’s the Python code:
Python
import qrcode

# URL for the QR code
url = "https://www.example.com"

# Create QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add URL data to the QR code
qr.add_data(url)
qr.make(fit=True)

# Create an image from the QR code
img = qr.make_image(fill_color="black", back_color="white")

# Save the QR code image
img.save("qrcode.png")
To use this script:
1.	Install the qrcode library using: pip install qrcode pillow
2.	Replace https://www.example.com with the desired web page URL.
3.	Run the script to generate a qrcode.png file in your working directory.
The generated QR code image can be scanned with a smartphone or QR code reader to open the specified web page.

