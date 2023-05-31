import numpy as np
from polarcodes import *

def text_to_bits(text):
    # Convert text to bytes using UTF-8 encoding
    bytes_data = text.encode('utf-8')

    # Convert bytes to binary representation
    bits = ''.join(format(byte, '08b') for byte in bytes_data)
    
    return bits

def bits_to_ascii(binary):
    # Convert binary string to an integer
    decimal = int(binary, 2)
    
    # Convert the integer to bytes
    bytes_data = decimal.to_bytes((decimal.bit_length() + 7) // 8, 'big')
    
    try:
        # Decode bytes to text using UTF-8 encoding
        text = bytes_data.decode('utf-8')
    except UnicodeDecodeError:
        # Handle decoding errors by replacing invalid bytes
        text = bytes_data.decode('utf-8', 'replace')
    
    return text

# initialise polar code
myPC = PolarCode(256, 100)
myPC.construction_type = 'bb'

# mothercode construction
design_SNR  = 5.0
Construct(myPC, design_SNR)
print(myPC, "\n\n")

message = "Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. Separated they live in."
code_word_length = 4300

# Truncate the message to 140 characters if necessary
message = message[:140]

# Encode the message
encoded_message = text_to_bits(message)

# Add padding zeros to the encoded message to match the code word length
encoded_message += '0' * (code_word_length - len(encoded_message))
my_message = encoded_message

myPC.set_message(my_message)
print("The message is:", my_message)

# print(f"Encoded message: {encoded_message}")
# print(f"Encoded message length: {len(encoded_message)} bits")

# # Example usage
# decoded_message = bits_to_ascii(encoded_message)

# print(f"Decoded message: {decoded_message}")

