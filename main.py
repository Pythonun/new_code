from account import Account
import datetime
#import random

"""
def add_test_records(account, num_records=1000):
    #批量添加测试记录
    categories = ["收入", "支出"]
    descriptions = ["工资", "餐饮", "购物", "交通", "娱乐"]
    
    for i in range(num_records):
        year = random.randint(2020, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 避免日期无效
        date = datetime.date(year, month, day)
        category = random.choice(categories)
        amount = random.uniform(1, 10000)
        description = random.choice(descriptions)
        
        account.add_record(date, category, amount, description)
        if i % 100 == 0:
            print(f"已添加 {i} 条测试记录")
"""

def display_menu():
    """
    显示菜单
    """
    print("\n===== 个人记账本 =====")
    print("1. 添加收支记录")
    print("2. 查询收支记录")
    print("3. 统计收支总额")
    print("4. 退出记账本")
#    print("5. 批量添加测试记录")

def get_valid_date(prompt):
    """
    获取有效的日期输入，包含格式和数值验证
    :param prompt: 提示信息
    :return: 有效的datetime.date对象
    """
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            print("日期格式错误，请使用YYYY-MM-DD格式")
            continue

        try:
            # 严格验证日期格式和有效性
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            # 检查月份和日期的有效性
            year, month, day = date.year, date.month, date.day
            
            # 额外验证（可根据需要添加）
            if month < 1 or month > 12:
                raise ValueError("月份必须在1-12之间")
            if day < 1:
                raise ValueError("日期必须大于0")
            
            # 检查每个月的最大天数
            if month in [4, 6, 9, 11] and day > 30:
                raise ValueError(f"{month}月最多有30天")
            if month == 2:
                # 闰年2月29天，非闰年2月28天
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                if day > (29 if is_leap else 28):
                    raise ValueError(f"闰年2月最多有29天，非闰年最多有28天")
            elif month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                if day > 31:
                    raise ValueError(f"{month}月最多有31天")
            
            return date.date()
        except ValueError as e:
            print(f"日期输入错误：{e}，请使用格式：YYYY-MM-DD")
        except KeyboardInterrupt:
            print("\n操作已取消，返回菜单...")
            return None
        except Exception as e:
            print(f"未知错误：{e}，请重新输入")
            
def get_valid_number(prompt):
    """获取有效的数字输入（正数）"""
    while True:
        num_str = input(prompt).strip()
        if not num_str:
            print("错误：输入不能为空，请重新输入")
            continue
        try:
            num = float(num_str)
            if num <= 0:
                print("错误：金额必须大于0，请重新输入")
                continue
            return num
        except ValueError:
            print("错误：请输入有效的数字，例如：100.5")

def main():
    account = Account()
    while True:
        display_menu()
        choice = input("请输入您的选择（1-4）：")
        if choice == "1":
            date = get_valid_date("请输入记录日期（格式：YYYY-MM-DD）：")
            category = input("请输入收支类别（收入或支出）：")
            if not category:
                print("错误：类别不能为空，请重新输入")
                continue
            if category not in ["收入", "支出"]:
                print("错误：类别必须为'收入'或'支出'")
                continue
                # 增强金额输入验证
            amount = get_valid_number("请输入金额：")
            description = input("请输入描述：").strip()
            if not description:
                description = "无"  # 设置默认描述
            
            account.add_record(date, category, amount, description)
        elif choice == "2":
            start_date = input("请输入开始日期（格式：YYYY-MM-DD，可选）：")
            end_date = input("请输入结束日期（格式：YYYY-MM-DD，可选）：")
            category = input("请输入收支类别（收入或支出，可选）：")
            if start_date:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            if end_date:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            results = account.query_records(start_date, end_date, category)
            if results:
                print("\n查询结果：")
                for record in results:
                    print(record)
            else:
                print("未相关找到记录！")
        elif choice == "3":
            category = input("请输入收支类别（收入或支出，可选）：")
            total = account.calculate_total(category)
            print(f"总金额：{total}")
        elif choice == "4":
            print("感谢使用个人记账本，再见！")
            break
        
#        elif choice == "5":  # 新增菜单项处理
#            count = int(input("请输入要添加的测试记录数量（默认1000）：") or "1000")
#            add_test_records(account, count)
#            print(f"成功添加 {count} 条测试记录")
        
        else:
            print("无效的选择，请重新输入！")

if __name__ == "__main__":
    main()