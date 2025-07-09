import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# 设置页面配置
st.set_page_config(
    page_title="数据分析仪表板",
    layout="wide"
)

# 缓存数据加载函数
@st.cache_data
def load_data(file):
    """缓存数据加载，避免重复读取"""
    return pd.read_csv(file)

# 页面标题
st.title("交互式数据分析工具")

# 初始化df变量（避免未定义错误）
df = None

# 侧边栏
with st.sidebar:
    st.header("数据配置")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])
    st.markdown("""
    [示例CSV文件下载](https://raw.githubusercontent.com/dataprofessor/data/master/delaney_solubility_with_descriptors.csv)
    """)
    
    # 使用示例数据按钮
    use_sample = st.button("使用内置示例数据")
    if use_sample:
        sample_data = """产品名称,类别,地区,销售额,销售量,利润率,日期
智能手机,电子产品,华东,89200,120,0.18,2025-01-01
笔记本电脑,电子产品,华北,125400,75,0.22,2025-01-01
平板电脑,电子产品,华南,45800,90,0.15,2025-01-01
蓝牙耳机,电子产品,华东,32500,250,0.25,2025-01-01
智能手表,电子产品,华北,56300,130,0.21,2025-01-01
咖啡,食品饮料,华东,18700,320,0.32,2025-01-01
茶叶,食品饮料,华南,24500,180,0.28,2025-01-01
巧克力,食品饮料,华北,15600,240,0.35,2025-01-01
饼干,食品饮料,华东,12400,160,0.26,2025-01-01
矿泉水,食品饮料,华南,9800,450,0.18,2025-01-01
运动鞋,服装鞋帽,华北,65400,120,0.22,2025-01-02
运动服,服装鞋帽,华东,78900,95,0.25,2025-01-02
牛仔裤,服装鞋帽,华南,45600,160,0.23,2025-01-02
T恤,服装鞋帽,华北,32100,280,0.19,2025-01-02
连衣裙,服装鞋帽,华东,56700,110,0.28,2025-01-02
冰箱,家电,华南,125400,40,0.25,2025-01-02
洗衣机,家电,华北,98700,55,0.23,2025-01-02
电视,家电,华东,156800,35,0.27,2025-01-02
空调,家电,华南,189500,42,0.31,2025-01-02
电饭煲,家电,华北,32500,120,0.20,2025-01-02"""
        df = pd.read_csv(io.StringIO(sample_data))

    # 数据参数设置
    st.header("分析参数")
    
    # 数据筛选（仅在数据加载成功后显示）
    st.header("数据筛选")
    if uploaded_file is not None or use_sample:
        # 确保df已正确加载
        if df is None and uploaded_file is not None:
            df = load_data(uploaded_file)
        
        if df is not None and not df.empty:
            # 先定义数值列和分类列（解决NameError）
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            # 处理缺失值
            df_clean = df.dropna(subset=numeric_cols) if numeric_cols else df
            
            # 分类列筛选
            for col in categorical_cols:
                unique_values = df[col].dropna().unique().tolist()  # 排除NaN值
                if unique_values:  # 仅当有有效值时显示筛选器
                    selected_values = st.multiselect(
                        f"筛选 {col}",
                        unique_values,
                        default=unique_values
                    )
                    df = df[df[col].isin(selected_values)]
            
            # 数值列筛选
            for col in numeric_cols:
                # 计算有效范围（避免NaN）
                col_data = df_clean[col].dropna()
                if not col_data.empty:
                    col_min = float(col_data.min())
                    col_max = float(col_data.max())
                    
                    if col_min == col_max:
                        st.info(f"{col} 的所有值均为 {col_min}，无需筛选")
                    else:
                        min_val, max_val = st.slider(
                            f"筛选 {col}",
                            col_min,
                            col_max,
                            (col_min, col_max)
                        )
                        df = df[(df[col] >= min_val) & (df[col] <= max_val)]
                else:
                    st.warning(f"{col} 列无有效数值，跳过筛选")
            
            # 显示筛选后的数据形状
            st.write(f"筛选后数据形状: {df.shape}")
        else:
            st.warning("未加载有效数据，无法筛选")
    else:
        st.info("请上传文件或使用示例数据后进行筛选")


# 主内容区域（数据分析）
if df is not None or uploaded_file is not None:
    # 优先使用示例数据的df，否则处理上传文件
    if df is None and uploaded_file is not None:
        st.subheader("数据概览")
        try:
            # 检查文件是否为空
            if uploaded_file.size == 0:
                st.error("上传的文件为空，请上传有效的CSV文件")
            else:
                st.info("正在分析文件格式...")
                
                # 读取前1000字节预览
                preview_bytes = uploaded_file.read(1000)
                encodings = ['utf-8', 'gbk', 'latin-1', 'utf-16']
                preview_text = None
                
                for encoding in encodings:
                    try:
                        preview_text = preview_bytes.decode(encoding)
                        st.success(f"使用 {encoding} 编码成功预览文件")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if preview_text is None:
                    st.warning("无法使用常见编码解码文件，将尝试二进制分析")
                    preview_text = str(preview_bytes[:300]) + "..."
                
                # 显示文件预览
                with st.expander("文件内容预览"):
                    st.code(preview_text)
                
                # 自动检测分隔符
                delimiters = [',', ';', '\t', '|']
                detected_delimiter = ','
                for delimiter in delimiters:
                    if delimiter in preview_text:
                        detected_delimiter = delimiter
                        st.info(f"检测到可能的分隔符: '{delimiter}'")
                        break
                
                # 重置文件指针并尝试解析
                uploaded_file.seek(0)
                parse_success = False
                error_messages = []
                
                for encoding in encodings:
                    for delimiter in [detected_delimiter, ',', ';', '\t']:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(
                                uploaded_file,
                                delimiter=delimiter,
                                encoding=encoding,
                                on_bad_lines='skip',
                                engine='python'
                            )
                            
                            if not df.empty:
                                st.success(f"使用 encoding='{encoding}', delimiter='{delimiter}' 成功解析数据")
                                parse_success = True
                                break
                        except Exception as e:
                            error_messages.append(f"尝试 encoding='{encoding}', delimiter='{delimiter}': {str(e)}")
                            continue
                    if parse_success:
                        break
                
                if not parse_success:
                    st.error("无法解析文件内容。以下是尝试的策略和错误:")
                    for msg in error_messages[:5]:  # 只显示前5个错误
                        st.warning(msg)
                    
                    # 手动解析选项
                    st.subheader("手动设置解析参数")
                    manual_encoding = st.selectbox("选择编码", encodings)
                    manual_delimiter = st.selectbox("选择分隔符", delimiters)
                    
                    if st.button("尝试手动解析"):
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(
                                uploaded_file,
                                delimiter=manual_delimiter,
                                encoding=manual_encoding,
                                on_bad_lines='skip',
                                engine='python'
                            )
                            if not df.empty:
                                st.success("手动解析成功")
                            else:
                                st.error("手动解析失败，文件可能为空或格式错误")
                        except Exception as e:
                            st.error(f"手动解析错误: {str(e)}")
        except Exception as e:  # 添加缺失的except块
            st.error(f"处理文件时出错: {str(e)}")

    # 数据分析（仅当df有效时执行）
    if df is not None and not df.empty:
        # 显示数据概览
        st.subheader("数据概览")
        st.write(f"数据形状: {df.shape}")
        st.dataframe(df.head())
        
        # 基本信息展开栏
        with st.expander("数据基本信息"):
            buffer = io.StringIO()
            df.info(buf=buffer)
            st.text(buffer.getvalue())
        
        with st.expander("数据统计摘要"):
            st.dataframe(df.describe())
        
        # 数据分析部分
        st.subheader("数据分析")
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # 1. 相关性分析
        if len(numeric_cols) > 1:
            st.subheader("📊 相关性分析")
            corr_cols = st.multiselect(
                "选择要分析的数值列",
                numeric_cols,
                default=numeric_cols[:5] if len(numeric_cols) >5 else numeric_cols  # 避免默认过多
            )
            
            if len(corr_cols) > 1:
                corr = df[corr_cols].corr()
                with st.expander("相关系数矩阵"):
                    st.dataframe(corr)
                
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                plt.title("相关性热力图")
                st.pyplot(fig)
        
        # 2. 分布分析
        if len(numeric_cols) > 0:
            st.subheader("📊 分布分析")
            dist_col = st.selectbox("选择要分析的列", numeric_cols)
            chart_type = st.selectbox("选择图表类型", ["直方图", "箱线图", "密度图"])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            if chart_type == "直方图":
                sns.histplot(df[dist_col], kde=True, ax=ax)
                plt.title(f"{dist_col} 的直方图")
            elif chart_type == "箱线图":
                sns.boxplot(y=df[dist_col], ax=ax)
                plt.title(f"{dist_col} 的箱线图")
            elif chart_type == "密度图":
                sns.kdeplot(df[dist_col], fill=True, ax=ax)
                plt.title(f"{dist_col} 的密度图")
            st.pyplot(fig)
        
        # 3. 分组分析
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            st.subheader("📊 分组分析")
            group_col = st.selectbox("选择分组列", categorical_cols)
            value_col = st.selectbox("选择数值列", numeric_cols)
            agg_func = st.selectbox("选择聚合函数", ["均值", "总和", "最大值", "最小值", "计数"])
            
            agg_func_map = {
                "均值": "mean", "总和": "sum", "最大值": "max", "最小值": "min", "计数": "count"
            }
            
            grouped_data = df.groupby(group_col)[value_col].agg(agg_func_map[agg_func]).reset_index()
            st.dataframe(grouped_data)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(x=group_col, y=value_col, data=grouped_data, ax=ax)
            plt.title(f"{group_col} 分组的 {value_col} {agg_func}")
            plt.xticks(rotation=45)
            st.pyplot(fig)
else:
    st.info("请上传CSV文件或点击'使用内置示例数据'开始分析")