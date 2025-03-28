import os

# 获取环境变量 PATH 的值
path_value = os.environ.get('PATH')

if path_value:
    print("环境变量 PATH 的值为:")
    print(path_value)
    with open('path.txt', 'w') as f:
        f.write(path_value)
        f.close()
else:
    print("未找到环境变量 PATH。")