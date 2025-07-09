import datetime
import os
import json
from record import Record
import shutil
import time
import functools

def profile(func):
    """性能分析装饰器"""
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        start_time:float = time.perf_counter()
        result = func(*args,**kwargs)
        end_time:float = time.perf_counter()
        print(f"{func.__name__}执行时间：{end_time - start_time:.4f}秒")
        return result
    return wrapper

class Account:
    @profile
    def __init__(self, data_file="code/data/records.json"):
        """
        初始化账户对象
        :param data_file: 存储收支记录的文件路径
        """
        self.data_file = data_file
        self.records = self.load_records()#加载已有记录
        self._build_indexes()#建立索引（首次加载时预处理）
    
    def _build_indexes(self):
        """建立日期和类别索引，加速查询"""
        #日期索引：按年-月分组
        self.date_index = {}
        #类别索引
        self.category_index = {"收入":[],"支出":[]}

        for record in self.records:
            #构建日期索引：格式为YYYY-MM
            year_mouth = record.date.strftime("%Y-%m")
            if year_mouth not in self.date_index:
                self.date_index[year_mouth] = []
            self.date_index[year_mouth].append(record)
        
        # 构建类别索引
            if record.category in self.category_index:
                self.category_index[record.category].append(record)

    @profile
    def load_records(self):
        """
        从文件中加载收支记录
        :return: 收支记录列表
        """
        if not os.path.exists(self.data_file):
            print(f"数据文件不存在，将创建新文件: {self.data_file}")
            return []
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                records_data = json.load(file)

            records = []
            for record_data in records_data:
                # 检查date字段是否存在
                if 'date' in record_data:
                    try:
                        # 转换日期格式
                        record_date = datetime.datetime.strptime(record_data['date'], "%Y-%m-%d").date()
                        record_data['date'] = record_date
                        # 添加到记录列表
                        records.append(Record(**record_data))
                    except ValueError:
                        print(f"警告: 日期格式错误，跳过记录: {record_data}")
                else:
                    # 处理缺少date字段的记录
                    print(f"警告: 记录缺少日期字段，跳过记录: {record_data}")
            print(f"成功从文件加载 {len(records)} 条记录")
            return records  # 确保在所有成功解析的情况下返回records
    
        except (json.JSONDecodeError, FileNotFoundError):
            print("警告：数据文件格式错误或不存在，创建新文件")
            return []  # 确保在异常情况下也返回空列表
        except Exception as e:
            print(f"加载数据时发生未知错误: {e}")
            return []

    @profile
    def save_records(self):
        """
        将收支记录保存到文件
        """
        
        try:
            records_data = [
                {
                    "date": record.date.strftime("%Y-%m-%d"),
                    "category": record.category, 
                    "amount": record.amount, 
                    "description": record.description
                } 
                for record in self.records
            ]
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(records_data, file, ensure_ascii=False, indent=4)

            print(f"成功保存 {len(self.records)} 条记录到文件")
            # 备份原文件
            if os.path.exists(self.data_file):
                backup_file = f"{self.data_file}.bak"
                shutil.copy2(self.data_file, backup_file)

        except Exception as e:
            print(f"保存数据失败：{e}")
       

    @profile
    def add_record(self, date, category, amount, description):
        """
        添加一条收支记录
        :param date: 记录日期
        :param category: 收支类别
        :param amount: 金额
        :param description: 描述
        """
        if category not in ["收入", "支出"]:
            raise ValueError("类别必须是'收入'或'支出'")
        if amount <= 0:
            raise ValueError("金额必须为正数")
        
        # 创建新记录并添加到列表
        new_record = Record(date, category, amount, description)
        self.records.append(new_record)  # 追加到列表，而非替换
        
        # 更新日期索引
        year_mouth = date.strftime("%Y-%m")
        if year_mouth not in self.date_index:
            self.date_index[year_mouth] = []
        self.date_index[year_mouth].append(new_record)
    
        # 更新类别索引
        if category in self.category_index:
            self.category_index[category].append(new_record)

        # 保存所有记录（覆盖写入，但self.records已包含全部数据）
        print(f"当前记录数量: {len(self.records)}")  # 调试输出
        self.save_records()
        print("记录添加成功！")


    @profile
    def query_records(self, start_date:datetime = None, end_date:datetime = None, category:str = None):
        """
        查询收支记录
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param category: 收支类别
        :return: 查询结果列表
        """
        #results = self.records
        #if start_date:
        #    results = [record for record in results if record.date >= start_date]
        #if end_date:
        #    results = [record for record in results if record.date <= end_date]
        #if category:
        #    results = [record for record in results if record.category == category]
        #return results
        """使用索引加速查询"""
        results = self.records
        
        # 先应用类别过滤（若有索引）
        if category and category in self.category_index:
            results = self.category_index[category]
        
        # 日期范围过滤（利用索引减少遍历）
        if start_date or end_date:
            filtered = []
            # 提取所有可能包含目标日期的年月
            if start_date and end_date:
                # 生成日期范围内的所有年月
                date_range = set()
                current = start_date
                while current <= end_date:
                    date_range.add(current.strftime("%Y-%m"))
                    # 计算下一个月
                    month = current.month + 1
                    year = current.year
                    if month > 12:
                        month = 1
                        year += 1
                    current = datetime.date(year, month, 1)  # 每月第一天
                
                # 从索引中获取可能的记录
                for ym in date_range:
                    if ym in self.date_index:
                        filtered.extend(self.date_index[ym])
            else:
                filtered = results
        
            # 二次过滤确保日期在范围内
            results = [r for r in filtered 
                    if (not start_date or r.date >= start_date) 
                    and (not end_date or r.date <= end_date)]
    
        return results

    @profile
    def calculate_total(self, category=None):
        """
        统计收支总额
        :param category: 收支类别
        :return: 总金额
        """
        total = 0
        for record in self.records:
            if category and record.category != category:
                continue
            if record.category == "收入":
                total += record.amount
            elif record.category == "支出":
                total -= record.amount
        return total