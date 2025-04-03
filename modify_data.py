import os
import chardet  # 自动检测文件编码

def detect_encoding(file_path):
    """ 检测文件编码 """
    with open(file_path, "rb") as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result["encoding"]

def process_txt_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):  # 只处理 .txt 文件
            file_path = os.path.join(directory, filename)
            
            # 自动检测文件编码
            encoding = detect_encoding(file_path)
            if encoding is None:
                print(f"无法检测 {filename} 的编码，跳过该文件。")
                continue

            # 读取文件内容
            with open(file_path, "r", encoding=encoding, errors="ignore") as file:
                lines = file.readlines()
            
            # 修改第一列是 '2' 的行，将其改为 '1'
            modified_lines = []
            for line in lines:
                parts = line.strip().split()
                if parts and parts[0] == '2':
                    parts[0] = '1'
                modified_lines.append(" ".join(parts))
            
            # 重新写回文件，使用 UTF-8 保存
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(modified_lines) + "\n")

if __name__ == "__main__":
    directory = os.getcwd() + '\\datasets\\train\\labels'
    process_txt_files(directory)
    print("所有 txt 文件处理完成！")
