import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import struct
import zlib
import io
from tkinter.ttk import Progressbar

class ByteStringEncryptedStream(io.BufferedIOBase):
    def __init__(self, main, CIPHERCODE, start_pos=0):
        self.main = main
        self.CIPHERCODE = CIPHERCODE
        self.base_pos = start_pos % len(CIPHERCODE)
        self.pos = 0

    def read(self, size=-1):
        data = self.main.read(size)
        decrypted_data = bytearray(data)
        for i in range(len(data)):
            decrypted_data[i] ^= self.CIPHERCODE[(self.base_pos + self.pos) % len(self.CIPHERCODE)]
            self.pos += 1
        return bytes(decrypted_data)

    def readinto(self, b):
        size = len(b)
        data = self.main.read(size)
        for i in range(size):
            b[i] = data[i] ^ self.CIPHERCODE[(self.base_pos + self.pos) % len(self.CIPHERCODE)]
            self.pos += 1
        return len(data)

def archive_files(input_folder, output_filename, progress_bar):
    archive_data = bytearray()
    file_info_entries = []

    total_files = sum(len(files) for _, _, files in os.walk(input_folder))
    progress_step = 100 / total_files
    progress = 0

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, 'rb') as file:
                file_data = file.read()
                archive_data.extend(file_data)

                relative_path = os.path.relpath(file_path, input_folder)
                relative_path = relative_path.replace('\\', '/')
                filename_bytes = relative_path.encode('utf-16-le')
                dummy_6bytes = b'\x00\x00\x00\x00\x00\x00'
                dummy_5bytes = b'\x00\x00\x00\x00\x00'
                offset = len(archive_data) - len(file_data)
                size = len(file_data)

                file_info_entry = struct.pack('<H', len(filename_bytes) // 2) + filename_bytes + dummy_6bytes + struct.pack('<I', offset) + struct.pack('<I', size) + b'\x20\x20\x20\x20' + dummy_5bytes
                file_info_entries.append(file_info_entry)

            progress += progress_step
            progress_bar["value"] = progress
            window.update_idletasks()

    file_info_data = b''.join(file_info_entries)
    file_info_data += b'\x00\x00\x00\x00'
    uncompressed_file_info_size = len(file_info_data)
    compressed_file_info_data = zlib.compress(file_info_data)
    compressed_file_info_data = struct.pack('<I', uncompressed_file_info_size) + compressed_file_info_data

    CIPHERCODE = bytearray([0x56, 0x7C, 0x1B, 0x90, 0xB6, 0xFE, 0x3F, 0xDB, 0xB6, 0x06, 0x79, 0xEA, 0xCC, 0x11, 0xA0, 0x4F])
    encrypted_file_info_data = ByteStringEncryptedStream(io.BytesIO(compressed_file_info_data), CIPHERCODE)

    archive_data.extend(encrypted_file_info_data.read())
    archive_data.extend("STKFile0PIDX".encode('ascii'))
    archive_data.extend(struct.pack('<I', len(compressed_file_info_data)))
    archive_data.extend("STKFile0PACKFILE".encode('ascii'))

    with open(output_filename, 'wb') as output_file:
        output_file.write(archive_data)

def browse_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, folder_selected)

def browse_output_file():
    file_selected = filedialog.asksaveasfilename(defaultextension=".GPK")
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, file_selected)

def create_archive():
    input_folder = input_folder_entry.get()
    output_filename = output_file_entry.get()

    if not input_folder or not output_filename:
        messagebox.showerror("Error", "Please select input folder and output file.")
        return

    try:
        archive_files(input_folder, output_filename, progress_bar)
        messagebox.showinfo("Success", "Archive created successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# GUI 생성
window = tk.Tk()
window.title("File Archiver")

# 입력 폴더 선택
input_folder_label = tk.Label(window, text="Input Folder:")
input_folder_label.pack()
input_folder_entry = tk.Entry(window)
input_folder_entry.pack()
browse_input_button = tk.Button(window, text="Browse", command=browse_input_folder)
browse_input_button.pack()

# 출력 파일 선택
output_file_label = tk.Label(window, text="Output File:")
output_file_label.pack()
output_file_entry = tk.Entry(window)
output_file_entry.pack()
browse_output_button = tk.Button(window, text="Browse", command=browse_output_file)
browse_output_button.pack()

# 프로그레스 바 추가
progress_bar = Progressbar(window, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()

# 아카이브 생성 버튼
create_button = tk.Button(window, text="Create Archive", command=create_archive)
create_button.pack()

window.mainloop()
