import hashlib
import json
import qrcode
from time import time
import os  # Importing os to check for file existence
import BlockClass
import BlockchainClass
import QrCodeClass

def add_media_file(self, file_path, known_good_hash):
    if known_good_hash==None:
        # Checking if the file exists before trying to open it
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"No such file or directory: '{file_path}'")
            file_hash = self.calculate_file_hash(file_path)
            if known_good_hash and file_hash != known_good_hash:
                raise ValueError("File authentication failed: The file hash does not match the known good hash.")
            
            with open(file_path, 'rb') as file:
                media_data = file.read()
            # Here you can add additional processing for the media file if needed
            return self.create_block(data=media_data)
        
def print_file_hash(file_path):
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_sha256.update(chunk)
                    print(f"SHA-256 hash of the file '{file_path}': {hash_sha256.hexdigest()}")
        except FileNotFoundError:
            print(f"The file '{file_path}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage:
# print_file_hash('path/to/your/file.txt')
    
        
print(print_file_hash)

print(add_media_file)