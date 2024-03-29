from PIL import Image, ImageDraw, ImageFont
import numpy as np
import sys
import os
import json

bitmap_size = (48, 48)
header_size = 0x40000  # 고정 헤더 크기

background_color = (0, 128, 128)
main_color = (15, 248, 0)
outline_color = (15, 160, 0)

# 비트맵 글꼴을 그리고 이미 합친 바이너리 파일에 저장하는 함수
def create_and_combine_bitmap_font(characters, font_path, output_file):
    # 비트맵 이미지를 저장할 리스트
    images = []

    # 헤더에 사용할 공백 바이트 추가
    header = bytearray(header_size)

    # 글자별 offset 정보를 저장할 딕셔너리 초기화
    offsets = {}

    # 첫 번째 글자를 생성하고 이미지 데이터 추출
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('YCbCr', bitmap_size, color=background_color)
    draw = ImageDraw.Draw(image)
    
    # 테두리 텍스트 그리기 (겹쳐 그리기)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                draw.text((0 + dx, 0 + dy), characters[0], font=font, fill=outline_color)
    
    # 원래 텍스트 그리기
    draw.text((0, 0), characters[0], font=font, fill=main_color)

    # 16비트로 변환
    yuv_image = np.array(image)
    yuv_image = yuv_image.astype(np.uint16)
    yuv_image = yuv_image[:,:,0] << 8 | yuv_image[:,:,1]
    
    images.append(yuv_image.tobytes())
    
    offset = header_size  # 첫번째 문자는 헤더 크기만 고려
    offsets[characters[0]] = offset

    # 나머지 글자를 생성하고 이미지 데이터와 offset 정보를 추가
    for character in characters[1:]:
        image = Image.new('YCbCr', bitmap_size, color=background_color)
        draw = ImageDraw.Draw(image)
        
        # 테두리 텍스트 그리기 (겹쳐 그리기)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text((0 + dx, 0 + dy), character, font=font, fill=outline_color)
        
        # 원래 텍스트 그리기
        draw.text((0, 0), character, font=font, fill=main_color)
        
        # 16비트로 변환
        yuv_image = np.array(image)
        yuv_image = yuv_image.astype(np.uint16)
        yuv_image = yuv_image[:,:,0] << 8 | yuv_image[:,:,1]
        
        images.append(yuv_image.tobytes())
        
        offset += len(yuv_image.tobytes()) + 1  # 이미지 길이와 0x00 바이트 고려
        offsets[character] = offset

    # offset 정보를 헤더에 저장
    for character, offset in offsets.items():
        header_offset = int.from_bytes(character.encode('utf-16le'), byteorder='little') * 4
        header[header_offset:header_offset + 4] = offset.to_bytes(4, byteorder='little')

    # 저장, 이미지 데이터 및 0x00 추가
    with open(output_file, 'wb') as combined_file:
        combined_file.write(header)
        for image_data in images:
            combined_file.write(image_data)
            combined_file.write(b'\x00')

# 실행
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong execution: Drag and drop the JSON file to run it.")
        os.system("pause")
        sys.exit(1)

    json_file_path = sys.argv[1]

    # JSON 파일을 읽어옴
    try:
        with open(json_file_path, 'r', encoding='utf-8-sig') as json_file:
            font_info = json.load(json_file)

        # JSON 데이터에서 필요한 정보 추출
        font_path = font_info["font_path"]
        font_size = font_info["font_size"]
        characters_to_draw = font_info["characters_to_draw"]

        if font_size >= 49:
            print("Font size must be less than 49. Exiting...")
            sys.exit(1)

        output_file = 'FONTDATA.DAT'

        create_and_combine_bitmap_font(characters_to_draw, font_path, output_file)

    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        sys.exit(1)
