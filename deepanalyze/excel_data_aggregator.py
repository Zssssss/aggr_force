#!/usr/bin/env python3
"""
Excel数据聚合器 - 将多个Excel文件内容合并为字符串
用于大模型处理和分析
"""

import pandas as pd
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from datetime import datetime


class ExcelDataAggregator:
    """Excel数据聚合器类"""
    
    def __init__(self, workspace_dir: str = "workspace"):
        """
        初始化聚合器
        
        Args:
            workspace_dir: Excel文件所在目录
        """
        self.workspace_dir = Path(workspace_dir)
        self.supported_extensions = {'.xlsx', '.xls'}
        
    def scan_excel_files(self) -> List[Path]:
        """
        扫描目录下的所有Excel文件
        
        Returns:
            Excel文件路径列表
        """
        excel_files = []
        for file_path in self.workspace_dir.glob("*"):
            if file_path.suffix.lower() in self.supported_extensions:
                excel_files.append(file_path)
        
        # 按文件名排序
        excel_files.sort(key=lambda x: x.name)
        return excel_files
    
    def read_excel_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        读取Excel文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            DataFrame或None（如果读取失败）
        """
        try:
            # 尝试读取"数据"sheet，如果不存在则读取第一个sheet
            try:
                df = pd.read_excel(file_path, sheet_name="数据")
            except:
                # 获取第一个sheet
                xl_file = pd.ExcelFile(file_path)
                first_sheet = xl_file.sheet_names[0]
                df = pd.read_excel(file_path, sheet_name=first_sheet)
            
            return df
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return None
    
    def extract_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        提取文件元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            元数据字典
        """
        stat = file_path.stat()
        
        # 解析文件名
        file_name = file_path.stem  # 不含扩展名
        parts = file_name.split("_")
        
        metadata = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "name_parts": parts,
            "category": parts[0] if parts else "未知",
            "sub_category": parts[1] if len(parts) > 1 else "未知",
            "date_str": parts[2] if len(parts) > 2 else "未知",
            "time_str": parts[3] if len(parts) > 3 else "未知"
        }
        
        return metadata
    
    def dataframe_to_string(self, df: pd.DataFrame, max_rows: int = 10000) -> str:
        """
        将DataFrame转换为字符串格式
        
        Args:
            df: DataFrame对象
            max_rows: 最大行数限制
            
        Returns:
            字符串表示
        """
        if df is None or df.empty:
            return "数据为空"
        
        # 限制行数
        if len(df) > max_rows:
            df_display = df.head(max_rows).copy()
            truncated_info = f"\n... (显示前{max_rows}行，共{len(df)}行)"
        else:
            df_display = df
            truncated_info = ""
        
        # 转换为字符串
        df_str = df_display.to_string(index=False)
        
        # 添加列信息
        col_info = f"列名: {', '.join(df.columns.tolist())}"
        shape_info = f"形状: {df.shape[0]}行 x {df.shape[1]}列"
        
        result = f"{col_info}\n{shape_info}\n\n{df_str}{truncated_info}"
        return result
    
    def process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        处理单个Excel文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含元数据和内容的字典
        """
        print(f"处理文件: {file_path.name}")
        
        # 提取元数据
        metadata = self.extract_file_metadata(file_path)
        
        # 读取数据
        df = self.read_excel_file(file_path)
        
        # 转换为字符串
        content_str = self.dataframe_to_string(df) if df is not None else "读取失败"
        
        return {
            "metadata": metadata,
            "content": content_str,
            "success": df is not None
        }
    
    def aggregate_all_data(self, output_file: Optional[str] = None) -> str:
        """
        聚合所有Excel文件数据
        
        Args:
            output_file: 输出文件路径（可选）
            
        Returns:
            聚合后的字符串
        """
        # 扫描文件
        excel_files = self.scan_excel_files()
        print(f"发现 {len(excel_files)} 个Excel文件")
        
        if not excel_files:
            return "未找到Excel文件"
        
        # 处理所有文件
        results = []
        for file_path in excel_files:
            result = self.process_single_file(file_path)
            results.append(result)
        
        # 构建聚合字符串
        aggregated_str = self._build_aggregated_string(results)
        
        # 保存到文件（如果指定）
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(aggregated_str)
            print(f"结果已保存到: {output_file}")
        
        return aggregated_str
    
    def _build_aggregated_string(self, results: List[Dict[str, Any]]) -> str:
        """
        构建聚合字符串
        
        Args:
            results: 处理结果列表
            
        Returns:
            聚合字符串
        """
        lines = []
        
        # # 添加标题
        # lines.append("=" * 80)
        # lines.append("Excel数据聚合报告")
        # lines.append(f"生成时间: {datetime.now().isoformat()}")
        # lines.append(f"文件总数: {len(results)}")
        # lines.append("=" * 80)
        # lines.append("")
        
        # 按类别分组
        category_groups = {}
        for result in results:
            category = result['metadata']['category']
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(result)
        
        # 输出每个类别
        for category, group_results in sorted(category_groups.items()):
            lines.append("-" * 80)
            lines.append(f"类别: {category} (共{len(group_results)}个文件)")
            lines.append("-" * 80)
            lines.append("")
            
            # 输出该类别下的每个文件
            for result in group_results:
                metadata = result['metadata']
                
                # 文件头信息
                lines.append(f"文件名: {metadata['file_name']}")
                lines.append(f"子类别: {metadata['sub_category']}")
                lines.append(f"日期: {metadata['date_str']}")
                lines.append(f"处理状态: {'成功' if result['success'] else '失败'}")
                lines.append("")
                
                # 数据内容
                if result['success']:
                    lines.append("数据内容:")
                    lines.append(result['content'])
                else:
                    lines.append("数据内容: 读取失败")
                
                lines.append("")
                lines.append("-" * 40)
                lines.append("")
        
        # # 添加摘要信息
        # lines.append("=" * 80)
        # lines.append("摘要统计")
        # lines.append("=" * 80)
        # lines.append("")
        
        # success_count = sum(1 for r in results if r['success'])
        # lines.append(f"成功读取: {success_count}/{len(results)} 个文件")
        # lines.append(f"失败读取: {len(results) - success_count}/{len(results)} 个文件")
        # lines.append("")
        
        # # 类别统计
        # lines.append("按类别统计:")
        # for category, group_results in sorted(category_groups.items()):
        #     success_in_group = sum(1 for r in group_results if r['success'])
        #     lines.append(f"  {category}: {success_in_group}/{len(group_results)} 成功")
        
        return "\n".join(lines)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Excel数据聚合器')
    parser.add_argument('--workspace', default='workspace', 
                       help='Excel文件所在目录 (默认: workspace)')
    parser.add_argument('--output', default='aggregated_data.txt',
                       help='输出文件路径 (默认: aggregated_data.txt)')
    parser.add_argument('--no-output', action='store_true',
                       help='不保存到文件，只打印到控制台')
    
    args = parser.parse_args()
    
    # 创建聚合器
    aggregator = ExcelDataAggregator(args.workspace)
    
    # 执行聚合
    output_file = None if args.no_output else args.output
    result = aggregator.aggregate_all_data(output_file)
    
    # 如果没有保存到文件，则打印结果
    if args.no_output:
        print(result)


if __name__ == "__main__":
    main()