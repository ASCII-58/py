# Python 工具集

这个仓库包含了一系列实用的 Python 工具和脚本，用于各种日常任务和开发工作。

## 项目列表

### 1. RSA 加密解密工具

强大的命令行 RSA 加密解密工具，支持文本加密与文件解密。

**主要功能**:

- 自动生成 RSA 密钥对
- 文本加密并保存为文件
- 解密已加密的文件
- 文件结构化管理（加密文件和解密文件分开存储）

**使用方法**:

```bash
python RSA0.py
```

详细文档请参考：[RSA 工具使用手册](RSAReady_Manual.md)

### 2. Python 库管理器

图形界面的 Python 包管理工具，方便管理已安装的第三方库。

**主要功能**:

- 查看已安装的 Python 库
- 安装/卸载/升级第三方库
- 查看库详细信息
- 搜索库

**使用方法**:

```bash
python bank.py
```

### 3. 语音转文本工具

利用 VOSK 模型的离线语音识别工具，支持多种语言。

**主要功能**:

- 实时语音转写
- 音频文件转写
- 支持多种语言模型
- 自动语音检测和噪音过滤

## 环境要求

- Python 3.6+
- 各工具所需依赖库（详见各工具的说明文档）

## 安装指南

1. 克隆仓库:

```bash
git clone https://github.com/yourusername/py.git
cd py
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

## 贡献指南

欢迎提交 Pull Request 或 Issue 来改进项目！

## 许可证

MIT License
