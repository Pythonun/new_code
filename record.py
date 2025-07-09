class Record:
    def __init__(self, date, category:str, amount:float, description:str):
        """
        初始化收支记录对象
        :param date: 记录日期
        :param category: 收支类别（收入或支出）
        :param amount: 金额
        :param description: 描述
        """
        self.date = date
        self.category = category
        self.amount = amount
        self.description = description

    def __str__(self):
        """
        返回收支记录的字符串表示
        """
        return f"日期：{self.date}，类别：{self.category}，金额：{self.amount}，描述：{self.description}"