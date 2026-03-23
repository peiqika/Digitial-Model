import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import joblib
import warnings
import time
import streamlit as st
import pickle
import json
from io import BytesIO
import math
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 强制启用滚动 - 解决 Chrome 滚动问题
st.markdown("""
<style>
    /* 修复主容器滚动 */
    .main > div {
        overflow-y: auto !important;
        height: 100vh !important;
    }
    
    /* 修复 block 容器滚动 */
    .block-container {
        overflow-y: auto !important;
        max-height: none !important;
        padding-bottom: 2rem !important;
    }
    
    /* 确保 body 可以滚动 */
    body {
        overflow-y: auto !important;
        height: auto !important;
    }
    
    /* 修复 iframe 相关问题 */
    iframe {
        overflow: auto !important;
    }
    
    /* 移除任何可能导致滚动失效的样式 */
    .stApp {
        overflow-y: auto !important;
    }
    
    /* 确保滚动条可见 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# 设置页面配置
st.set_page_config(
    page_title="Digital Assembly Simulator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 白色主题版 + 超大输入框 + 字体放大 + 间距优化 + 结果界面优化
st.markdown("""
<style>
    /* 全局白色背景 */
    .stApp {
        background-color: #FFFFFF;
    }

    /* 主内容区域背景 */
    .main > div {
        background-color: #FFFFFF;
    }

    /* 侧边栏背景 - 浅灰色 */
    section[data-testid="stSidebar"] {
        background-color: #F5F5F5;
    }

    /* 主标题样式 - 白色主题 */
    .main-header {
        text-align: center;
        color: #2E7D32;
        padding: 15px 0;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 0 0 10px rgba(46, 125, 50, 0.2);
    }

    /* 页面整体内边距调整：左右留白增加 */
    .block-container {
        padding: 0.3rem 0.5rem !important;
    }

    /* 副标题样式 - 白色主题 */
    .section-header {
        color: #2E7D32;
        border-bottom: 2px solid #2E7D32;
        padding-bottom: 8px;
        margin-top: 15px;
        margin-bottom: 10px;
        font-size: 29px !important;
    }

    /* 结果卡片样式 - 白色主题 + 深色文字 */
    .result-card {
        background-color: #F8F9FA;
        border-radius: 8px;
        padding: 5px;
        margin: 5px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #2E7D32;
        font-size: 30px !important;
    }
    
    /* 修改metric值的大小和颜色 */
    .result-card [data-testid="stMetricValue"] {
    font-size: 30px !important;  /* 改为更大一些 */
    color: #000000 !important;      /* 改为纯黑色 */
    }
    
    /* 修改metric标签的大小和颜色 */
    .result-card [data-testid="stMetricLabel"] {
    font-size: 30px !important;   /* 调整标签大小 */
    color: #000000 !important;
    }

    /* 结果卡片内普通文字为深色 */
    .result-card p,
    .result-card .stMarkdown,
    .result-card strong {
        color: #000000 !important;
    }

    /* Pass 样式 - 绿色文字 */
    .result-card .pass {
        color: #000000 !important;
        font-weight: bold;
        font-size: 30px !important;
        background: none !important;
        padding: 0;
        border: none;
        display: inline-block;
    }

    /* Fail 样式 - 红色文字 */
    .result-card .fail {
        color: #000000 !important;
        font-weight: bold;
        font-size: 30px !important;
        background: none !important;
        padding: 0;
        border: none;
        display: inline-block;
    }

    /* 输入组样式 - 白色主题 */
    .input-group {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 28px 28px 18px 28px;
        margin: 2px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #000000;
        height: 100%;
    }

    /* 列之间的间距：为每列添加左右内边距 */
    div[data-testid="column"] {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }

    /* 每个参数项容器增加底部间距 */
    .input-group .element-container {
        margin-bottom: 14px !important;
    }

    /* 参数名称标签 - 放大到28px */
    .param-label {
        font-weight: 800;
        color: #000000;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        font-size: 28px !important;
        line-height: 0.5;
        word-break: break-word;
    }

    /* 参数范围显示 - 放大到18px */
    .range-display {
        font-size: 22px !important;
        color: #000000;
        margin-top: 2px;
        margin-bottom: 5px;
        font-weight: 600;
    }

    /* 输入框容器放大 */
    .stNumberInput {
        width: 100% !important;
    }

    /* 输入框数字超大放大 */
    .stNumberInput input {
        border-radius: 6px;
        border: 2px solid #E0E0E0;
        background-color: #FFFFFF;
        color: #000000;
        transition: all 0.3s ease;
        font-size: 30px !important;
        font-weight: 800 !important;
        padding: 5px 8px !important;
        height: 100px !important;
        width: 100% !important;
    }

    .stNumberInput input:focus {
        border-color: #2E7D32;
        box-shadow: 0 0 0 4px rgba(46, 125, 50, 0.2);
        background-color: #FFFFFF;
    }

    /* 输入框旁边的按钮放大 */
    .stNumberInput button {
        height: 100px !important;
        width: 40px !important;
        font-size: 20px !important;
    }

    /* 状态指示器旁边的文本（✓/✗）超大放大 */
    .status-indicator + span {
        font-size: 30px !important;
        font-weight: bold !important;
        margin-left: 12px;
    }

    /* 状态指示器放大 */
    .status-indicator {
        display: inline-block;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50%;
        margin-left: 10px;
    }

    .status-in-range {
        background-color: #2E7D32;
        box-shadow: 0 0 10px #2E7D32;
    }

    .status-out-of-range {
        background-color: #D32F2F;
        box-shadow: 0 0 10px #D32F2F;
    }

    /* 按钮样式 - 白色主题，放大 */
    .stButton > button {
        background-color: #2E7D32;
        color: white;
        border: 1px solid #2E7D32;
        font-weight: 800;
        transition: all 0.3s ease;
        font-size: 30px !important;
        padding: 0.5rem 0.5rem !important;
        height: 80px !important;
    }

    .stButton > button:hover {
        background-color: #1B5E20;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3);
    }

    /* 紧凑布局调整 */
    .element-container {
        margin-bottom: 0.5rem;
    }

    /* 侧边栏文字颜色 */
    .css-1d391kg, .css-163ttbj, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown {
        color: #333333;
    }

    /* 指标卡片默认颜色 */
    [data-testid="stMetricValue"] {
        color: #000000;
        font-size: 30px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #000000;
        font-size: 30px !important;
    }

    /* 数据表格样式 - 白色主题 */
    .stDataFrame {
        background-color: #FFFFFF;
    }

    .stDataFrame [data-testid="StyledDataFrameDataCell"] {
        background-color: #FFFFFF;
        color: #333333;
        font-size: 30px !important;
    }

    /* 展开器样式 - 白色主题 */
    .streamlit-expanderHeader {
        background-color: #F8F9FA;
        color: #333333;
        border: 1px solid #E0E0E0;
        font-size: 30px !important;
    }

    .streamlit-expanderContent {
        background-color: #F8F9FA;
        color: #333333;
        border: 1px solid #E0E0E0;
    }

    /* 警告框样式 - 白色主题，放大 */
    .stAlert {
        background-color: #FFEBEE;
        color: #D32F2F;
        border: 1px solid #FFCDD2;
        font-size: 30px !important;
        padding: 5px !important;
    }

    /* 成功消息样式 - 白色主题，放大 */
    .stSuccess {
        background-color: #E8F5E9;
        color: #2E7D32;
        border: 5px solid #C8E6C9;
        font-size: 30px !important;
        padding: 5px !important;
    }

    /* 信息框样式 - 白色主题 */
    .stInfo {
        background-color: #E3F2FD;
        color: #1976D2;
        border: 1px solid #BBDEFB;
    }

    /* 下载按钮样式 */
    .stDownloadButton > button {
        background-color: #F5F5F5;
        color: #333333;
        border: 1px solid #2E7D32;
        font-size: 30px !important;
        padding: 0.5rem 1rem !important;
    }

    .stDownloadButton > button:hover {
        background-color: #E0E0E0;
        border-color: #2E7D32;
    }

    /* 页脚样式 */
    footer {
        color: #666666;
    }

    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background-color: #2E7D32;
    }

    /* 欢迎信息文字颜色 */
    .welcome-text h3 {
        color: #333333 !important;
        font-size: 1.5rem;
    }
    .welcome-text p {
        color: #666666 !important;
        font-size: 1.5rem;
    }

    /* 分隔线样式调整（参数之间的细线） */
    hr {
        margin-top: 20px !important;
        margin-bottom: 20px !important;
        border-color: #E0E0E0 !important;
        border-width: 2px !important;
    }

    /* 文本区域样式 */
    .stTextArea textarea {
        background-color: #FFFFFF;
        color: #333333;
        border: 1px solid #E0E0E0;
        font-size: 30px !important;
    }

    /* 选择框样式 */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF;
        border-color: #E0E0E0;
        font-size: 30px !important;
    }

    /* 滑块样式 */
    .stSlider div[data-baseweb="slider"] {
        background-color: #FFFFFF;
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F8F9FA;
    }

    .stTabs [data-baseweb="tab"] {
        color: #666666;
        font-size: 30px !important;
    }

    .stTabs [aria-selected="true"] {
        color: #2E7D32 !important;
    }

    /* 输入框容器内的标签隐藏 */
    .stNumberInput label {
        display: none !important;
    }

    /* 确保输入框占据整个宽度 */
    div[data-testid="column"] .stNumberInput {
        width: 100% !important;
    }

    /* 输入框和状态指示器的容器布局优化 */
    div.row-widget.stHorizontal {
        align-items: center !important;
    }
</style>
""", unsafe_allow_html=True)

# 应用标题
st.markdown('<div class="main-header">Digital Assembly Simulator</div>', unsafe_allow_html=True)

# 检查图片文件是否存在 - 自适应全宽
if os.path.exists("Stand.png"):
    st.image("Stand.png", use_column_width=True)
else:
    st.info("📷 Assembly diagram image (Stand.png) not found")

# 初始化session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'simulation_count' not in st.session_state:
    st.session_state.simulation_count = 0
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None
if 'success_rate' not in st.session_state:
    st.session_state.success_rate = 0
if 'input_values' not in st.session_state:
    st.session_state.input_values = {}
if 'input_status' not in st.session_state:
    st.session_state.input_status = {}


# 定义预测函数
def predict_torque_smart(feature_values, linear_model, pt, scaler, selected_features, historical_data, all_features):
    """智能预测函数，处理特征维度问题"""
    if isinstance(feature_values, dict):
        values_array = [feature_values.get(feature, historical_data[feature].mean())
                        for feature in selected_features]
    else:
        values_array = feature_values

    # 创建82维的DataFrame（与训练时一致）
    sample_82 = pd.DataFrame([historical_data.mean()])

    # 将输入的12个特征值赋给对应的列
    for i, feature in enumerate(selected_features):
        if feature in sample_82.columns:
            sample_82[feature] = values_array[i]

    try:
        # 预处理流程
        X_transformed = pt.transform(sample_82)
        X_transformed_df = pd.DataFrame(X_transformed, columns=all_features)
        X_scaled = scaler.transform(X_transformed_df)
        X_scaled_df = pd.DataFrame(X_scaled, columns=all_features)
        X_final = X_scaled_df[selected_features]

        # 预测
        prediction = linear_model.predict(X_final)[0]
        return prediction
    except Exception as e:
        st.warning(f"主预测方法失败，使用备用方法: {e}")
        return predict_torque_fallback(values_array, linear_model, selected_features, historical_data)


def predict_torque_fallback(feature_values, linear_model, selected_features, historical_data):
    """备用预测方法"""
    normalized_features = []
    for i, feature in enumerate(selected_features):
        value = feature_values[i]
        mean_val = historical_data[feature].mean()
        std_val = historical_data[feature].std()
        normalized = (value - mean_val) / std_val if std_val != 0 else 0
        normalized_features.append(normalized)

    prediction = linear_model.intercept_
    for i, coef in enumerate(linear_model.coef_):
        prediction += coef * normalized_features[i]
    return prediction


# 定义给定的特征取值范围
given_ranges = {
    '⌀6圆孔碟形华司材料厚度1': [0.95, 1],
    '⌀6椭圆孔单钩华司料厚3': [1.95, 2],
    '⌀6圆孔碟形华司材料厚度2': [0.95, 1],
    '⌀6椭圆孔单钩华司扁孔直径3': [6, 6.03],
    '⌀6圆孔单钩华司内径2': [5.8, 6.08],
    '轴心扁位总长度-左&右': [31.5, 32.5],
    '轴心总长度': [83.5, 85.5],
    '左扭簧线径': [1.8, 1.85],
    '右扭簧线径': [1.8, 1.85],
    '套筒外径2': [8.9, 9.06],
    '套筒外径1': [8.9, 9.06],
    '套筒内径1': [6.04, 6.12]
}

# 英文特征名映射
feature_mapping = {
    '⌀6圆孔碟形华司材料厚度1': 'Round Hole Disc Washer Material Thickness 1',
    '⌀6椭圆孔单钩华司料厚3': 'Elliptical Hole Single Hook Washer Material Thickness 3',
    '⌀6圆孔碟形华司材料厚度2': 'Round Hole Disc Washer Material Thickness 2',
    '⌀6椭圆孔单钩华司扁孔直径3': 'Elliptical Hole Single Hook Washer Flat Hole Diameter 3',
    '⌀6圆孔单钩华司内径2': 'Round Hole Single Hook Washer Inner Diameter 2',
    '轴心扁位总长度-左&右': 'Total Flat Section Length of Shaft - Left & Right',
    '轴心总长度': 'Total Shaft Length',
    '左扭簧线径': 'Left Torsion Spring Wire Diameter',
    '右扭簧线径': 'Right Torsion Spring Wire Diameter',
    '套筒外径2': 'Sleeve Outer Diameter 2',
    '套筒外径1': 'Sleeve Outer Diameter 1',
    '套筒内径1': 'Sleeve Inner Diameter 1'
}

# 侧边栏 - 紧凑版
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.info("""
    **Digital Assembly Simulator**

    Version: 2.0
    Last Updated: 2024

    Simulates assembly performance based on dimensional parameters.
    """)

    st.markdown("### 📋 Model Status")

    # 加载模型按钮
    if st.button("🔄 Load Models", use_container_width=True, type="primary"):
        try:
            with st.spinner("Loading models..."):
                linear_model = joblib.load('linear_regression_model.pkl')
                pt = joblib.load('power_transformer.pkl')
                scaler = joblib.load('standard_scaler.pkl')
                selected_features = joblib.load('selected_features.pkl')
                historical_data = pd.read_excel('extended.xlsx')

                st.session_state.linear_model = linear_model
                st.session_state.pt = pt
                st.session_state.scaler = scaler
                st.session_state.selected_features = selected_features
                st.session_state.historical_data = historical_data
                st.session_state.all_features = historical_data.columns.tolist()
                st.session_state.model_loaded = True

                st.success("✅ Models loaded successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Failed to load models: {e}")

    st.markdown("---")

    # 检查模型文件状态
    model_status = ""
    files_to_check = [
        "linear_regression_model.pkl",
        "power_transformer.pkl",
        "standard_scaler.pkl",
        "selected_features.pkl",
        "extended.xlsx"
    ]

    for file in files_to_check:
        if os.path.exists(file):
            model_status += f"✅ {file}\n"
        else:
            model_status += f"⚠️ {file}\n"

    st.text_area("File Status", model_status, height=120, disabled=True)

    st.markdown("---")

    # 统计数据
    st.markdown("### 📊 Statistics")
    st.write(f"**Simulations:** {st.session_state.simulation_count}")

    if st.session_state.results:
        recent_torques = [r["torque"] for r in st.session_state.results]
        avg_torque = np.mean(recent_torques) if recent_torques else 0
        st.write(f"**Avg Torque:** {avg_torque:.2f} N·m")

        pass_count = sum(1 for r in st.session_state.results if r["judgment"] == "Pass")
        if st.session_state.simulation_count > 0:
            pass_rate = (pass_count / st.session_state.simulation_count) * 100
            st.write(f"**Pass Rate:** {pass_rate:.1f}%")

    st.markdown("---")

    if st.button("🔄 Clear History", use_container_width=True):
        st.session_state.results = []
        st.session_state.simulation_count = 0
        st.session_state.input_values = {}
        st.session_state.input_status = {}
        st.rerun()

# 主内容区 - 输入参数
st.markdown('<div class="section-header">📐 Input Parameters (mm)</div>', unsafe_allow_html=True)

# 检查模型是否已加载
if not st.session_state.get('model_loaded', False):
    st.warning("⚠️ Please load models first by clicking 'Load Models' button in the sidebar")
else:
    # 获取特征顺序
    selected_features = st.session_state.selected_features

    # 创建两列布局用于参数输入（6行2列）
    col1, col2 = st.columns(2)

    # 存储所有输入值的字典
    all_input_values = {}
    input_status = {}

    # 第1列: 特征1,3,5,7,9,11 (奇数索引)
    with col1:
        st.markdown('<div class="input-group">', unsafe_allow_html=True)

        # 奇数索引：0,2,4,6,8,10
        odd_indices = [0, 2, 4, 6, 8, 10]
        for i, idx in enumerate(odd_indices):
            if idx < len(selected_features):
                feature = selected_features[idx]
                display_name = feature_mapping.get(feature, feature)
                min_val, max_val = given_ranges.get(feature, [0, 1])
                default_val = (min_val + max_val) / 2

                # 获取之前存储的值（如果有）
                previous_value = st.session_state.input_values.get(feature, default_val)

                # 创建带标签和范围显示的输入行
                st.markdown(f'<div class="param-label">{display_name}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="range-display">Range: {min_val:.2f} - {max_val:.2f} mm</div>',
                            unsafe_allow_html=True)

                # 创建两列布局：输入框和状态指示器
                input_col, status_col = st.columns([4, 1])

                with input_col:
                    # 数字输入框
                    input_value = st.number_input(
                        "",
                        min_value=None,
                        max_value=None,
                        value=float(previous_value),
                        step=0.001,
                        format="%.2f",
                        key=f"input_{feature}",
                        label_visibility="collapsed"
                    )

                with status_col:
                    # 检查输入值是否在范围内并显示状态
                    is_in_range = min_val <= input_value <= max_val
                    status_class = "status-in-range" if is_in_range else "status-out-of-range"
                    status_text = "✓" if is_in_range else "✗"

                    # 存储状态
                    input_status[feature] = is_in_range

                    # 根据状态显示不同的颜色
                    if is_in_range:
                        st.markdown(f'<div class="status-indicator {status_class}" title="Within range"></div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-indicator {status_class}" title="Out of range"></div>',
                                    unsafe_allow_html=True)

                    # 在tooltip中显示状态
                    st.markdown(
                        f'<span title="{"Within range" if is_in_range else "Out of range"}">{status_text}</span>',
                        unsafe_allow_html=True)

                # 存储输入值
                all_input_values[feature] = input_value

                # 如果值不在范围内，显示警告
                if not is_in_range:
                    st.warning(
                        f"⚠️ Value ({input_value:.2f}) is outside the recommended range ({min_val:.2f}-{max_val:.2f})",
                        icon="⚠️")

                # 参数之间的分隔线（除了最后一个参数）
                if i < len(odd_indices) - 1:
                    st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)

    # 第2列: 特征2,4,6,8,10,12 (偶数索引)
    with col2:
        st.markdown('<div class="input-group">', unsafe_allow_html=True)

        # 偶数索引：1,3,5,7,9,11
        even_indices = [1, 3, 5, 7, 9, 11]
        for i, idx in enumerate(even_indices):
            if idx < len(selected_features):
                feature = selected_features[idx]
                display_name = feature_mapping.get(feature, feature)
                min_val, max_val = given_ranges.get(feature, [0, 1])
                default_val = (min_val + max_val) / 2

                # 获取之前存储的值（如果有）
                previous_value = st.session_state.input_values.get(feature, default_val)

                # 创建带标签和范围显示的输入行
                st.markdown(f'<div class="param-label">{display_name}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="range-display">Range: {min_val:.2f} - {max_val:.2f} mm</div>',
                            unsafe_allow_html=True)

                # 创建两列布局：输入框和状态指示器
                input_col, status_col = st.columns([4, 1])

                with input_col:
                    # 数字输入框
                    input_value = st.number_input(
                        "",
                        min_value=None,
                        max_value=None,
                        value=float(previous_value),
                        step=0.001,
                        format="%.2f",
                        key=f"input_{feature}",
                        label_visibility="collapsed"
                    )

                with status_col:
                    # 检查输入值是否在范围内并显示状态
                    is_in_range = min_val <= input_value <= max_val
                    status_class = "status-in-range" if is_in_range else "status-out-of-range"
                    status_text = "✓" if is_in_range else "✗"

                    # 存储状态
                    input_status[feature] = is_in_range

                    # 根据状态显示不同的颜色
                    if is_in_range:
                        st.markdown(f'<div class="status-indicator {status_class}" title="Within range"></div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-indicator {status_class}" title="Out of range"></div>',
                                    unsafe_allow_html=True)

                    # 在tooltip中显示状态
                    st.markdown(
                        f'<span title="{"Within range" if is_in_range else "Out of range"}">{status_text}</span>',
                        unsafe_allow_html=True)

                # 存储输入值
                all_input_values[feature] = input_value

                # 如果值不在范围内，显示警告
                if not is_in_range:
                    st.warning(
                        f"⚠️ Value ({input_value:.2f}) is outside the recommended range ({min_val:.2f}-{max_val:.2f})",
                        icon="⚠️")

                # 参数之间的分隔线（除了最后一个参数）
                if i < len(even_indices) - 1:
                    st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)

    # 保存输入值和状态到session state
    st.session_state.input_values = all_input_values
    st.session_state.input_status = input_status

    # 运行模拟按钮
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        submitted = st.button(
            "🚀 Run Simulation",
            use_container_width=True,
            type="primary",
            key="run_simulation"
        )

# 处理模拟运行
if submitted and st.session_state.get('model_loaded', False):
    st.session_state.simulation_count += 1

    with st.spinner("🔬 Running simulation..."):
        # 准备输入值
        input_array = [st.session_state.input_values[feature] for feature in st.session_state.selected_features]

        # 进行预测
        torque_prediction = predict_torque_smart(
            input_array,
            st.session_state.linear_model,
            st.session_state.pt,
            st.session_state.scaler,
            st.session_state.selected_features,
            st.session_state.historical_data,
            st.session_state.all_features
        )

        # 单位换算
        nm_result = torque_prediction * 0.098

        # 判断结果
        if 2.35 <= nm_result <= 2.75:
            judge = "Pass"
            result_style = "pass"
        else:
            judge = "Fail"
            result_style = "fail"

        # 存储结果
        result_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "torque": nm_result,
            "torque_kg_cm": torque_prediction,
            "judgment": judge,
            "parameters": {feature_mapping.get(f, f): st.session_state.input_values[f] for f in
                           st.session_state.selected_features},
            "parameters_status": {feature_mapping.get(f, f): st.session_state.input_status.get(f, True) for f in
                                  st.session_state.selected_features}
        }
        st.session_state.results.append(result_data)

        # 显示成功消息
        st.success(f"✅ Simulation #{st.session_state.simulation_count} completed!")

        # 显示结果 - 仅显示扭矩值和通过与否
        st.markdown('<div class="section-header">📊 Simulation Results</div>', unsafe_allow_html=True)

        # 结果卡片（单列，只包含扭矩和判断）
        st.markdown('<div class="result-card">', unsafe_allow_html=True)

        # 使用两列显示两个扭矩值
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric(
                label="**Torque (N·m)**",
                value=f"{nm_result:.2f}"
            )
        with col_metric2:
            st.metric(
                label="**Torque (kg·cm)**",
                value=f"{torque_prediction:.2f}"
            )

        st.markdown(f"**Judgment:** <span class='{result_style}'>{judge}</span>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# 如果还没有运行过模拟，显示欢迎信息
if not submitted or not st.session_state.get('model_loaded', False):
    col_welcome1, col_welcome2, col_welcome3 = st.columns([1, 3, 1])
    with col_welcome2:
        st.markdown("""
        <div class="welcome-text" style='text-align: center; padding: 20px;'>
            <h3 style='color: #333333;'>Welcome to Digital Assembly Simulator</h3>
            <p style='color: #666666;'>Simulate and analyze assembly parameters for optimal performance.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📖 How to use", expanded=True):
            st.markdown("""
            1. **Load Models** - Click 'Load Models' in the sidebar
            2. **Enter Parameters** - Input values in the 12 parameter boxes above
            3. **Check Ranges** - Green indicator (✓) means value is within recommended range
            4. **Run Simulation** - Click the 'Run Simulation' button
            5. **View Results** - Analyze the torque prediction

            **Specifications:**
            - Target torque range: **2.35 - 2.75 N·m** (24 - 28 kg·cm)
            - All measurements in millimeters (mm)

            **Color Indicators:**
            - ✅ Green: Value within recommended range
            - ❌ Red: Value outside recommended range
            """)

    # 显示历史结果（如果有）
    if st.session_state.results:
        st.markdown('<div class="section-header">📈 Recent Simulations</div>', unsafe_allow_html=True)

        history_data = []
        for i, res in enumerate(st.session_state.results[-3:], 1):
            history_data.append({
                "#": f"#{len(st.session_state.results) - 3 + i}",
                "Time": res["timestamp"][11:19],
                "Torque": f"{res['torque']:.2f} N·m",
                "Result": res["judgment"]
            })

        if history_data:
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, hide_index=True, use_container_width=True)

# 紧凑页脚
st.markdown("---")
st.caption(
    "Digital Assembly Lab | For technical support, contact engineering department",
    help="Version 2.0 | Last updated: 2024"
)
