import hashlib
import json
import qrcode
from time import time
import os  # Importing os to check for file existence
import BlockchainClass
import BlockClass

class QrCode:
    def create_qr_code(image_path, output_path):
        # Create a QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            )
    
        # Add the image file path or URL to the QR code
        qr.add_data(image_path)
        qr.make(fit=True)
    
        # Create an image from the QR Code instance
        img = qr.make_image(fill_color="black", back_color="white")
    
        # Save the QR code as an image file
        img.save(output_path)

    if __name__ == "__main__":
        image_path = r'C:\Users\irisc\CoalCarPOC.jpg'  # Replace with your image file path, make sure it's a raw string
        output_path = 'qrcode.png'              # Output QR code file

        create_qr_code(image_path, output_path)
        print(f"QR code saved to {output_path}")
