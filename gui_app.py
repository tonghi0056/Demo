import customtkinter as ctk
from tkinter import filedialog
import os
from src.cipher import BlowfishCipher

# Cấu hình giao diện (Dark mode & Màu xanh dương chủ đạo)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BlowfishApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ chính
        self.title("Blowfish Cipher Demo")
        self.geometry("700x550")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === PHẦN NHẬP KEY (PASSWORD) ===
        self.frame_key = ctk.CTkFrame(self)
        self.frame_key.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_key = ctk.CTkLabel(self.frame_key, text="🔑 Secret Key:", font=("Arial", 14, "bold"))
        self.label_key.pack(side="left", padx=10)
        
        self.entry_key = ctk.CTkEntry(self.frame_key, placeholder_text="Nhập mật khẩu mã hóa/giải mã...", width=400, show="*")
        self.entry_key.pack(side="left", padx=10, pady=10)

        # === TABVIEW (CHIA 2 TAB: TEXT & FILE) ===
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.tab_text = self.tabview.add("Text Processing")
        self.tab_file = self.tabview.add("File Processing")

        # --- SETUP GIAO DIỆN TAB TEXT ---
        self.setup_text_tab()
        
        # --- SETUP GIAO DIỆN TAB FILE ---
        self.setup_file_tab()

    def get_cipher(self):
        """Hàm lấy key và tạo đối tượng Cipher"""
        key = self.entry_key.get()
        if not key:
            # Nếu chưa nhập key thì báo lỗi nhẹ
            return None
        return BlowfishCipher(key)

    # ==========================================
    # LOGIC TAB TEXT
    # ==========================================
    def setup_text_tab(self):
        # Input Text
        self.lbl_input = ctk.CTkLabel(self.tab_text, text="Input Text:", anchor="w")
        self.lbl_input.pack(fill="x", padx=10, pady=(10, 0))
        
        self.txt_input = ctk.CTkTextbox(self.tab_text, height=100)
        self.txt_input.pack(fill="x", padx=10, pady=5)

        # Buttons Row
        self.btn_frame = ctk.CTkFrame(self.tab_text, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=10, pady=10)

        self.btn_encrypt = ctk.CTkButton(self.btn_frame, text="⬇️ Encrypt (Mã hóa)", command=self.on_encrypt_text)
        self.btn_encrypt.pack(side="left", expand=True, padx=5)

        self.btn_decrypt = ctk.CTkButton(self.btn_frame, text="⬆️ Decrypt (Giải mã)", command=self.on_decrypt_text, fg_color="green")
        self.btn_decrypt.pack(side="left", expand=True, padx=5)

        # Output Text
        self.lbl_output = ctk.CTkLabel(self.tab_text, text="Result (Base64 / Plaintext):", anchor="w")
        self.lbl_output.pack(fill="x", padx=10, pady=(10, 0))
        
        self.txt_output = ctk.CTkTextbox(self.tab_text, height=100, state="disabled") # Mặc định chỉ đọc
        self.txt_output.pack(fill="x", padx=10, pady=5)

    def on_encrypt_text(self):
        cipher = self.get_cipher()
        if not cipher:
            self.show_output("⚠️ Vui lòng nhập Secret Key trước!")
            return
        
        inp = self.txt_input.get("1.0", "end-1c") # Lấy text input
        if not inp.strip():
            return
        
        try:
            res = cipher.encrypt_text(inp)
            self.show_output(res)
        except Exception as e:
            self.show_output(f"Error: {e}")

    def on_decrypt_text(self):
        cipher = self.get_cipher()
        if not cipher:
            self.show_output("⚠️ Vui lòng nhập Secret Key trước!")
            return

        inp = self.txt_input.get("1.0", "end-1c")
        try:
            res = cipher.decrypt_text(inp)
            self.show_output(res)
        except Exception as e:
            self.show_output(f"Error: {e}")

    def show_output(self, text):
        self.txt_output.configure(state="normal") # Mở khóa để ghi
        self.txt_output.delete("1.0", "end")
        self.txt_output.insert("1.0", text)
        self.txt_output.configure(state="disabled") # Khóa lại

    # ==========================================
    # LOGIC TAB FILE
    # ==========================================
    def setup_file_tab(self):
        self.file_path = None

        # Nút chọn file
        self.btn_select = ctk.CTkButton(self.tab_file, text="📂 Chọn File (Input)", command=self.select_file)
        self.btn_select.pack(pady=20)

        self.lbl_file_path = ctk.CTkLabel(self.tab_file, text="Chưa chọn file nào", text_color="gray")
        self.lbl_file_path.pack(pady=5)

        # Các nút xử lý
        self.file_action_frame = ctk.CTkFrame(self.tab_file, fg_color="transparent")
        self.file_action_frame.pack(pady=20)

        self.btn_enc_file = ctk.CTkButton(self.file_action_frame, text="🔒 Mã hóa File", command=self.on_encrypt_file, state="disabled")
        self.btn_enc_file.pack(side="left", padx=10)

        self.btn_dec_file = ctk.CTkButton(self.file_action_frame, text="🔓 Giải mã File", command=self.on_decrypt_file, state="disabled", fg_color="green")
        self.btn_dec_file.pack(side="left", padx=10)

        # Log trạng thái
        self.lbl_status = ctk.CTkLabel(self.tab_file, text="", font=("Arial", 12, "italic"))
        self.lbl_status.pack(pady=20)

    def select_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_path = filename
            self.lbl_file_path.configure(text=f"File: {os.path.basename(filename)}", text_color="white")
            self.btn_enc_file.configure(state="normal")
            self.btn_dec_file.configure(state="normal")

    def on_encrypt_file(self):
        cipher = self.get_cipher()
        if not cipher:
            self.lbl_status.configure(text="⚠️ Chưa nhập Key!", text_color="red")
            return
        
        try:
            output_path = self.file_path + ".enc"
            cipher.encrypt_file(self.file_path, output_path)
            self.lbl_status.configure(text=f"✅ Đã mã hóa xong!\nLưu tại: {os.path.basename(output_path)}", text_color="#00FF00")
        except Exception as e:
            self.lbl_status.configure(text=f"Lỗi: {e}", text_color="red")

    def on_decrypt_file(self):
        cipher = self.get_cipher()
        if not cipher:
            self.lbl_status.configure(text="⚠️ Chưa nhập Key!", text_color="red")
            return

        try:
            # Tự động xóa đuôi .enc nếu có để tạo tên file giải mã
            base_name = os.path.basename(self.file_path).replace(".enc", "")
            output_path = os.path.join(os.path.dirname(self.file_path), "decrypted_" + base_name)
            
            cipher.decrypt_file(self.file_path, output_path)
            self.lbl_status.configure(text=f"✅ Đã giải mã xong!\nLưu tại: decrypted_{base_name}", text_color="#00FF00")
        except Exception as e:
            self.lbl_status.configure(text=f"Lỗi giải mã: {e}", text_color="red")

if __name__ == "__main__":
    app = BlowfishApp()
    app.mainloop()