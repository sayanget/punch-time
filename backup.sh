#!/bin/bash

# 数据备份脚本
# 使用方法: bash backup.sh

set -e

# 配置
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$DATE.tar.gz"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "开始备份数据..."

# 备份数据文件
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    users.json \
    punches.json \
    2>/dev/null || echo "警告: 某些文件可能不存在"

if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo "✓ 备份成功: $BACKUP_DIR/$BACKUP_FILE"
    
    # 显示备份文件大小
    SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo "  文件大小: $SIZE"
    
    # 保留最近10个备份
    cd "$BACKUP_DIR"
    ls -t backup_*.tar.gz | tail -n +11 | xargs -r rm
    echo "  已清理旧备份，保留最近10个"
else
    echo "✗ 备份失败"
    exit 1
fi

# 可选: 上传到云存储
# 取消注释以下行并配置你的云存储
# aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" s3://your-bucket/backups/
# aliyun oss cp "$BACKUP_DIR/$BACKUP_FILE" oss://your-bucket/backups/

echo "备份完成!"
