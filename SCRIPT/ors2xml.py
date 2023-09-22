import os
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# 명령줄에서 전달받은 디렉토리 경로 가져오기
if len(sys.argv) != 2:
    print("Usage: python ors2xml.py <ors_directory>")
    sys.exit(1)

ors_directory = sys.argv[1]

# 루트 XML 엘리먼트 생성
root = ET.Element("ORSData")

# 디렉토리 내의 모든 파일 검색
for filename in os.listdir(ors_directory):
    if filename.endswith(".ORS"):
        # ORS 파일 경로
        ors_file_path = os.path.join(ors_directory, filename)
        
        # 파일 이름을 결과에 추가
        file_element = ET.SubElement(root, "File")
        file_element.set("name", filename)
        
        try:
            # ORS 파일을 열고 읽기 모드로 데이터를 읽어옵니다.
            with open(ors_file_path, 'r', encoding='sjis') as file:
                for line in file:
                    # PrintText 태그 또는 SetSELECT 태그가 있는 열을 찾습니다.
                    if "[PrintText]=" in line:
                        # 쉼표로 문자열을 분할하고 2번째 값과 3번째 값을 문자열로 추출합니다.
                        parts = line.split(',')
                        if len(parts) >= 3:
                            print_text_element = ET.SubElement(file_element, "PrintText")
                            print_text_element.set("name", parts[1].strip())
                            print_text_element.text = parts[2].strip()
                    elif "[SetSELECT]=" in line:
                        # 쉼표로 문자열을 분할하고 2번째 값과 3번째 값을 문자열로 추출합니다.
                        parts = line.split(',')
                        if len(parts) >= 3:
                            set_select_element = ET.SubElement(file_element, "SetSELECT")
                            set_select_element.set("sel1", parts[1].strip())
                            set_select_element.set("sel2", parts[2].strip())
        except UnicodeDecodeError as e:
            print(f"오류 발생: {ors_file_path} 파일을 읽을 수 없음. UnicodeDecodeError 발생.")
            print(str(e))

# XML 파일로 결과 저장 (인덴트 설정 추가)
output_file_path = f'{ors_directory}.xml'
tree = ET.ElementTree(root)
xml_string = ET.tostring(root, encoding='utf-8')
dom = minidom.parseString(xml_string)
with open(output_file_path, 'wb') as output_file:
    output_file.write(dom.toprettyxml(encoding='utf-8'))

print(f"데이터가 {output_file_path}에 저장되었습니다.")
