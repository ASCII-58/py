"""
RSA加密解密工具
基于cryptography库实现RSA密钥生成、加密解密功能
作者: [你的名字]
日期: 2025-03-09
版本: 1.1 - 文件结构优化
"""

from cryptography.hazmat.backends import default_backend  # 加密后端
from cryptography.hazmat.primitives.asymmetric import rsa, padding  # RSA算法和填充模式
from cryptography.hazmat.primitives import serialization, hashes  # 序列化和哈希算法
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key  # 加载PEM格式密钥
import os  # 文件系统操作
import base64  # Base64编码
import re  # 正则表达式
import random
import string


def validate_password(password):
    """
    验证密码是否有效
    参数:
        password (str): 用户输入的密码
    返回:
        str: 有效密码，如果输入为空则返回默认密码'123456'
    """
    if not password:
        return '123456'  # 默认密码
    return password

def sanitize_filename(filename, max_length=20):
    """
    清理并验证文件名
    参数:
        filename (str): 原始文件名
        max_length (int): 最大文件名长度，默认20
    返回:
        str: 清理后的合法文件名，如果输入为空则返回None
    """
    if not filename:
        return None
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制长度
    return filename[:max_length]

def generate_rsa_keys(password, private_key_file="private.pem", public_key_file="public.pem"):
    """
    生成RSA密钥对
    参数:
        password (str): 用于加密私钥的密码
        private_key_file (str): 私钥保存路径，默认为"private.pem"
        public_key_file (str): 公钥保存路径，默认为"public.pem"
    返回:
        bool: 生成成功返回True，失败返回False
    """
    try:
        password = validate_password(password)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        )
        with open(f'RSAkey/{private_key_file}', 'wb') as f:
            f.write(private_pem)

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(f'RSAkey/{public_key_file}', 'wb') as f:
            f.write(public_pem)
            
        print("密钥对生成成功")
        return True
    except Exception as e:
        print(f"生成密钥对时出错: {e}")
        return False

def load_private_key(password, private_key_file="private.pem"):
    """
    加载PEM格式的私钥
    参数:
        password (str): 解密私钥所需的密码
        private_key_file (str): 私钥文件路径，默认为"private.pem"
    返回:
        RSAPrivateKey: 成功加载返回私钥对象，失败返回None
    """
    if not os.path.exists(f'RSAkey/{private_key_file}'):
        print(f"错误：私钥文件 {private_key_file} 不存在")
        return None
        
    try:
        with open(f'RSAkey/{private_key_file}', 'rb') as f:
            private_pem = f.read()
        return load_pem_private_key(private_pem, password.encode(), backend=default_backend())
    except ValueError:
        print("错误：密码不正确")
        return None
    except Exception as e:
        print(f"加载私钥时出错: {e}")
        return None

def load_public_key(public_key_file="public.pem"):
    """
    加载PEM格式的公钥
    参数:
        public_key_file (str): 公钥文件路径，默认为"public.pem"
    返回:
        RSAPublicKey: 成功加载返回公钥对象，失败返回None
    """
    if not os.path.exists(f'RSAkey/{public_key_file}'):
        print(f"错误：公钥文件 {public_key_file} 不存在")
        return None
        
    try:
        with open(f'RSAkey/{public_key_file}', 'rb') as f:
            public_pem = f.read()
        return load_pem_public_key(public_pem, backend=default_backend())
    except Exception as e:
        print(f"加载公钥时出错: {e}")
        return None

def encrypt_with_public_key(public_key, plaintext):
    """
    使用RSA公钥加密数据
    参数:
        public_key (RSAPublicKey): 公钥对象
        plaintext (str): 要加密的明文
    返回:
        bytes: 加密后的密文，失败返回None
    """
    try:
        if not plaintext:
            raise ValueError("加密文本不能为空")
            
        ciphertext = public_key.encrypt(
            plaintext.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    except Exception as e:
        print(f"加密时出错: {e}")
        return None

def decrypt_with_private_key(private_key, ciphertext):
    """
    使用RSA私钥解密数据
    参数:
        private_key (RSAPrivateKey): 私钥对象
        ciphertext (bytes): 要解密的密文
    返回:
        str: 解密后的明文，失败返回None
    """
    try:
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()
    except Exception as e:
        print(f"解密时出错: {e}")
        return None

def ensure_directories():
    """
    确保必要的目录结构存在
    - RSAkey: 存放密钥文件
    - encrypt: 存放加密后的文件
    - decrypt: 存放解密后的文件
    """
    required_dirs = ["RSAkey", "encrypt", "decrypt"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")

def encryption():
    """
    执行加密流程，优化文件管理
    步骤:
        1. 加载公钥
        2. 获取用户输入的加密文本
        3. 使用公钥加密文本
        4. 生成并验证加密文件名
        5. 保存加密结果到指定文件夹
    返回:
        bool: 加密成功返回True，失败返回False
    """
    # 加载公钥
    public_key = load_public_key()
    if not public_key:
        return False

    # 获取要加密的文本
    text = input("请输入要加密的文本: ").strip()
    if not text:
        print("错误：加密文本不能为空")
        return False

    # 加密数据
    ciphertext = encrypt_with_public_key(public_key, text)
    if not ciphertext:
        return False

    print("加密完成")

    # 处理文件名
    while True:
        file = input("请输入要保存的加密文件名(留空则使用自动生成的文件名): ").strip()
        if not file:
            file = f"encrypted_{random_string(10)}"
        else:
            file = sanitize_filename(file)
            
        # 完整路径
        filepath = os.path.join("encrypt", file)
        
        if not os.path.exists(filepath):
            break
        print(f"文件 {filepath} 已存在，请使用其他文件名")

    # 保存加密结果
    try:
        with open(filepath, 'wb') as f:
            f.write(ciphertext)
        print(f"加密结果已保存到文件: {filepath}")
        return True
    except Exception as e:
        print(f"保存加密结果时出错: {e}")
        return False

def decryption():
    """
    执行解密流程，优化文件管理
    步骤:
        1. 获取并验证用户输入的密码
        2. 加载私钥
        3. 显示可用的加密文件列表供选择
        4. 读取并解密文件内容
        5. 输出解密结果并保存到指定文件夹
    返回:
        bool: 解密成功返回True，失败返回False
    """
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        password = input("请输入密码: ").strip()
        private_key = load_private_key(password)
        if private_key:
            break
        attempts += 1
        if attempts < max_attempts:
            print(f"还剩 {max_attempts - attempts} 次尝试机会")
        else:
            print("密码错误次数过多，请稍后重试")
            return False

    # 显示可用的加密文件
    encrypt_dir = "encrypt"
    if not os.path.exists(encrypt_dir) or not os.listdir(encrypt_dir):
        print("未找到加密文件。请先加密一些内容。")
        return False
        
    print("\n可用的加密文件:")
    encrypted_files = os.listdir(encrypt_dir)
    for i, filename in enumerate(encrypted_files):
        print(f"{i+1}. {filename}")
    
    # 让用户选择文件
    while True:
        selection = input("\n请输入文件编号或文件名（输入q返回）: ").strip()
        
        if selection.lower() == 'q':
            return False
            
        # 尝试根据编号选择
        try:
            file_index = int(selection) - 1
            if 0 <= file_index < len(encrypted_files):
                file = os.path.join(encrypt_dir, encrypted_files[file_index])
                break
        except ValueError:
            # 不是数字，尝试作为文件名处理
            file = os.path.join(encrypt_dir, selection)
            if os.path.exists(file):
                break
            else:
                # 检查是否在encrypt目录中
                direct_file = selection
                if os.path.exists(direct_file):
                    file = direct_file
                    break
                
        print("无效的选择，请重新输入")

    # 读取并解密文件
    try:
        with open(file, 'rb') as f:
            ciphertext = f.read()
        
        original = decrypt_with_private_key(private_key, ciphertext)
        if original:
            print(f"解密完成\n解密结果: {original}")
            
            # 保存解密结果
            save_filename = input("请输入保存解密结果的文件名(留空自动生成): ").strip()
            if not save_filename:
                save_filename = f"decrypted_{random_string(10)}.txt"
            else:
                save_filename = sanitize_filename(save_filename)
                if not save_filename.endswith(".txt"):
                    save_filename += ".txt"
                    
            save_path = os.path.join("decrypt", save_filename)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(original)
            print(f"解密结果已保存至: {save_path}")
            return True
        return False
    except Exception as e:
        print(f"读取或解密文件时出错: {e}")
        return False

def random_string(length):
    # 定义字符集（包括大小写字母和数字）
    characters = string.ascii_letters + string.digits
    # 使用 random.choice 随机选择字符
    random_str = ''.join(random.choice(characters) for _ in range(length))
    return random_str


def main():
    """
    主程序入口
    功能:
        1. 检查并初始化必要的目录结构
        2. 检查并初始化RSA密钥对
        3. 提供加密/解密功能菜单
        4. 处理用户选择并执行相应操作
    """
    print("欢迎使用RSA加密解密工具")
    try:
        # 确保必要的目录结构存在
        ensure_directories()
        
        # 检查并生成密钥对
        if not (os.path.exists("RSAkey/private.pem") and os.path.exists("RSAkey/public.pem")):
            password = input("首次使用需要设置密码: ").strip()
            if not generate_rsa_keys(password):
                print("初始化失败，程序退出")
                return
            print("初始化完成")
        else:
            print("密钥对已存在")

        # 主循环
        while True:
            print("\n=== RSA加密解密工具 ===")
            print("1: 加密")
            print("2: 解密")
            print("3: 退出")
            
            try:
                choice = input("请选择操作 [1-3]: ").strip()
                
                if choice == "1":
                    encryption()
                elif choice == "2":
                    decryption()
                elif choice == "3":
                    graceful_exit()
                    break
                else:
                    print("无效的选择，请重新输入")
            except KeyboardInterrupt:
                print("\n检测到中断，正在安全退出...")
                graceful_exit()
                break
            except Exception as e:
                print(f"\n操作过程中出错: {e}")
                print("请重新尝试或选择其他操作")
                
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        graceful_exit()
    except Exception as e:
        print(f"\n程序遇到错误: {e}")
        graceful_exit()

def graceful_exit():
    """
    优雅地退出程序
    - 清理可能的临时文件
    - 显示退出信息
    """
    print("\n正在清理资源...", end="")
    
    # 删除可能存在的临时文件
    temp_files = [f for f in os.listdir('.') if f.startswith('temp_rsa_')]
    for file in temp_files:
        try:
            os.remove(file)
        except:
            pass
    
    print(" 完成")
    print("感谢使用RSA加密解密工具，再见！")

if __name__ == "__main__":
    main()
