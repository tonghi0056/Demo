# src/cipher.py
import struct
import os
import base64
import hashlib
from .utils import PaddingUtils
from .constants import P, S # Import mảng P và S từ file constants.py

class BlowfishCipher:
    def __init__(self, password: str):
        # Hash password để đảm bảo key an toàn, nhưng dùng 56 bytes max cho Blowfish
        key_bytes = hashlib.sha256(password.encode()).digest()
        
        # === KHỞI TẠO KEY (KEY EXPANSION) ===
        # Copy mảng P và S gốc để không làm hỏng dữ liệu gốc khi chạy nhiều lần
        self.P = P[:]
        self.S = [row[:] for row in S]
        
        key_len = len(key_bytes)
        p_len = len(self.P)

        # 1. XOR P-array với Key
        key_pos = 0
        for i in range(p_len):
            data = 0x00000000
            for k in range(4): # Ghép 4 bytes key thành 1 số 32-bit
                data = (data << 8) | key_bytes[key_pos]
                key_pos = (key_pos + 1) % key_len
            self.P[i] = self.P[i] ^ data

        # 2. Mã hóa mảng P và S bằng chính thuật toán Blowfish (với mảng P, S đang biến đổi)
        datal, datar = 0, 0
        
        # Cập nhật P-array
        for i in range(0, p_len, 2):
            datal, datar = self._encipher_block(datal, datar)
            self.P[i] = datal
            self.P[i+1] = datar

        # Cập nhật 4 S-boxes
        for i in range(4):
            for j in range(0, 256, 2):
                datal, datar = self._encipher_block(datal, datar)
                self.S[i][j] = datal
                self.S[i][j+1] = datar

    # --- CÁC HÀM CORE CỦA BLOWFISH ---
    
    def _F(self, x):
        """Hàm Feistel"""
        a = (x >> 24) & 0xFF
        b = (x >> 16) & 0xFF
        c = (x >> 8) & 0xFF
        d = x & 0xFF
        
        y = (self.S[0][a] + self.S[1][b]) & 0xFFFFFFFF
        y = y ^ self.S[2][c]
        y = (y + self.S[3][d]) & 0xFFFFFFFF
        return y

    def _encipher_block(self, xl, xr):
        """Mã hóa 1 khối 64-bit (2 số 32-bit L và R)"""
        for i in range(16):
            xl = xl ^ self.P[i]
            xr = self._F(xl) ^ xr
            # Swap
            xl, xr = xr, xl
        
        # Undo last swap
        xl, xr = xr, xl
        
        xr = xr ^ self.P[16]
        xl = xl ^ self.P[17]
        
        return xl, xr

    def _decipher_block(self, xl, xr):
        """Giải mã 1 khối 64-bit"""
        for i in range(17, 1, -1):
            xl = xl ^ self.P[i]
            xr = self._F(xl) ^ xr
            # Swap
            xl, xr = xr, xl
            
        # Undo last swap
        xl, xr = xr, xl
        
        xr = xr ^ self.P[1]
        xl = xl ^ self.P[0]
        
        return xl, xr

    # --- CÁC HÀM XỬ LÝ MODE CBC (TỰ CODE) ---

    def encrypt_cbc(self, data: bytes) -> bytes:
        """Mã hóa chế độ CBC thủ công"""
        # 1. Padding
        padded_data = PaddingUtils.pad(data)
        
        # 2. Tạo IV
        iv = os.urandom(8)
        iv_int_L, iv_int_R = struct.unpack(">II", iv) # Chuyển IV thành 2 số int
        
        encrypted_blocks = bytearray(iv) # 8 byte đầu là IV
        
        prev_L, prev_R = iv_int_L, iv_int_R # Vector khởi tạo
        
        # 3. Duyệt từng block 8 bytes
        for i in range(0, len(padded_data), 8):
            block = padded_data[i:i+8]
            block_L, block_R = struct.unpack(">II", block)
            
            # XOR với block trước (CBC logic)
            input_L = block_L ^ prev_L
            input_R = block_R ^ prev_R
            
            # Mã hóa
            out_L, out_R = self._encipher_block(input_L, input_R)
            
            # Lưu kết quả
            encrypted_blocks.extend(struct.pack(">II", out_L, out_R))
            
            # Cập nhật block trước cho vòng lặp sau
            prev_L, prev_R = out_L, out_R
            
        return bytes(encrypted_blocks)

    def decrypt_cbc(self, data: bytes) -> bytes:
        """Giải mã chế độ CBC thủ công"""
        if len(data) < 8:
            raise ValueError("Dữ liệu quá ngắn, thiếu IV")
            
        # 1. Tách IV
        iv = data[:8]
        iv_L, iv_R = struct.unpack(">II", iv)
        ciphertext = data[8:]
        
        decrypted_blocks = bytearray()
        prev_L, prev_R = iv_L, iv_R
        
        # 2. Duyệt từng block
        for i in range(0, len(ciphertext), 8):
            block = ciphertext[i:i+8]
            block_L, block_R = struct.unpack(">II", block) # Đây là Ciphertext hiện tại
            
            # Giải mã
            dec_L, dec_R = self._decipher_block(block_L, block_R)
            
            # XOR với Ciphertext của block trước (CBC logic)
            plain_L = dec_L ^ prev_L
            plain_R = dec_R ^ prev_R
            
            decrypted_blocks.extend(struct.pack(">II", plain_L, plain_R))
            
            # Cập nhật prev bằng chính Ciphertext hiện tại (để dùng cho block sau)
            prev_L, prev_R = block_L, block_R
            
        # 3. Unpad
        return PaddingUtils.unpad(bytes(decrypted_blocks))

    # --- CÁC HÀM GIAO TIẾP VỚI GUI (GIỮ NGUYÊN TÊN ĐỂ KHÔNG SỬA GUI) ---

    def encrypt_text(self, plain_text: str) -> str:
        data = plain_text.encode('utf-8')
        enc_data = self.encrypt_cbc(data)
        return base64.b64encode(enc_data).decode('utf-8')

    def decrypt_text(self, encrypted_b64: str) -> str:
        try:
            enc_data = base64.b64decode(encrypted_b64)
            dec_data = self.decrypt_cbc(enc_data)
            return dec_data.decode('utf-8')
        except Exception as e:
            return f"Lỗi giải mã: {str(e)}"

    def encrypt_file(self, input_path: str, output_path: str):
        with open(input_path, 'rb') as f:
            data = f.read()
        enc_data = self.encrypt_cbc(data)
        with open(output_path, 'wb') as f:
            f.write(enc_data)

    def decrypt_file(self, input_path: str, output_path: str):
        with open(input_path, 'rb') as f:
            data = f.read()
        dec_data = self.decrypt_cbc(data)
        with open(output_path, 'wb') as f:
            f.write(dec_data)