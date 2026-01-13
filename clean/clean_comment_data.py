"""
Comment数据清洗脚本
功能:
1. 顺序处理每个JSON文件
2. 按issue_url分组,将同一个问题的所有comments放在一起
3. 只保留指定字段: id, body, user, created_at, updated_at, html_url, issue_url
4. 输出结构: 每个原始文件对应一个输出文件

用法:
    python clean_comment_data.py          # 交互式，需要确认
    python clean_comment_data.py --yes    # 跳过确认直接执行
"""
import os
import sys
import json
import re
from typing import List, Dict, Optional
from collections import defaultdict

# 配置
COMMENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "comment")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "comment_cleaned")

# 需要保留的字段
KEEP_FIELDS = ["id", "body", "user", "created_at", "updated_at", "html_url", "issue_url"]


def clean_json_content(content: str) -> str:
    """清理JSON内容中的控制字符和格式问题"""
    # 移除可能的UTF-8 BOM
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # 移除所有控制字符（\x00-\x1f），但保留换行符(\n=\x0a)和回车符(\r=\x0d)
    # 这些控制字符在JSON字符串中是非法的
    content = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]', '', content)
     
    return content.strip()


def deep_clean_json_string(content: str) -> str:
    """
    深度清理JSON字符串中的控制字符
    处理字符串值内部的控制字符（在引号内的内容）
    使用更激进的清理策略
    """
    # 策略1: 使用正则表达式替换字符串内的控制字符
    # 匹配JSON字符串并清理其中的控制字符
    def clean_string_value(match):
        s = match.group(0)
        # 移除字符串内的控制字符（除了已转义的）
        # 保留 \n \r \t 的转义形式，但移除裸露的控制字符
        cleaned = []
        i = 0
        while i < len(s):
            char = s[i]
            if char == '\\' and i + 1 < len(s):
                # 保留转义序列
                cleaned.append(char)
                cleaned.append(s[i + 1])
                i += 2
                continue
            # 移除控制字符 (0x00-0x1F, 0x7F)
            if ord(char) < 32 or ord(char) == 127:
                # 换行和制表符转换为空格
                if char in '\n\r\t':
                    cleaned.append(' ')
                # 其他控制字符直接移除
                i += 1
                continue
            cleaned.append(char)
            i += 1
        return ''.join(cleaned)
    
    # 匹配JSON字符串 (包括转义的引号)
    # 这个正则表达式匹配: "..." 包括转义的引号 \"
    try:
        result = re.sub(r'"(?:[^"\\]|\\.)*"', clean_string_value, content)
        return result
    except Exception:
        # 如果正则失败，使用逐字符方法
        pass
    
    # 备用策略: 逐字符处理
    result = []
    in_string = False
    escape_next = False
    
    for char in content:
        if escape_next:
            result.append(char)
            escape_next = False
            continue
            
        if char == '\\' and in_string:
            result.append(char)
            escape_next = True
            continue
            
        if char == '"' and not escape_next:
            in_string = not in_string
            result.append(char)
            continue
        
        # 如果在字符串内部，处理控制字符
        if in_string:
            if ord(char) < 32 or ord(char) == 127:
                # 换行/回车/制表符转换为空格
                if char in '\n\r\t':
                    result.append(' ')
                # 其他控制字符直接跳过
                continue
            else:
                result.append(char)
        else:
            # 不在字符串内，保留正常的换行等
            if ord(char) < 32 and char not in '\n\r\t':
                continue
            result.append(char)
    
    return ''.join(result)


def try_parse_json(content: str, filepath: str) -> Optional[List[Dict]]:
    """尝试多种方法解析JSON"""
    filename = os.path.basename(filepath)
    
    # 方法1: 直接解析
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        else:
            print(f"  ⚠️  {filename}: 数据不是数组格式")
            return None
    except json.JSONDecodeError as e:
        error_msg = str(e)
        
        # 方法2: 如果是"Extra data"错误，尝试只读取第一个完整的JSON数组
        if "Extra data" in error_msg:
            print(f"  ⚠️  {filename}: 检测到Extra data错误，尝试修复...")
            try:
                decoder = json.JSONDecoder()
                data, idx = decoder.raw_decode(content)
                if isinstance(data, list):
                    remaining = content[idx:].strip()
                    if remaining:
                        print(f"     警告: 文件末尾有 {len(remaining)} 字符被忽略")
                    return data
            except Exception as e2:
                print(f"     修复失败: {e2}")
        
        # 方法3: 如果是控制字符错误，尝试深度清理
        if "control character" in error_msg.lower():
            print(f"  ⚠️  {filename}: 检测到控制字符错误，尝试深度清理...")
            try:
                cleaned = deep_clean_json_string(content)
                data = json.loads(cleaned)
                if isinstance(data, list):
                    print(f"     深度清理成功，解析 {len(data)} 条数据")
                    return data
            except json.JSONDecodeError as e3:
                # 如果还是失败，尝试更激进的清理：移除所有控制字符
                print(f"     深度清理仍有问题: {e3}")
                print(f"     尝试激进清理...")
                try:
                    # 移除所有控制字符（包括字符串内的换行）
                    aggressive_cleaned = re.sub(r'[\x00-\x1f\x7f]', ' ', content)
                    data = json.loads(aggressive_cleaned)
                    if isinstance(data, list):
                        print(f"     激进清理成功，解析 {len(data)} 条数据")
                        return data
                except Exception as e4:
                    print(f"     激进清理失败: {e4}")
        
        # 方法4: 尝试修复截断的JSON
        try:
            last_complete = content.rfind('}')
            if last_complete > 0:
                truncated = content[:last_complete+1]
                if not truncated.rstrip().endswith(']'):
                    truncated = truncated + ']'
                data = json.loads(truncated)
                if isinstance(data, list):
                    print(f"  ⚠️  {filename}: 修复截断JSON成功，解析 {len(data)} 条数据")
                    return data
        except Exception:
            pass
        
        print(f"  ❌ {filename}: JSON解析失败 - {error_msg}")
        return None


def clean_comment(comment: Dict) -> Dict:
    """清洗单条comment,只保留指定字段"""
    cleaned = {}
    for field in KEEP_FIELDS:
        if field in comment:
            cleaned[field] = comment[field]
        else:
            cleaned[field] = None
    return cleaned


def group_comments_by_issue(comments: List[Dict]) -> Dict[str, List[Dict]]:
    """按issue_url分组comments"""
    grouped = defaultdict(list)
    
    for comment in comments:
        issue_url = comment.get("issue_url")
        if issue_url:
            grouped[issue_url].append(comment)
        else:
            grouped["unknown"].append(comment)
    
    # 对每个分组内的comments按created_at排序
    result = {}
    for issue_url, issue_comments in grouped.items():
        sorted_comments = sorted(
            issue_comments,
            key=lambda x: x.get("created_at") or ""
        )
        result[issue_url] = sorted_comments
    
    return result


def process_single_file(input_filepath: str, output_filepath: str) -> tuple[bool, dict]:
    """
    处理单个JSON文件
    
    Returns:
        (是否成功, 统计信息)
    """
    filename = os.path.basename(input_filepath)
    stats = {
        "total_comments": 0,
        "issue_count": 0
    }
    
    try:
        # 读取原始数据
        with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 清理内容
        content = clean_json_content(content)
        
        # 解析JSON
        data = try_parse_json(content, input_filepath)
        
        if data is None:
            return False, stats
        
        # 清洗每条comment
        cleaned_comments = [clean_comment(comment) for comment in data]
        stats["total_comments"] = len(cleaned_comments)
        
        # 按issue_url分组
        grouped = group_comments_by_issue(cleaned_comments)
        stats["issue_count"] = len(grouped)
        
        # 构建输出数据结构
        output_data = {
            "source_file": filename,
            "total_comments": len(cleaned_comments),
            "issue_count": len(grouped),
            "issues": []
        }
        
        # 按issue_url排序输出
        for issue_url in sorted(grouped.keys()):
            issue_comments = grouped[issue_url]
            output_data["issues"].append({
                "issue_url": issue_url,
                "comment_count": len(issue_comments),
                "comments": issue_comments
            })
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        
        # 保存到文件
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        return True, stats
        
    except Exception as e:
        print(f"  ❌ {filename}: 处理失败 - {e}")
        return False, stats


def main():
    """主函数"""
    print("=" * 60)
    print("🧹 Comment数据清洗工具")
    print("=" * 60)
    print(f"\n功能说明:")
    print(f"  1. 只保留字段: {', '.join(KEEP_FIELDS)}")
    print(f"  2. 按issue_url分组comments")
    print(f"  3. 每个文件独立处理")
    print(f"\n输入目录: {COMMENT_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 检查输入目录
    if not os.path.exists(COMMENT_DIR):
        print(f"\n❌ 输入目录不存在: {COMMENT_DIR}")
        return
    
    # 获取所有JSON文件
    json_files = [f for f in os.listdir(COMMENT_DIR) if f.endswith('.json')]
    json_files.sort()
    
    print(f"\n找到 {len(json_files)} 个JSON文件")
    
    # 检查是否有 --yes 参数跳过确认
    if "--yes" not in sys.argv and "-y" not in sys.argv:
        confirm = input("\n确认开始处理? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "-" * 60)
    print("开始处理...")
    print("-" * 60 + "\n")
    
    # 统计信息
    total_stats = {
        "success": 0,
        "failed": 0,
        "total_comments": 0,
        "total_issues": 0,
        "failed_files": []
    }
    
    # 顺序处理每个文件
    for i, filename in enumerate(json_files, 1):
        input_path = os.path.join(COMMENT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"[{i}/{len(json_files)}] 处理: {filename}")
        
        success, stats = process_single_file(input_path, output_path)
        
        if success:
            total_stats["success"] += 1
            total_stats["total_comments"] += stats["total_comments"]
            total_stats["total_issues"] += stats["issue_count"]
            print(f"  ✓ 完成: {stats['total_comments']:,} comments, {stats['issue_count']} issues")
        else:
            total_stats["failed"] += 1
            total_stats["failed_files"].append(filename)
    
    # 打印最终统计
    print("\n" + "=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    print(f"\n文件处理:")
    print(f"  - 成功: {total_stats['success']}/{len(json_files)}")
    print(f"  - 失败: {total_stats['failed']}")
    
    if total_stats["failed_files"]:
        print(f"\n失败的文件:")
        for f in total_stats["failed_files"]:
            print(f"  - {f}")
    
    print(f"\n数据统计:")
    print(f"  - 总comments: {total_stats['total_comments']:,}")
    print(f"  - 总issues: {total_stats['total_issues']:,}")
    
    print(f"\n输出目录: {OUTPUT_DIR}")
    print("\n" + "=" * 60)
    print("✅ 处理完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
