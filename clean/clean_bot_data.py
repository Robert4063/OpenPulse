"""
数据清洗脚本 - 清除Comments和Issues中的Bot数据
检查user字段，删除包含"bot"关键词的条目
"""
import os
import json
import re
from typing import List, Dict, Tuple

# 配置
COMMENT_DIR = os.path.join("data", "comment")
ISSUE_DIR = os.path.join("data", "issue")
BACKUP_SUFFIX = ".backup"

def is_bot_user(username) -> bool:
    """
    判断用户是否为bot
    检查username中是否包含'bot'关键词（不区分大小写）
    """
    if not username:
        return False
    # 处理username可能是dict的情况
    if isinstance(username, dict):
        username = username.get("login", "")
    if not isinstance(username, str):
        return False
    return "adguard-bot" in username.lower()

def clean_data(data: List[Dict]) -> Tuple[List[Dict], int]:
    """
    清洗数据，移除bot用户的条目
    
    Args:
        data: 原始数据列表
        
    Returns:
        (cleaned_data, removed_count): 清洗后的数据和移除的条目数量
    """
    original_count = len(data)
    cleaned_data = [item for item in data if not is_bot_user(item.get("user"))]
    removed_count = original_count - len(cleaned_data)
    
    return cleaned_data, removed_count

def process_json_file(filepath: str, backup: bool = True) -> Tuple[int, int]:
    """
    处理单个JSON文件
    
    Args:
        filepath: JSON文件路径
        backup: 是否备份原文件
        
    Returns:
        (original_count, removed_count): 原始条目数和移除的条目数
    """
    try:
        # 读取原始数据，忽略控制字符
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # 移除控制字符（除了换行、制表符等正常字符）
            import re
            content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', content)
            data = json.loads(content)
        
        if not isinstance(data, list):
            print(f"  ⚠️  {os.path.basename(filepath)}: 数据格式不是数组，跳过")
            return 0, 0
        
        original_count = len(data)
        
        # 清洗数据
        cleaned_data, removed_count = clean_data(data)
        
        # 如果有数据被移除，则更新文件
        if removed_count > 0:
            # 备份原文件
            if backup:
                backup_path = filepath + BACKUP_SUFFIX
                if not os.path.exists(backup_path):
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 写入清洗后的数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ {os.path.basename(filepath)}: 移除 {removed_count}/{original_count} 条bot数据")
        else:
            print(f"  - {os.path.basename(filepath)}: 无bot数据")
        
        return original_count, removed_count
        
    except json.JSONDecodeError as e:
        print(f"  ❌ {os.path.basename(filepath)}: JSON解析错误 - {e}")
        return 0, 0
    except Exception as e:
        print(f"  ❌ {os.path.basename(filepath)}: 处理失败 - {e}")
        return 0, 0

def process_directory(directory: str, backup: bool = True) -> Dict[str, int]:
    """
    处理目录中的所有JSON文件
    
    Args:
        directory: 目录路径
        backup: 是否备份原文件
        
    Returns:
        统计信息字典
    """
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return {"files": 0, "total_items": 0, "removed_items": 0}
    
    stats = {
        "files": 0,
        "total_items": 0,
        "removed_items": 0
    }
    
    # 获取所有JSON文件
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    
    print(f"\n📁 处理目录: {directory}")
    print(f"   找到 {len(json_files)} 个JSON文件\n")
    
    for filename in sorted(json_files):
        filepath = os.path.join(directory, filename)
        original_count, removed_count = process_json_file(filepath, backup)
        
        stats["files"] += 1
        stats["total_items"] += original_count
        stats["removed_items"] += removed_count
    
    return stats

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 Bot数据清洗工具")
    print("=" * 60)
    print(f"\n清洗策略: 移除user字段中包含'bot'关键词的条目\n")
    
    # 询问是否备份
    backup_choice = input("是否备份原始文件? (y/n, 默认y): ").strip().lower()
    backup = backup_choice != 'n'
    
    if backup:
        print("✓ 将创建 .backup 备份文件")
    else:
        print("⚠️  不创建备份文件")
    
    # 确认执行
    confirm = input("\n确认开始清洗? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    print("\n" + "=" * 60)
    
    # 处理comments目录
    comment_stats = process_directory(COMMENT_DIR, backup)
    
    # 处理issues目录
    issue_stats = process_directory(ISSUE_DIR, backup)
    
    # 汇总统计
    total_files = comment_stats["files"] + issue_stats["files"]
    total_items = comment_stats["total_items"] + issue_stats["total_items"]
    total_removed = comment_stats["removed_items"] + issue_stats["removed_items"]
    
    print("\n" + "=" * 60)
    print("📊 清洗统计")
    print("=" * 60)
    print(f"\nComments:")
    print(f"  - 处理文件: {comment_stats['files']} 个")
    print(f"  - 原始条目: {comment_stats['total_items']:,} 条")
    print(f"  - 移除条目: {comment_stats['removed_items']:,} 条 ({comment_stats['removed_items']/comment_stats['total_items']*100 if comment_stats['total_items'] > 0 else 0:.2f}%)")
    
    print(f"\nIssues:")
    print(f"  - 处理文件: {issue_stats['files']} 个")
    print(f"  - 原始条目: {issue_stats['total_items']:,} 条")
    print(f"  - 移除条目: {issue_stats['removed_items']:,} 条 ({issue_stats['removed_items']/issue_stats['total_items']*100 if issue_stats['total_items'] > 0 else 0:.2f}%)")
    
    print(f"\n总计:")
    print(f"  - 处理文件: {total_files} 个")
    print(f"  - 原始条目: {total_items:,} 条")
    print(f"  - 移除条目: {total_removed:,} 条 ({total_removed/total_items*100 if total_items > 0 else 0:.2f}%)")
    print(f"  - 保留条目: {total_items - total_removed:,} 条")
    
    print("\n" + "=" * 60)
    print("✅ 清洗完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
