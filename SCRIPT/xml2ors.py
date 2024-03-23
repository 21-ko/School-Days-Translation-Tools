import sys
import xml.etree.ElementTree as ET
import os

if len(sys.argv) != 2:
    print("Enter an XML file to use it.")
    sys.exit(1)

xml_filename = sys.argv[1]

# XML 파일을 불러옵니다
try:
    tree = ET.parse(xml_filename)
    root = tree.getroot()
    folder_name = os.path.splitext(os.path.basename(xml_filename))[0]  # 파일 이름에서 확장자 제거
except FileNotFoundError:
    print(f"The file {xml_filename} was not found.")
    sys.exit(1)

# 모든 파일 요소 찾기
file_elements = root.findall(".//File")

try:
    for file_element in file_elements:
        # File 요소의 name 속성 값 가져오기
        file_name = file_element.get("name")

        # 파일 경로 조합
        file_path = os.path.join("Script", folder_name, file_name)

        # 파일 열기
        with open(file_path, "r", encoding="utf-8-sig") as file:
            file_contents = file.read()

            # "[PrintText]"로 둘러싸인 문자열 찾기
            print_text_start = 0
            print_text_index = 0  # 인덱스를 사용하여 어떤 PrintText 요소를 사용할지 추적
            while print_text_start != -1:
                print_text_start = file_contents.find("[PrintText]=", print_text_start)
                if print_text_start != -1:
                    print_text_end = file_contents.find(";", print_text_start)
                    if print_text_end != -1:
                        print_text_str = file_contents[print_text_start + len("[PrintText]="):print_text_end]
                        # 문자열을 ','로 분리하여 b_column, c열의 문자열 찾기
                        print_text_parts = print_text_str.split(',')
                        if len(print_text_parts) > 2:
                            b_column = print_text_parts[1].strip()
                            c_column = print_text_parts[2].strip()

                            # 현재 PrintText 요소에서 텍스트를 가져옵니다
                            current_print_text = file_element.findall(".//PrintText")[print_text_index]

                            if current_print_text is not None:
                                new_b_column = current_print_text.get("name")  # 이름 속성 가져오기
                                new_c_column = current_print_text.text

                                # 수정된 텍스트에서 b_column 및 c_column 값 바꾸기
                                modified_print_text_str = print_text_str.replace(b_column, new_b_column).replace(c_column, new_c_column)

                                # file_contents의 텍스트를 수정된 텍스트로 바꿉니다.
                                file_contents = file_contents[:print_text_start + len("[PrintText]=")] + modified_print_text_str + file_contents[print_text_end:]

                                # 다음 대체를 위해 다음 PrintText 요소로 이동합니다.
                                print_text_index += 1

                    print_text_start = print_text_end  # 다음 탐색을 위해 시작 위치 갱신

            # "[SetSELECT]"로 둘러싸인 문자열 찾기
            set_select_start = 0
            set_select_index = 0  # 인덱스를 사용하여 어떤 SetSELECT 요소를 사용할지 추적
            while set_select_start != -1:
                set_select_start = file_contents.find("[SetSELECT]=", set_select_start)
                if set_select_start != -1:
                    set_select_end = file_contents.find(";", set_select_start)
                    if set_select_end != -1:
                        set_select_str = file_contents[set_select_start + len("[SetSELECT]="):set_select_end]
                        # 문자열을 ','로 분리하여 b_column, c열의 문자열 찾기
                        set_select_parts = set_select_str.split(',')
                        if len(set_select_parts) > 2:
                            b_column = set_select_parts[1].strip()
                            c_column = set_select_parts[2].strip()

                            # 현재 SetSELECT 요소 가져오기
                            current_set_select = file_element.findall(".//SetSELECT")[set_select_index]

                            if current_set_select is not None:
                                new_b_column = current_set_select.get("sel1")  # sel1 속성 가져오기
                                new_c_column = current_set_select.get("sel2")  # sel2 속성 가져오기

                                # 수정된 텍스트에서 b_column 및 c_column 값 바꾸기
                                modified_set_select_str = set_select_str.replace(b_column, new_b_column).replace(c_column, new_c_column)

                                # file_contents의 텍스트를 수정된 텍스트로 바꿉니다
                                file_contents = file_contents[:set_select_start + len("[SetSELECT]=")] + modified_set_select_str + file_contents[set_select_end:]

                                # 다음 교체를 위해 다음 SetSELECT 요소로 이동합니다
                                set_select_index += 1

                    set_select_start = set_select_end  # 다음 탐색을 위해 시작 위치 갱신

            # 수정된 내용을 새 파일에 저장
            new_file_name = file_name  # 새 파일 이름
            new_folder_path = os.path.join("New", folder_name)
            new_file_path = os.path.join("New", folder_name, new_file_name)
            
            if new_folder_path and not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            
            with open(new_file_path, "w", encoding="utf-8-sig") as new_file:
                new_file.write(file_contents)

except FileNotFoundError:
    print(f"The file {file_name} was not found in the directory.")
