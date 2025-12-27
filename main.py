# main.py
import os
from src.cipher import BlowfishCipher

def main():
    print("=== DEMO BLOWFISH CIPHER ===")
    password = input("🔑 Nhập password (Key) chung cho phiên này: ")
    blowfish = BlowfishCipher(password)

    # Đảm bảo thư mục tồn tại
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/encrypted", exist_ok=True)
    os.makedirs("data/decrypted", exist_ok=True)

    while True:
        print("\n--- MENU ---")
        print("1. Mã hóa Text")
        print("2. Giải mã Text")
        print("3. Mã hóa File (trong data/input)")
        print("4. Giải mã File (trong data/encrypted)")
        print("0. Thoát")
        
        choice = input("Chọn chức năng: ")

        if choice == '1':
            txt = input("Nhập nội dung cần mã hóa: ")
            enc = blowfish.encrypt_text(txt)
            print(f"🔏 Kết quả (Base64): {enc}")

        elif choice == '2':
            enc_txt = input("Nhập chuỗi Base64 cần giải mã: ")
            dec = blowfish.decrypt_text(enc_txt)
            print(f"🔓 Nội dung gốc: {dec}")

        elif choice == '3':
            filename = input("Tên file trong data/input (vd: test.txt): ")
            in_path = os.path.join("data/input", filename)
            out_path = os.path.join("data/encrypted", filename + ".enc")
            
            if os.path.exists(in_path):
                blowfish.encrypt_file(in_path, out_path)
            else:
                print("❌ Không tìm thấy file!")

        elif choice == '4':
            filename = input("Tên file trong data/encrypted (vd: test.txt.enc): ")
            in_path = os.path.join("data/encrypted", filename)
            # Xóa đuôi .enc để lấy tên gốc
            orig_name = filename.replace(".enc", "") 
            out_path = os.path.join("data/decrypted", "restored_" + orig_name)
            
            if os.path.exists(in_path):
                blowfish.decrypt_file(in_path, out_path)
            else:
                print("❌ Không tìm thấy file!")

        elif choice == '0':
            break

if __name__ == "__main__":
    main()