#!/usr/bin/env python3
"""
生成自签名SSL证书用于本地HTTPS开发
"""
import os
from pathlib import Path

def generate_self_signed_cert():
    """生成自签名SSL证书"""
    # 创建ssl目录
    ssl_dir = Path('ssl')
    ssl_dir.mkdir(exist_ok=True)
    
    cert_path = ssl_dir / 'cert.pem'
    key_path = ssl_dir / 'key.pem'
    
    # 检查证书是否已存在
    if cert_path.exists() and key_path.exists():
        print(f"✓ SSL证书已存在:")
        print(f"  证书: {cert_path}")
        print(f"  私钥: {key_path}")
        return
    
    try:
        # 使用OpenSSL生成自签名证书
        import subprocess
        
        print("正在生成自签名SSL证书...")
        
        # 生成私钥和证书
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', str(key_path),
            '-out', str(cert_path),
            '-days', '365',
            '-nodes',
            '-subj', '/CN=localhost'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✓ SSL证书生成成功!")
            print(f"  证书: {cert_path}")
            print(f"  私钥: {key_path}")
            print(f"\n注意: 这是自签名证书,浏览器会显示安全警告")
            print(f"      点击\"高级\"然后\"继续访问\"即可")
        else:
            print(f"\n✗ 证书生成失败!")
            print(f"错误: {result.stderr}")
            raise Exception("OpenSSL命令执行失败")
            
    except FileNotFoundError:
        print("\n✗ 未找到OpenSSL命令!")
        print("\n请安装OpenSSL:")
        print("  Windows: 下载并安装 https://slproweb.com/products/Win32OpenSSL.html")
        print("  或使用: winget install OpenSSL.Light")
        print("\n或者使用Python的cryptography库生成证书...")
        
        # 尝试使用cryptography库
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            print("\n使用cryptography库生成证书...")
            
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # 生成证书
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Punch Timer"),
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(u"localhost"),
                    x509.DNSName(u"127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # 保存私钥
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # 保存证书
            with open(cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            print(f"\n✓ SSL证书生成成功!")
            print(f"  证书: {cert_path}")
            print(f"  私钥: {key_path}")
            print(f"\n注意: 这是自签名证书,浏览器会显示安全警告")
            print(f"      点击\"高级\"然后\"继续访问\"即可")
            
        except ImportError:
            print("\n✗ cryptography库未安装!")
            print("\n请安装: pip install cryptography")
            raise Exception("无法生成SSL证书")

if __name__ == '__main__':
    generate_self_signed_cert()
