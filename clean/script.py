"""
Comment数据清洗与分组脚本
功能:
1. 只保留指定字段: id, body, user, created_at, updated_at, html_url, issue_url
2. 按issue_url分组,将同一个问题的所有comments放在一起
3. 输出到新的目录结构
4. 增强的错误处理和JSON修复能力
"""
import os
import json
import re
from typing import List, Dict, Optional
from collections import defaultdict

# 配置
COMMENT_DIR = os.path.join("data", "comment")
OUTPUT_DIR = os.path.join("data", "comment_cleaned")
ERROR_DIR = os.path.join("data", "comment_errors")
BACKUP_SUFFIX = ".backup"

# 需要保留的字段（匹配实际JSON中的字段名）
KEEP_FIELDS = ["id", "body", "user", "created_at", "updated_at", "html_url", "issue_url"]

def clean_json_content(content: str) -> str:
    """
    清理JSON内容中的控制字符和格式问题
    
    Args:
        content: 原始JSON字符串
        
    Returns:
        清理后的JSON字符串
    """
    # 移除控制字符（保留换行、制表符等正常字符）
    content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', content)
    
    # 尝试修复常见的JSON格式问题
    # 移除可能的UTF-8 BOM
    if content.startswith('\ufeff'):
        content = content[1:]
     
    return content.strip()

def try_parse_json(content: str, filepath: str) -> Optional[List[Dict]]:
    """
    尝试多种方法解析JSON
    
    Args:   
        content: JSON字符串
        filepath: 文件路径（用于错误日志）
        
    Returns:
        解析后的数据列表，失败返回None
    """
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
                # 使用JSONDecoder逐个解析
                decoder = json.JSONDecoder()
                data, idx = decoder.raw_decode(content)
                if isinstance(data, list):
                    remaining = content[idx:].strip()
                    if remaining:
                        print(f"     警告: 文件末尾有 {len(remaining)} 字符被忽略")
                    return data
            except Exception as e2:
                print(f"     修复失败: {e2}")
        
        # 方法3: 尝试逐行解析（可能是JSONL格式）
        if "Extra data" in error_msg or "Expecting" in error_msg:
            print(f"  ⚠️  {filename}: 尝试作为多行JSON解析...")
            try:
                lines = content.strip().split('\n')
                all_data = []
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line and (line.startswith('[') or line.startswith('{')):
                        try:
                            item = json.loads(line)
                            if isinstance(item, list):
                                all_data.extend(item)
                            elif isinstance(item, dict):
                                all_data.append(item)
                        except:
                            pass
                if all_data:
                    print(f"     成功解析 {len(all_data)} 条数据")
                    return all_data
            except Exception as e3:
                print(f"     多行解析失败: {e3}")
        
        # 方法4: 尝试修复截断的JSON
        print(f"  ⚠️  {filename}: 尝试修复截断的JSON...")
        try:
            # 找到最后一个完整的对象
            last_complete = content.rfind('}')
            if last_complete > 0:
                # 确保以 ']' 结尾
                truncated = content[:last_complete+1]
                if not truncated.rstrip().endswith(']'):
                    truncated = truncated + ']'
                data = json.loads(truncated)
                if isinstance(data, list):
                    print(f"     修复成功，解析 {len(data)} 条数据")
                    return data
        except Exception as e4:
            print(f"     修复失败: {e4}")
        
        print(f"  ❌ {filename}: 所有解析方法都失败 - {error_msg}")
        return None

def clean_comment(comment: Dict) -> Dict:
    """
    清洗单条comment,只保留指定字段
    
    Args:
        comment: 原始comment数据
        
    Returns:
        清洗后的comment数据
    """
    cleaned = {}
    for field in KEEP_FIELDS:
        if field in comment:
            cleaned[field] = comment[field]
        else:
            # 如果字段不存在,设为None
            cleaned[field] = None
    
    return cleaned

def group_comments_by_issue(comments: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按issue_url分组comments
    
    Args:
        comments: comment列表
        
    Returns:
        以issue_url为key的字典,value为该issue的所有comments
    """
    grouped = defaultdict(list)
    no_issue_count = 0
    
    for comment in comments:
        issue_url = comment.get("issue_url")
        if issue_url:
            grouped[issue_url].append(comment)
        else:
            # 如果没有issue_url,归入"unknown"组
            grouped["unknown"].append(comment)
            no_issue_count += 1
    
    if no_issue_count > 0:
        print(f"  ⚠️  {no_issue_count} 条comments没有issue_url")
    
    return dict(grouped)

def extract_issue_number(issue_url: str) -> str:
    """
    从issue_url中提取issue编号
    例如: "https://api.github.com/repos/owner/repo/issues/123" -> "issue_123"
    
    Args:
        issue_url: issue的URL
        
    Returns:
        issue编号字符串
    """
    if not issue_url or issue_url == "unknown":
        return "unknown"
    
    try:
        # 提取URL最后的数字部分
        parts = issue_url.rstrip('/').split('/')
        issue_num = parts[-1]
        return f"issue_{issue_num}"
    except:
        return "unknown"

def process_json_file(filepath: str) -> tuple[List[Dict], bool]:
    """
    处理单个JSON文件,清洗并返回所有comments
    
    Args:
        filepath: JSON文件路径
        
    Returns:
        (清洗后的comments列表, 是否成功)
    """
    filename = os.path.basename(filepath)
    
    try:
        # 读取原始数据
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 清理内容
        content = clean_json_content(content)
        
        # 尝试解析JSON
        data = try_parse_json(content, filepath)
        
        if data is None:
            return [], False
        
        # 清洗每条comment
        cleaned_comments = [clean_comment(comment) for comment in data]
        
        print(f"  ✓ {filename}: 处理 {len(cleaned_comments)} 条comments")
        
        return cleaned_comments, True
        
    except Exception as e:
        print(f"  ❌ {filename}: 处理失败 - {e}")
        return [], False

def process_all_comments(directory: str) -> tuple[List[Dict], dict]:
    """
    处理目录中的所有JSON文件,合并所有comments
    
    Args:
        directory: 目录路径
        
    Returns:
        (所有清洗后的comments列表, 统计信息)
    """
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return [], {}
    
    all_comments = []
    stats = {
        "total_files": 0,
        "success_files": 0,
        "failed_files": 0,
        "failed_file_names": []
    }
    
    # 获取所有JSON文件
    json_files = [f for f in os.listdir(directory) 
                  if f.endswith('.json') and not f.endswith(BACKUP_SUFFIX)]
    
    print(f"\n📁 处理目录: {directory}")
    print(f"   找到 {len(json_files)} 个JSON文件\n")
    
    for filename in sorted(json_files):
        filepath = os.path.join(directory, filename)
        comments, success = process_json_file(filepath)
        
        stats["total_files"] += 1
        if success:
            stats["success_files"] += 1
            all_comments.extend(comments)
        else:
            stats["failed_files"] += 1
            stats["failed_file_names"].append(filename)
    
    return all_comments, stats

def save_grouped_comments(grouped_comments: Dict[str, List[Dict]], output_dir: str):
    """
    保存分组后的comments到文件
    
    Args:
        grouped_comments: 按issue_url分组的comments
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n💾 保存分组数据到: {output_dir}\n")
    
    # 保存每个issue的comments
    saved_count = 0
    for issue_url, comments in sorted(grouped_comments.items()):
        # 生成文件名
        issue_id = extract_issue_number(issue_url)
        filename = f"{issue_id}.json"
        filepath = os.path.join(output_dir, filename)
        
        # 按created_at排序comments
        sorted_comments = sorted(
            comments, 
            key=lambda x: x.get("created_at") or ""
        )
        
        # 构建输出数据
        output_data = {
            "issue_url": issue_url,
            "comment_count": len(sorted_comments),
            "comments": sorted_comments
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        saved_count += 1
        if saved_count <= 10 or len(sorted_comments) > 100:
            print(f"  ✓ {filename}: {len(sorted_comments)} 条comments")
    
    if saved_count > 10:
        print(f"  ... (省略 {saved_count - 10} 个文件)")

def main():
    """主函数"""
    print("=" * 60)
    print("🧹 Comment数据清洗与分组工具")
    print("=" * 60)
    print(f"\n功能说明:")
    print(f"  1. 只保留字段: {', '.join(KEEP_FIELDS)}")
    print(f"  2. 按issue_url分组comments")
    print(f"  3. 输出到: {OUTPUT_DIR}")
    print(f"  4. 增强的JSON解析和错误修复")
    
    # 确认执行
    confirm = input("\n确认开始处理? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    print("\n" + "=" * 60)
    
    # 步骤1: 读取并清洗所有comments
    print("\n📖 步骤1: 读取并清洗comments")
    all_comments, stats = process_all_comments(COMMENT_DIR)
    
    print(f"\n文件处理统计:")
    print(f"  - 总文件数: {stats['total_files']}")
    print(f"  - 成功: {stats['success_files']}")
    print(f"  - 失败: {stats['failed_files']}")
    
    if stats['failed_files'] > 0:
        print(f"\n失败的文件:")
        for name in stats['failed_file_names']:
            print(f"  - {name}")
    
    if not all_comments:
        print("\n❌ 未找到任何有效的comments数据")
        return
    
    print(f"\n✓ 共读取 {len(all_comments):,} 条comments")
    
    # 步骤2: 按issue_url分组
    print("\n📊 步骤2: 按issue_url分组")
    grouped_comments = group_comments_by_issue(all_comments)
    
    print(f"✓ 分组完成: {len(grouped_comments)} 个不同的issues")
    
    # 显示分组统计
    issue_comment_counts = [(url, len(comments)) for url, comments in grouped_comments.items()]
    issue_comment_counts.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n前10个最多comments的issues:")
    for i, (url, count) in enumerate(issue_comment_counts[:10], 1):
        issue_id = extract_issue_number(url)
        print(f"  {i}. {issue_id}: {count} 条comments")
    
    # 步骤3: 保存分组后的数据
    print(f"\n💾 步骤3: 保存分组数据")
    save_grouped_comments(grouped_comments, OUTPUT_DIR)
    
    # 最终统计
    print("\n" + "=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    print(f"\n总计:")
    print(f"  - 处理文件: {stats['success_files']}/{stats['total_files']}")
    print(f"  - 处理comments: {len(all_comments):,} 条")
    print(f"  - 分组issues: {len(grouped_comments)} 个")
    print(f"  - 输出目录: {OUTPUT_DIR}")
    print(f"  - 平均每个issue: {len(all_comments)/len(grouped_comments):.1f} 条comments")
    
    print("\n" + "=" * 60)
    print("✅ 处理完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()