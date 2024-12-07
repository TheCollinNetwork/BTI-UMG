import hashlib
import json
from time import time
import os  # Importing os to check for file existence
import BlockClass

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

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash='0')

    def create_block(self, data=None, previous_hash=None):
        block = BlockClass.Block(len(self.chain) + 1, time(), data, previous_hash or self.chain[-1].hash)
        self.chain.append(block)
        return block

    def calculate_file_hash(self, file_path):
        # Calculates the SHA-256 hash of the file
        hasher = hashlib.sha256
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192): #reads the file in chunks
                hasher.update(chunk)
            return hasher.hexdigest()
        
print (Blockchain)