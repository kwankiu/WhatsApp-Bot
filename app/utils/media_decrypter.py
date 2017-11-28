import os, hashlib
import hmac
import binascii

from Crypto.Cipher import AES
from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil

WHATSAPP_KEY = "576861747341707020496d616765204b657973"
AUDIO_KEY = "576861747341707020417564696f204b657973"
VIDEO_KEY = "576861747341707020566964656f204b657973"
IMAGE_KEY = "576861747341707020496d616765204b657973"
DOCUMENT_KEY = "576861747341707020496d616765204b657973"

def decrypt_file(enc_path, media_key, media_type, out_path=""):
    media_key = binascii.hexlify(media_key)
    key = getKey(media_type)
    derivative = HKDFv3().deriveSecrets(binascii.unhexlify(media_key), binascii.unhexlify(key), 112)
    
    splits = ByteUtil.split(derivative, 16, 32)
    iv = splits[0]
    cipher_key = splits[1]

    cipher = AES.new(key=cipher_key, mode=AES.MODE_CBC, IV=iv)
    
    if (out_path == ""):
        out_path = os.path.splitext(enc_path)[0]
    
    chunk_size = 4096 * 10
    with open(enc_path, "rb") as in_file:
        with open(out_path, "wb") as out_file:
            while True:
                chunk = in_file.read(chunk_size)
                try:
                    piece = cipher.decrypt(chunk)
                except:
                    # Last chunk most likely to get into here
                    # Because cipher needs a multiple of 16
                    piece = cipher.decrypt(pad(chunk))
                    
                if len(chunk) == 0:
                    break # end of file
        
                out_file.write(piece)
                
    return out_path
    
    
def getKey(media_type):
    print(media_type)
    if media_type == "image":
        return IMAGE_KEY
    elif media_type == "audio":
        return AUDIO_KEY
    elif media_type == "document":
        return DOCUMENT_KEY
    else:
        return IMAGE_KEY
    
def pad(stream):
    x = (16 - len(stream) % 16) * chr(16 - len(stream) % 16)
    return stream + x.encode()