"""
交互式数据分析工具（Streamlit 应用）
本应用为用户提供了一个可上传 CSV 文件或使用内置示例数据的交互式数据分析仪表板，支持数据筛选、采样、相关性分析、分布分析和分组分析等功能。主要特性如下：
功能概述:
- 支持上传 CSV 文件或一键加载内置示例数据。
- 自动识别数值型和分类型字段，支持多条件筛选。
- 可自定义相关性热力图的阈值、显示风格和颜色主题。
- 支持数据采样，便于大数据集的快速分析。
- 提供数据概览、基本信息、统计摘要等数据展示。
- 相关性分析：可视化相关系数矩阵和热力图，支持阈值过滤与系数显示。
- 分布分析：支持直方图、箱线图、密度图等多种分布可视化。
- 分组分析：支持按分类字段分组，对数值字段进行多种聚合（均值、总和、最大、最小、计数），并可自定义显示前N组。
- 所有参数和数据状态均通过 Streamlit session_state 管理，保证交互体验和数据一致性。
主要依赖:
- streamlit
- pandas
- numpy
- matplotlib
- seaborn
适用场景:
- 快速数据探索与可视化分析
- 非技术用户的交互式数据分析
- 数据科学教学与演示
使用方法:
1. 运行本脚本以启动 Streamlit 应用。
2. 在侧边栏上传 CSV 文件或点击“使用内置示例数据”。
3. 根据需要设置分析参数、筛选条件和采样比例。
4. 在主界面查看数据概览、相关性分析、分布分析和分组分析结果。
注意事项:
- 采样和筛选操作会影响后续分析结果。
- 支持中文字段和数据，已设置中文字体兼容。
- 若上传文件编码异常，自动尝试不同编码读取。
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import matplotlib.font_manager as fm

# 设置中文字体
sns.set_theme(font='SimHei')  # Windows/Linux
# sns.set_theme(font='WenQuanYi Micro Hei')  # Linux
# sns.set_theme(font='Heiti TC')  # macOS

# 设置 matplotlib 的字体
plt.rcParams['font.family'] = 'SimHei'  # 或者其他系统默认中文字体
plt.rcParams['axes.unicode_minus'] = False # 修复负号

# 初始化会话状态（保存关键变量，避免重置）
if 'df' not in st.session_state:
    st.session_state.df = None  # 保存数据
if 'use_sample' not in st.session_state:
    st.session_state.use_sample = False  # 标记是否使用示例数据
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False  # 标记是否上传了文件
if 'original_df' not in st.session_state:
    st.session_state.original_df = None  # 保存原始数据

# 设置页面配置
st.set_page_config(
    page_title="数据分析仪表板",
    layout="wide"
)

# 页面标题
st.title("交互式数据分析工具")

# 侧边栏
with st.sidebar:
    st.header("数据配置")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])
    st.markdown("""
    [示例CSV文件下载](https://raw.githubusercontent.com/dataprofessor/data/master/delaney_solubility_with_descriptors.csv)
    """)
    
    # 使用示例数据按钮（通过session_state保存状态）
    if st.button("使用内置示例数据"):
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
        st.session_state.df = pd.read_csv(io.StringIO(sample_data))
        st.session_state.use_sample = True  # 标记使用示例数据
        st.session_state.uploaded = False  # 重置上传状态
        st.session_state.original_df = st.session_state.df.copy()  # 保存原始数据

    # 上传文件时更新df（通过session_state保存）
    if uploaded_file is not None:
        try:
            st.session_state.df = pd.read_csv(uploaded_file, sep=',', encoding='utf-8', on_bad_lines='skip')
            st.session_state.uploaded = True  # 标记已上传
            st.session_state.use_sample = False  # 重置示例数据状态
            st.session_state.original_df = st.session_state.df.copy()  # 保存原始数据
        except UnicodeDecodeError:
            try:
                st.session_state.df = pd.read_csv(uploaded_file, sep=',', encoding='latin1', on_bad_lines='skip')
                st.session_state.uploaded = True  # 标记已上传
                st.session_state.use_sample = False  # 重置示例数据状态
                st.session_state.original_df = st.session_state.df.copy()  # 保存原始数据
            except Exception as e:
                st.error(f"读取 CSV 文件时出错: {e}")
        except Exception as e:
            st.error(f"读取 CSV 文件时出错: {e}")

    # 如果删除上传的文件且没有使用示例数据，则重置数据
    if uploaded_file is None and not st.session_state.use_sample:
        st.session_state.df = None
        st.session_state.original_df = None
        st.session_state.uploaded = False

    # 分析参数设置（关键：依赖session_state中的df）
    st.header("分析参数")
    # 仅当df存在且非空时显示参数
    if st.session_state.df is not None and not st.session_state.df.empty:
        df = st.session_state.df  # 从会话状态获取df

        # 1. 相关性分析参数
        st.subheader("相关性分析参数")
        corr_threshold = st.slider(
            "相关性热力图显示阈值",
            min_value=0.0, max_value=1.0, value=0.0, step=0.1
        )
        corr_annot = st.checkbox("显示相关系数值", value=True)

        # 2. 可视化参数
        st.subheader("可视化参数")
        plot_style = st.selectbox(
            "图表风格",
            ["默认", "白色网格", "深色背景", "无网格"],
            index=0
        )
        style_mapping = {
            "默认": "whitegrid", 
            "白色网格": "whitegrid", 
            "深色背景": "darkgrid",
            "无网格": "ticks"
        }
        selected_style = style_mapping[plot_style]

        color_palette = st.selectbox(
            "图标颜色主题",
            ["coolwarm", "viridis", "pastel", "Set2", "tab10"],
            index=0
        )

        # 为热力图单独定义颜色映射选项
        heatmap_cmaps = {
            "coolwarm": "coolwarm",  # 保持默认映射
            "viridis": "viridis",    # 保持默认映射
            "pastel": "YlOrRd",      # 替换为有效的连续颜色映射
            "Set2": "BuGn",          # 替换为有效的连续颜色映射
            "tab10": "RdBu"          # 替换为有效的连续颜色映射
        }
        heatmap_cmap = heatmap_cmaps[color_palette]


        # 3. 数据采样参数
        st.subheader("数据采样参数")
        if st.session_state.df is not None and not st.session_state.df.empty:
            total_rows = len(st.session_state.original_df) # 使用原始数据的行数
            sample_ratio = st.slider(
                f"数据采样比例（共{total_rows}行）",
                min_value=0.1, max_value=1.0, value=1.0, step=0.1
            )
            if sample_ratio <= 1.0:
                if st.button("确认采样"):
                    if total_rows > 0:
                        st.session_state.df = st.session_state.original_df.sample(frac=sample_ratio, random_state=42)
                        st.success(f"已采样 {sample_ratio*100}% 的数据（{len(st.session_state.df)}行）")
                    else:
                        st.error("数据集为空，无法进行采样")
            else:
                st.session_state.df = st.session_state.original_df.copy()  # 当比例为1.0时，恢复原始数据
        st.write(f"当前数据形状: {st.session_state.df.shape}")
        st.info("请注意，采样后可能会影响相关性分析和分组分析的结果")

        # 4. 分组分析参数
        st.subheader("分组分析参数")
        top_n_groups = st.slider(
            "仅显示前N个组",
            min_value=3, max_value=20, value=10, step=1
        )

        # 保存参数到会话状态
        st.session_state.params = {
            "corr_threshold": corr_threshold,
            "corr_annot": corr_annot,
            "plot_style": selected_style,
            "color_palette": color_palette,  # 用于柱状图等
            "heatmap_cmap": heatmap_cmap,    # 专门用于热力图
            "top_n_groups": top_n_groups
        }
    else:
        st.info("请上传文件或使用示例数据后设置参数")
        st.session_state.params = None  # 无数据时参数为空

    # 数据筛选（基于session_state中的df）
    st.header("数据筛选")

    if st.session_state.df is not None and not st.session_state.df.empty:
        df = st.session_state.df
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # 可以在每次筛选前保存原始数据，避免筛选结果相互影响
        original_df = st.session_state.df.copy()
        
        # 分类列筛选
        for col in categorical_cols:
            unique_values = original_df[col].dropna().unique().tolist()
            if unique_values:
                selected_values = st.multiselect(
                    f"筛选 {col}",
                    unique_values,
                    default=unique_values
                )
                st.session_state.df = st.session_state.df[st.session_state.df[col].isin(selected_values)]



        # 数值列筛选
        for col in numeric_cols:
            col_data = original_df[col].dropna()
            if not col_data.empty:
                col_min = float(col_data.min())
                col_max = float(col_data.max())
                if col_min != col_max:
                    min_val, max_val = st.slider(
                        f"筛选 {col}",
                        col_min, col_max, (col_min, col_max)
                    )
                    st.session_state.df = st.session_state.df[
                        (st.session_state.df[col] >= min_val) & 
                        (st.session_state.df[col] <= max_val)
                    ]
                else:
                    st.info(f"{col} 的值均为 {col_min}，无需筛选")

        st.write(f"筛选后数据形状: {st.session_state.df.shape}")
    else:
        st.info("无数据可筛选")


# 主内容区域（数据分析）
if st.session_state.df is not None and not st.session_state.df.empty:
    df = st.session_state.df
    params = st.session_state.params

    # 应用可视化风格
    if params:
        sns.set_style(params["plot_style"])

    # 数据概览
    st.subheader("数据概览")
    st.write(f"数据形状: {df.shape}")
    st.dataframe(df.head())

    with st.expander("数据基本信息"):
        buffer = io.StringIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue())

    with st.expander("统计摘要"):
        st.dataframe(df.describe())

    # 数据分析
    st.subheader("数据分析")
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # 1. 相关性分析（应用参数）
    if len(numeric_cols) > 1 and params:
        st.subheader("📊 相关性分析")
        corr_cols = st.multiselect(
            "选择数值列",
            numeric_cols,
            default=numeric_cols[:5] if len(numeric_cols) >5 else numeric_cols
        )
        if len(corr_cols) > 1:
            corr = df[corr_cols].corr()
            if params["corr_threshold"] > 0:
                mask = np.abs(corr) < params["corr_threshold"]
                corr = corr.mask(mask)
            with st.expander("相关系数矩阵"):
                st.dataframe(corr)
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(
                corr,
                annot=params["corr_annot"],
                cmap=params["heatmap_cmap"],
                mask=mask if params["corr_threshold"] > 0 else None
            )
            plt.title(f"相关性热力图（阈值: {params['corr_threshold']}）")
            st.pyplot(fig)

    # 2. 分布分析
    if len(numeric_cols) > 0 and params:
        st.subheader("📊 分布分析")
        dist_col = st.selectbox("选择列", numeric_cols)
        chart_type = st.selectbox("图表类型", ["直方图", "箱线图", "密度图"])
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_palette(params["color_palette"])
        if chart_type == "直方图":
            sns.histplot(df[dist_col], kde=True, ax=ax)
        elif chart_type == "箱线图":
            sns.boxplot(y=df[dist_col], ax=ax)
        elif chart_type == "密度图":
            sns.kdeplot(df[dist_col], fill=True, ax=ax)
        plt.title(f"{dist_col} 的{chart_type}")
        st.pyplot(fig)

    # 3. 分组分析
    if len(categorical_cols) > 0 and len(numeric_cols) > 0 and params:
        st.subheader("📊 分组分析")
        group_col = st.selectbox("分组列", categorical_cols)
        value_col = st.selectbox("数值列", numeric_cols)
        agg_func = st.selectbox("聚合函数", ["均值", "总和", "最大值", "最小值", "计数"])
        agg_func_map = {"均值": "mean", "总和": "sum", "最大值": "max", "最小值": "min", "计数": "count"}
        grouped_data = df.groupby(group_col)[value_col].agg(agg_func_map[agg_func]).reset_index()
        grouped_data = grouped_data.sort_values(by=value_col, ascending=False).head(params["top_n_groups"])
        st.dataframe(grouped_data)
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(
            x=group_col, y=value_col, 
            data=grouped_data, 
            palette=params["color_palette"]
        )
        plt.title(f"{group_col} 分组的 {value_col} {agg_func}（前{params['top_n_groups']}组）")
        plt.xticks(rotation=45)
        st.pyplot(fig)
else:
    st.info("请上传CSV文件或点击'使用内置示例数据'开始分析")
