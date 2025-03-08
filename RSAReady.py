from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import os
import base64



# 生成 RSA 密钥对并保存到 PEM 文件
def generate_rsa_keys(password,PrivateKeyFile="private.pem", PublicKeyFile="public.pem"):
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    if password=='':password='123456'
    # 序列化私钥并保存到文件
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,  # 使用 PEM 编码格式
        format=serialization.PrivateFormat.PKCS8,  # 使用 PKCS8 格式
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())  # 不加密私钥
    )
    with open(PrivateKeyFile, 'wb') as f:
        f.write(private_pem)

    # 从私钥生成公钥
    public_key = private_key.public_key()
    # 序列化公钥并保存到文件
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,  # 使用 PEM 编码格式
        format=serialization.PublicFormat.SubjectPublicKeyInfo  # 使用 SubjectPublicKeyInfo 格式
    )
    with open(PublicKeyFile, 'wb') as f:
        f.write(public_pem)
    print(f"私钥已保存到 {PrivateKeyFile}")
    print(f"公钥已保存到 {PublicKeyFile}")
    

# 加载私钥
def load_private_key(password,PrivateKeyFile="private.pem"):
    """
    从文件中加载私钥。
    
    :param PrivateKeyFile: 私钥文件路径，默认为 "private.pem"
    :return: 加载的私钥对象
    """
    try:
        with open(PrivateKeyFile, 'rb') as f:
            private_pem = f.read()
        private_key = load_pem_private_key(private_pem, password.encode(), backend=default_backend())
        return private_key
    except Exception as e:
        print(f"加载私钥时出错: {e}")
        return None

# 加载公钥
def load_public_key(PublicKeyFile="public.pem"):
    """
    从文件中加载公钥。
    
    :param PublicKeyFile: 公钥文件路径，默认为 "public.pem"
    :return: 加载的公钥对象
    """
    with open(PublicKeyFile, 'rb') as f:
        public_pem = f.read()
    public_key = load_pem_public_key(public_pem, backend=default_backend())
    return public_key

# 使用公钥加密数据
def encrypt_with_public_key(public_key, plaintext):
    """
    使用公钥加密数据。
    
    :param public_key: 公钥对象
    :param plaintext: 待加密的明文数据
    :return: 加密后的密文数据
    """
    ciphertext = public_key.encrypt(
        plaintext.encode(),  # 将明文编码为字节
        padding.OAEP(  # 使用 OAEP 填充
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # 使用 SHA256 作为 MGF1 的哈希算法
            algorithm=hashes.SHA256(),  # 使用 SHA256 作为哈希算法
            label=None  # 不使用标签
        )
    )
    return ciphertext

# 使用私钥解密数据
def decrypt_with_private_key(private_key, ciphertext):
    """
    使用私钥解密数据。
    
    :param private_key: 私钥对象
    :param ciphertext: 待解密的密文数据
    :return: 解密后的明文数据
    """
    plaintext = private_key.decrypt(
        ciphertext,  # 待解密的密文
        padding.OAEP(  # 使用 OAEP 填充
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # 使用 SHA256 作为 MGF1 的哈希算法
            algorithm=hashes.SHA256(),  # 使用 SHA256 作为哈希算法
            label=None  # 不使用标签
        )
    )
    return plaintext.decode()  # 将字节解码为字符串
def Encryption():# 加密
    text = input("请输入要加密的文本:")
    load_public_key()
    ciphertext=encrypt_with_public_key(load_public_key(),text)
    print(f'加密完成\n加密结果为:{ciphertext}')
    # 选择加密结果存放的文件
    while True:
        file = input("请输入要保存的加密文件名(若为空则保存在乱序文件名中):")
        if file=='':file=base64.b64encode(ciphertext).decode('utf-8')
        # 去除文件名从第一个非法字符后的内容
        
        if len(file)>20:
            file=file[:20]
        
        if not os.path.exists(file):break
        else:print(f"文件名为{file}的文件已存在于目录中，请重新输入文件名")
    with open(file, 'wb') as f:
        f.write(ciphertext)
    print(f"加密结果已保存到 {file}文件中")
    return ciphertext
def Decryption(TF=False):# 解密
    if TF==False:PrivateKey=load_private_key(input("请输入密码："))
    else:PrivateKey=load_private_key(input("请重新输入密码："))
    if PrivateKey==None:Decryption(True)
    while True:
        file = input("请输入要解密的文件名:")
        if os.path.exists(file):break
        else:print(f"文件名为{file}的文件不存在，请重新输入文件名")
    with open(file, 'rb') as f:
        ciphertext = f.read()
    original=decrypt_with_private_key(PrivateKey, ciphertext)
    print(f"解密完成\n解密结果为:{original}")
    return original

if __name__ == "__main__":
    # 判断是否需要生成密钥对
    if not os.path.exists("private.pem") or not os.path.exists("public.pem"):
        generate_rsa_keys(password=input("请输入密码："))
        print("密钥对已生成")
    else:print("密钥对已存在")
    while True:
        choice = input("请选择操作：\n1: 加密\n2: 解密\n其他按键: 退出\n")
        if choice == "1":Encryption()
        elif choice == "2":Decryption()
        else:break