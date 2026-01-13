"""
过滤 top300_20_23.csv 文件，只保留2022年到2023年之间的数据
"""

import pandas as pd
import time
import os

# 输入和输出文件路径
input_file = 'top300_20_23/top300_20_23.csv'
output_file = 'top300_20_23/top300_2022_2023.csv'

# 定义日期范围
start_date = '2022-03-01'
end_date = '2023-03-31 23:59:59'

print(f"开始处理文件: {input_file}")
print(f"日期范围: {start_date} 到 {end_date}")

# 获取文件大小（用于估算进度）
file_size = os.path.getsize(input_file)
print(f"文件大小: {file_size / (1024**3):.2f} GB")

# 先快速统计总行数
print("\n正在统计文件总行数...")
count_start = time.time()
total_lines = sum(1 for _ in open(input_file, 'r', encoding='utf-8')) - 1  # 减去表头
count_time = time.time() - count_start
print(f"文件共有 {total_lines:,} 行数据（统计耗时: {count_time:.1f}秒）")

# 由于文件很大，使用分块读取
chunk_size = 100000  # 每次读取10万行
processed_rows = 0
filtered_rows = 0
first_chunk = True
chunk_count = 0

print("\n开始过滤数据...")
start_time = time.time()

# 分块读取和处理
for chunk in pd.read_csv(input_file, chunksize=chunk_size, low_memory=False):
    chunk_count += 1
    processed_rows += len(chunk)
    
    # 将 created_at 列转换为日期时间格式
    chunk['created_at'] = pd.to_datetime(chunk['created_at'], errors='coerce')
    
    # 过滤2022年到2023年的数据
    mask = (chunk['created_at'] >= start_date) & (chunk['created_at'] <= end_date)
    filtered_chunk = chunk[mask]
    
    filtered_rows += len(filtered_chunk)
    
    # 写入文件（第一块包含表头，后续不包含）
    if first_chunk:
        filtered_chunk.to_csv(output_file, index=False, mode='w')
        first_chunk = False
    else:
        filtered_chunk.to_csv(output_file, index=False, mode='a', header=False)
    
    # 计算进度和剩余时间
    progress = (processed_rows / total_lines) * 100
    elapsed_time = time.time() - start_time
    
    if progress > 0:
        estimated_total_time = elapsed_time / (progress / 100)
        remaining_time = estimated_total_time - elapsed_time
        
        # 格式化剩余时间
        if remaining_time >= 60:
            remaining_str = f"{remaining_time / 60:.1f} 分钟"
        else:
            remaining_str = f"{remaining_time:.0f} 秒"
        
        # 计算处理速度
        speed = processed_rows / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\r进度: {progress:.1f}% | 已处理: {processed_rows:,}/{total_lines:,} 行 | "
              f"筛选出: {filtered_rows:,} 行 | 速度: {speed:,.0f} 行/秒 | "
              f"预计剩余: {remaining_str}", end='', flush=True)

# 最终统计
total_time = time.time() - start_time
print(f"\n\n{'='*60}")
print(f"处理完成!")
print(f"{'='*60}")
print(f"总共处理: {processed_rows:,} 行")
print(f"筛选出: {filtered_rows:,} 行 (符合日期范围的数据)")
print(f"筛选比例: {(filtered_rows/processed_rows)*100:.1f}%")
print(f"总耗时: {total_time:.1f} 秒 ({total_time/60:.1f} 分钟)")
print(f"平均速度: {processed_rows/total_time:,.0f} 行/秒")
print(f"输出文件: {output_file}")
