# src/utils.py (Giữ nguyên hoặc dùng code này)
class PaddingUtils:
    BLOCK_SIZE = 8

    @staticmethod
    def pad(data: bytes) -> bytes:
        padding_len = PaddingUtils.BLOCK_SIZE - (len(data) % PaddingUtils.BLOCK_SIZE)
        padding = bytes([padding_len] * padding_len)
        return data + padding

    @staticmethod
    def unpad(data: bytes) -> bytes:
        if not data:
            return b""
        padding_len = data[-1]
        if padding_len > PaddingUtils.BLOCK_SIZE or padding_len == 0:
             # Trường hợp lỗi padding (do sai key giải mã ra rác)
             raise ValueError("Invalid padding")
        return data[:-padding_len]