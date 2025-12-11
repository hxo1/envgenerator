#!/usr/bin/env python3
"""
Minimal cryptography module wrapper using ctypes and OpenSSL
This is a workaround for when the cryptography package is not available
"""
import ctypes
import ctypes.util
from ctypes import c_void_p, c_char_p, c_int, c_uint, c_ulong, POINTER, byref

# Load OpenSSL library
libcrypto = ctypes.CDLL('/usr/lib64/libcrypto.so.3')

# Define necessary OpenSSL functions
libcrypto.EVP_CIPHER_CTX_new.restype = c_void_p
libcrypto.EVP_CIPHER_CTX_free.argtypes = [c_void_p]
libcrypto.EVP_aes_256_gcm.restype = c_void_p
libcrypto.EVP_DecryptInit_ex.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p, c_char_p]
libcrypto.EVP_DecryptInit_ex.restype = c_int
libcrypto.EVP_CIPHER_CTX_ctrl.argtypes = [c_void_p, c_int, c_int, c_void_p]
libcrypto.EVP_CIPHER_CTX_ctrl.restype = c_int
libcrypto.EVP_DecryptUpdate.argtypes = [c_void_p, c_char_p, POINTER(c_int), c_char_p, c_int]
libcrypto.EVP_DecryptUpdate.restype = c_int
libcrypto.EVP_DecryptFinal_ex.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
libcrypto.EVP_DecryptFinal_ex.restype = c_int
libcrypto.PKCS5_PBKDF2_HMAC.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int, c_void_p, c_int, c_char_p]
libcrypto.PKCS5_PBKDF2_HMAC.restype = c_int
libcrypto.EVP_sha256.restype = c_void_p

# Constants
EVP_CTRL_GCM_SET_IVLEN = 0x9
EVP_CTRL_GCM_SET_TAG = 0x11

class CryptoWrapper:
    @staticmethod
    def pbkdf2_hmac_sha256(password, salt, iterations, key_length):
        """Derive a key using PBKDF2-HMAC-SHA256"""
        key = ctypes.create_string_buffer(key_length)
        result = libcrypto.PKCS5_PBKDF2_HMAC(
            password,
            len(password),
            salt,
            len(salt),
            iterations,
            libcrypto.EVP_sha256(),
            key_length,
            key
        )
        if result != 1:
            raise Exception("PBKDF2 key derivation failed")
        return bytes(key)
    
    @staticmethod
    def aes_gcm_decrypt(key, nonce, tag, ciphertext):
        """Decrypt using AES-256-GCM"""
        # Create cipher context
        ctx = libcrypto.EVP_CIPHER_CTX_new()
        if not ctx:
            raise Exception("Failed to create cipher context")
        
        try:
            # Initialize decryption
            if libcrypto.EVP_DecryptInit_ex(ctx, libcrypto.EVP_aes_256_gcm(), None, None, None) != 1:
                raise Exception("Failed to initialize decryption")
            
            # Set IV (nonce) length
            if libcrypto.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, len(nonce), None) != 1:
                raise Exception("Failed to set IV length")
            
            # Set key and IV
            if libcrypto.EVP_DecryptInit_ex(ctx, None, None, key, nonce) != 1:
                raise Exception("Failed to set key and IV")
            
            # Decrypt the ciphertext
            plaintext = ctypes.create_string_buffer(len(ciphertext) + 16)
            outlen = c_int()
            
            if libcrypto.EVP_DecryptUpdate(ctx, plaintext, byref(outlen), ciphertext, len(ciphertext)) != 1:
                raise Exception("Failed to decrypt")
            
            plaintext_len = outlen.value
            
            # Set expected tag value
            tag_buf = ctypes.create_string_buffer(tag)
            if libcrypto.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, len(tag), tag_buf) != 1:
                raise Exception("Failed to set authentication tag")
            
            # Finalize decryption (this verifies the tag)
            if libcrypto.EVP_DecryptFinal_ex(ctx, plaintext[plaintext_len:], byref(outlen)) != 1:
                raise Exception("Decryption failed - authentication tag verification failed")
            
            plaintext_len += outlen.value
            
            return bytes(plaintext[:plaintext_len])
            
        finally:
            libcrypto.EVP_CIPHER_CTX_free(ctx)

# Create a module-like namespace for compatibility
class hazmat:
    class primitives:
        class hashes:
            class SHA256:
                name = "sha256"
        
        class kdf:
            class pbkdf2:
                class PBKDF2HMAC:
                    def __init__(self, algorithm, length, salt, iterations, backend=None):
                        self.algorithm = algorithm
                        self.length = length
                        self.salt = salt
                        self.iterations = iterations
                    
                    def derive(self, password):
                        return CryptoWrapper.pbkdf2_hmac_sha256(password, self.salt, self.iterations, self.length)
        
        class ciphers:
            class algorithms:
                class AES:
                    def __init__(self, key):
                        self.key = key
            
            class modes:
                class GCM:
                    def __init__(self, nonce, tag=None):
                        self.nonce = nonce
                        self.tag = tag
            
            class Cipher:
                def __init__(self, algorithm, mode, backend=None):
                    self.algorithm = algorithm
                    self.mode = mode
                
                def decryptor(self):
                    return AESGCMDecryptor(self.algorithm.key, self.mode.nonce, self.mode.tag)
    
    class backends:
        @staticmethod
        def default_backend():
            return None

class AESGCMDecryptor:
    def __init__(self, key, nonce, tag):
        self.key = key
        self.nonce = nonce
        self.tag = tag
        self.buffer = b''
    
    def update(self, ciphertext):
        self.buffer += ciphertext
        return b''
    
    def finalize(self):
        result = CryptoWrapper.aes_gcm_decrypt(self.key, self.nonce, self.tag, self.buffer)
        self.buffer = b''
        return result

if __name__ == '__main__':
    # Test
    import base64
    
    # Test PBKDF2
    password = b"test"
    salt = b"saltsalt"
    key = CryptoWrapper.pbkdf2_hmac_sha256(password, salt, 100000, 32)
    print(f"Derived key (first 16 bytes): {key[:16].hex()}")
    
    print("Crypto wrapper module loaded successfully")
