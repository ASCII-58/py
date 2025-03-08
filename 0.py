import pandas as pd
def new_feather():
    # 创建一个示例 DataFrame
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'Score': [85.5, 90.0, 88.5]
    }
    df = pd.DataFrame(data)

    # 将 DataFrame 写入 Feather 文件
    df.to_feather('output.feather')  # `index=False` 表示不保存索引
