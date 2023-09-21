import os
import json
import sys

# 명령줄에서 전달받은 디렉토리 경로 가져오기
if len(sys.argv) != 2:
    print("Usage: python ors2json.py <ors_directory>")
    sys.exit(1)

ors_directory = sys.argv[1]

# 디렉토리 내의 모든 파일 검색
result = {}

for filename in os.listdir(ors_directory):
    if filename.endswith(".ORS"):
        # ORS 파일 경로
        ors_file_path = os.path.join(ors_directory, filename)
        
        # 파일 이름을 결과에 추가
        result[filename] = {'PrintText': [], 'SetSELECT': []}
        
        try:
            # ORS 파일을 열고 읽기 모드로 데이터를 읽어옵니다.
            with open(ors_file_path, 'r', encoding='utf-8-sig') as file:
                for line in file:
                    # PrintText 태그 또는 SetSELECT 태그가 있는 열을 찾습니다.
                    if "[PrintText]=" in line:
                        # 쉼표로 문자열을 분할하고 2번째 값과 3번째 값을 문자열로 추출합니다.
                        parts = line.split(',')
                        if len(parts) >= 3:
                            value2 = parts[1].strip()
                            value3 = parts[2].strip()
                            result[filename]['PrintText'].append({'name': value2, 'string': value3})
                    elif "[SetSELECT]=" in line:
                        # 쉼표로 문자열을 분할하고 2번째 값과 3번째 값을 문자열로 추출합니다.
                        parts = line.split(',')
                        if len(parts) >= 3:
                            value2 = parts[1].strip()
                            value3 = parts[2].strip()
                            result[filename]['SetSELECT'].append({'sel1': value2, 'sel2': value3})
        except UnicodeDecodeError as e:
            print(f"오류 발생: {ors_file_path} 파일을 읽을 수 없음. UnicodeDecodeError 발생.")
            print(str(e))

# JSON 파일로 결과 저장
output_file_path = f'{ors_directory}.json'
with open(output_file_path, 'w', encoding='utf-8-sig') as output_file:
    json.dump(result, output_file, ensure_ascii=False, indent=4)

print(f"데이터가 {output_file_path}에 저장되었습니다.")
