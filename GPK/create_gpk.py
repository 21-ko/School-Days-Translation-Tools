import os
import struct
import zlib
import io

class ByteStringEncryptedStream(io.BufferedIOBase):
    def __init__(self, main, CIPHERCODE, start_pos=0):  # key
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

def archive_files(input_folder, output_filename):
    # 파일을 합치기 위한 바이트 배열
    archive_data = bytearray()

    # 파일 정보를 저장하기 위한 리스트
    file_info_entries = []

    # 입력 폴더에서 모든 파일 목록 가져오기 (하위 폴더 포함)
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, 'rb') as file:
                file_data = file.read()
                archive_data.extend(file_data)

                # 파일 정보를 생성하고 리스트에 추가
                # 파일 경로에서 input_folder를 제외한 부분을 사용하여 파일 이름 작성
                relative_path = os.path.relpath(file_path, input_folder)
                # '\'를 '/'로 대체하여 사용
                relative_path = relative_path.replace('\\', '/')
                filename_bytes = relative_path.encode('utf-16-le')
                dummy_6bytes = b'\x00\x00\x00\x00\x00\x00'
                dummy_5bytes = b'\x00\x00\x00\x00\x00'
                offset = len(archive_data) - len(file_data)  # 현재까지의 길이에서 현재 파일의 길이를 뺍니다.
                size = len(file_data)

                file_info_entry = struct.pack('<H', len(filename_bytes) // 2) + filename_bytes + dummy_6bytes + struct.pack('<I', offset) + struct.pack('<I', size) + b'\x20\x20\x20\x20' + dummy_5bytes
                file_info_entries.append(file_info_entry)

    # 인포메이션 데이터를 합치기
    file_info_data = b''.join(file_info_entries)

    # 인포메이션 맨 끝에 0x00 4바이트 추가
    file_info_data += b'\x00\x00\x00\x00'

    # 압축되기 전 인포메이션 데이터의 크기를 4바이트로 추가
    uncompressed_file_info_size = len(file_info_data)

    # 인포메이션 데이터를 압축
    compressed_file_info_data = zlib.compress(file_info_data)

    # 압축되기 전 인포메이션 데이터의 크기를 compressed_file_info_data 맨 앞에 4바이트로 추가
    compressed_file_info_data = struct.pack('<I', uncompressed_file_info_size) + compressed_file_info_data

    # 인포메이션 데이터를 암호화
    CIPHERCODE = bytearray([0x56, 0x7C, 0x1B, 0x90, 0xB6, 0xFE, 0x3F, 0xDB, 0xB6, 0x06, 0x79, 0xEA, 0xCC, 0x11, 0xA0, 0x4F])
    encrypted_file_info_data = ByteStringEncryptedStream(io.BytesIO(compressed_file_info_data), CIPHERCODE)

    # 아카이브 데이터에 암호화된 인포메이션 데이터 추가
    archive_data.extend(encrypted_file_info_data.read())  # 암호화된 인포메이션 데이터 추가

    # 마지막 구조체 쓰기 (푸터)
    archive_data.extend("STKFile0PIDX".encode('ascii'))
    archive_data.extend(struct.pack('<I', len(compressed_file_info_data)))
    archive_data.extend("STKFile0PACKFILE".encode('ascii'))

    # 결과를 출력 파일에 쓰기
    with open(output_filename, 'wb') as output_file:
        output_file.write(archive_data)

if __name__ == "__main__":
    # 패킹할 파일이 있는 폴더 경로
    input_folder = "Script"

    # 결과 아카이브 파일 이름
    output_filename = "Script.GPK"

    archive_files(input_folder, output_filename)
