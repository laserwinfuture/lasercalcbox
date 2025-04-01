import math
import numpy as np
import streamlit as st
import sys
import os
import ast
import openai
from streamlit_elements import elements, mui, html
import base64
import datetime
import io

# mylib
from mylib import lensTransfer


# 加密用户信息的读取
# 使用ast.literal_eval安全地转换为字典
USER_AUTH        = ast.literal_eval(st.secrets["USER_AUTH"])
API_ENDPOINTS    = ast.literal_eval(st.secrets["API_ENDPOINTS"])
AVAILABLE_MODELS = ast.literal_eval(st.secrets["AVAILABLE_MODELS"])
PREDEFINED_ROLES = ast.literal_eval(st.secrets["PREDEFINED_ROLES"])


APP_TITTLE = '激光计算工具箱V0.3'

# 验证用户并获取API密钥
def verify_user(username):
    """
    验证用户并返回对应的API密钥
    
    Args:
        username (str): 用户名
        
    Returns:
        tuple: (是否验证通过, API密钥)
    """
    if username in USER_AUTH:
        return True, USER_AUTH[username]
    return False, None




# 设置页面配置
st.set_page_config(
    page_title='Laser Calc Box',
    page_icon='logo/ICO.ico',
    layout='centered'
)

# 加载自定义CSS样式
st.markdown("""
    <style>
    .stHorizontalBlock > div {
        flex-shrink: 0;
        min-width: auto !important;
    }
    div[data-testid="stFormSubmitButton"] > button {
        width: auto;
    }
    div.row-widget.stNumberInput > div {
        display: inline-flex !important;
        align-items: center !important;
        width: 100% !important;
    }
    div.row-widget.stNumberInput > div > label {
        margin: 0 !important;
        min-width: 120px !important;
        padding-right: 10px !important;
        white-space: nowrap !important;
        flex: 0 0 auto !important;
    }
    div.row-widget.stNumberInput > div > div {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: row;
    }
    .chat-message.user {
        background-color: #2b313e;
    }
    .chat-message.assistant {
        background-color: #475063;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .message {
        width: 80%;
    }
    .settings-container {
        background-color: #1e2130;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .settings-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .settings-panel {
        background-color: #2c3141;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        transition: max-height 0.3s ease-out;
    }
    .stButton>button {
        width: 100%;
    }
    .chat-sidebar {
        padding: 1rem;
        background-color: #1e2130;
        border-radius: 0.5rem;
        min-width: 300px;
    }
    .chat-container {
        max-width: 100%;
        margin: 0 auto;
    }
    .wide-layout {
        max-width: 1400px !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin: 0 auto !important;
    }
    /* LaTeX样式 */
    .math-content {
        margin: 1em 0;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 0.5em 0;
    }
    .katex { 
        font-size: 1.1em !important;
        text-align: left !important;
    }
    .katex-display {
        overflow: auto hidden;
        padding: 0.2em 0;
        margin: 0.5em 0;
    }
    </style>
    """, unsafe_allow_html=True)


# 使用streamlit_elements渲染LaTeX公式
def render_math(content):
    """渲染带有LaTeX公式的内容"""
    with elements("latex_renderer"):
        with mui.Box(sx={"width": "100%"}):
            html.Div(content, dangerouslySetInnerHTML={"__html": f"""
            <div class="latex-content">{content}</div>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <script>
            MathJax = {{
                tex: {{
                    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
                }},
                svg: {{
                    fontCache: 'global'
                }}
            }};
            </script>
            """})

def update_energy_state(value, unit):
    # 使用session_state中的实际输入值
    value = st.session_state[f'energy_input_{unit}']
    # 根据单位转换为基本单位(J)
    if unit == 'nJ':
        st.session_state.energy = value * 1e-9
    elif unit == 'μJ':
        st.session_state.energy = value * 1e-6
    else:  # mJ
        st.session_state.energy = value * 1e-3
    # 更新功率
    st.session_state.power = st.session_state.energy * st.session_state.PRF

def update_power_state(value, unit):
    # 使用session_state中的实际输入值
    value = st.session_state[f'power_input_{unit}']
    # 根据单位转换为基本单位(W)
    st.session_state.power = value * (0.001 if unit == 'mW' else 1)
    # 更新能量
    st.session_state.energy = st.session_state.power / st.session_state.PRF

def get_chatgpt_response(prompt, api_key, base_url=None, model="gpt-3.5-turbo", system_role="你是一个专业的激光技术顾问，可以回答用户关于激光技术方面的问题。", temperature=0.7, top_p=1.0, max_tokens=1000, presence_penalty=0, frequency_penalty=0, conversation_history=None):
    try:
        if base_url:
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = openai.OpenAI(api_key=api_key)
        
        # 构建消息历史
        messages = [{"role": "system", "content": system_role}]
        
        # 如果有对话历史，添加到消息中
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前用户提问
        messages.append({"role": "user", "content": prompt})
            
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty
        )
    
        # 获取回复内容
        content = response.choices[0].message.content
        
        # 更新token计数
        if 'total_tokens' not in st.session_state:
            st.session_state.total_tokens = 0
        
        # 如果响应对象中包含usage信息，添加到累计值
        if hasattr(response, 'usage') and response.usage is not None:
            if hasattr(response.usage, 'total_tokens'):
                st.session_state.total_tokens += response.usage.total_tokens
   
        # 检查是否包含思维链内容
        if '/think' in content:
            think_content = content.split('/think')[1].strip()  # 获取思维链内容
            answer_content = content.split('/think')[0].strip()  # 获取回答内容
            return think_content, answer_content  # 返回思维链和回答内容
        else:
            return None, content  # 如果没有思维链内容，返回None和回答内容
    
    except Exception as e:
        return f"发生错误: {str(e)}"

def update_role():
    # 清空聊天记录
    st.session_state.chat_messages = []
    # 更新角色定义
    st.session_state.system_role = st.session_state.role_input

def clear_chat():
    # 清空聊天记录
    st.session_state.chat_messages = []

def get_markdown_download_link(markdown_content, filename="聊天记录.md"):
    """生成Markdown下载链接"""
    b64 = base64.b64encode(markdown_content.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}">下载 Markdown 文件</a>'
    return href

def format_chat_to_markdown(chat_messages):
    """将聊天记录格式化为Markdown"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markdown = f"# 激光计算工具箱聊天记录\n\n导出时间: {current_time}\n\n"
    
    for message in chat_messages:
        role = "用户" if message["role"] == "user" else "AI助手"
        content = message["content"]
        markdown += f"## {role}\n\n{content}\n\n"
    
    return markdown

# 初始化session state
if 'page' not in st.session_state:
    st.session_state.page = '激光功率/能量/能量密度等换算'  # 默认页面
if 'PRF' not in st.session_state:
    st.session_state.PRF = 1000  # 默认1kHz
if 'PW' not in st.session_state:
    st.session_state.PW = 1e-9   # 默认1ns
if 'diameter' not in st.session_state:
    st.session_state.diameter = 0.1  # 默认1mm -> 0.1cm
if 'damage' not in st.session_state:
    st.session_state.damage = 1.0  # 默认1 J/cm^2@10ns
if 'energy' not in st.session_state:
    st.session_state.energy = 1e-3  # 默认1mJ
if 'power' not in st.session_state:
    st.session_state.power = st.session_state.energy * st.session_state.PRF
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""
if 'system_role' not in st.session_state:
    st.session_state.system_role = "你是一个专业的激光技术顾问，可以回答用户关于激光技术方面的问题。请用标准的语法描述公式：1）行内用$符号进行包裹，2）行间公式用$$ 进行包裹"
if 'base_url' not in st.session_state:
    st.session_state.base_url = None
if 'model' not in st.session_state:
    #st.session_state.model = "gpt-4o-mini"
    # 默认模型：chatgpt-4o-latest
    st.session_state.model = "chatgpt-4o-latest"
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7
if 'top_p' not in st.session_state:
    st.session_state.top_p = 1.0
if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 4000
if 'presence_penalty' not in st.session_state:
    st.session_state.presence_penalty = 0.0
if 'frequency_penalty' not in st.session_state:
    st.session_state.frequency_penalty = 0.0
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'is_verified' not in st.session_state:
    st.session_state.is_verified = False
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False
if 'export_format' not in st.session_state:
    st.session_state.export_format = 'markdown'
if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0

# 创建侧边栏导航
st.sidebar.subheader(f'{APP_TITTLE}')
laser_power_button  = st.sidebar.button('激光功率/能量/能量密度等换算')
beam_quality_button = st.sidebar.button('M2及高斯光束传输与聚焦')
ai_chat_button      = st.sidebar.button('AI激光顾问')

# 添加空白占位，将文字推到底部
st.sidebar.markdown('---')
for _ in range(25):
    st.sidebar.write('')

# 在底部添加文字
st.sidebar.markdown('by Dr.shi  \n8582864@qq.com')

if laser_power_button:
    st.session_state.page = '激光功率/能量/能量密度等换算'
elif beam_quality_button:
    st.session_state.page = 'M2及高斯光束传输与聚焦'
elif ai_chat_button:
    st.session_state.page = 'AI激光顾问'

if st.session_state.page == '激光功率/能量/能量密度等换算':
    st.subheader('基本参数设置')
    
    # PRF设置
    col_prf1, col_prf2 = st.columns([3, 1])
    with col_prf1:
        prf_value = st.number_input('重复频率', value=1.0, format='%f')
    with col_prf2:
        prf_unit = st.selectbox('脉冲频率单位', ['Hz', 'kHz', 'MHz'], index=1,  label_visibility='hidden')
    
    if prf_unit == 'Hz':
        st.session_state.PRF = prf_value
    elif prf_unit == 'kHz':
        st.session_state.PRF = prf_value * 1e3
    else:  # MHz
        st.session_state.PRF = prf_value * 1e6
        

    # 脉冲宽度设置
    col_pw1, col_pw2 = st.columns([3, 1])
    with col_pw1:
        pw_value = st.number_input('脉冲宽度', value=1.0, step=1.0, format='%f')
    with col_pw2:
        pw_unit = st.selectbox('脉冲宽度单位', ['ps', 'ns', 'us'], index=1,  label_visibility='hidden')
    
    if pw_unit == 'ps':
        st.session_state.PW = pw_value * 1e-12
    elif pw_unit == 'ns':
        st.session_state.PW = pw_value * 1e-9
    else:  # us
        st.session_state.PW = pw_value * 1e-6
        
    # 光斑直径设置
    st.session_state.diameter = st.number_input('光斑直径(mm)', value=1.0) * 0.1  # 转换为cm
    
    # 损伤阈值设置
    st.session_state.damage = st.number_input('损伤阈值(J/cm²@10ns)', value=5.0)
    
    st.subheader('能量/功率(任输其一)')
    
    # 能量设置
    col_e1, col_e2 = st.columns([3, 1])
    with col_e2:
        energy_unit = st.selectbox('  ', ['nJ', 'μJ', 'mJ'], index=2)
    with col_e1:
        # 根据当前能量和单位计算显示值
        if energy_unit == 'nJ':
            display_energy = st.session_state.energy * 1e9
        elif energy_unit == 'μJ':
            display_energy = st.session_state.energy * 1e6
        else:  # mJ
            display_energy = st.session_state.energy * 1e3
        
        energy_value = st.number_input(
            '能量',
            value=display_energy,
            format='%f',
            key=f'energy_input_{energy_unit}',
            on_change=update_energy_state,
            args=(None, energy_unit)
        )
    
    # 功率显示
    col_p1, col_p2 = st.columns([3, 1])
    with col_p2:
        power_unit = st.selectbox('平均功率单位', ['W', 'mW'], index=0,  label_visibility='hidden')
    with col_p1:
        # 根据单位显示功率值
        display_power = st.session_state.power * (1000 if power_unit == 'mW' else 1)
        
        power_value = st.number_input(
            '功率',
            value=display_power,
            format='%f',
            key=f'power_input_{power_unit}',
            on_change=update_power_state,
            args=(None, power_unit)
        )
        
        # 根据单位更新功率值
        st.session_state.power = power_value * (0.001 if power_unit == 'mW' else 1)
        # 更新能量值
        st.session_state.energy = st.session_state.power / st.session_state.PRF
    
    # 计算结果显示
    st.subheader('计算结果')
    
    # 光斑面积
    area = math.pi * (st.session_state.diameter / 2) ** 2
    st.write(f'光斑面积: {area:.4f} cm²')
    
    # 平均功率密度
    avg_power_density = st.session_state.power / area
    st.write(f'平均功率密度: {avg_power_density:.2f} W/cm² = {avg_power_density*0.001:.2f} kW/cm²')
    
    # 峰值功率
    peak_power = st.session_state.energy / st.session_state.PW
    st.write(f'峰值功率: {peak_power*1e-3:.2f} kW = {peak_power*1e-6:.2f} MW = {peak_power*1e-9:.2f} GW')
    
    # 能量密度
    energy_density = st.session_state.energy / area
    st.write(f'能量密度: {energy_density*1e6:.2f} μJ/cm² = {energy_density*1e3:.2f} mJ/cm² = {energy_density:.2f} J/cm²')
    
    # 峰值功率密度
    peak_power_density = peak_power / area
    st.write(f'峰值功率密度: {peak_power_density*1e-3:.2f} kW/cm² = {peak_power_density*1e-6:.2f} MW/cm² = {peak_power_density*1e-9:.2f} GW/cm²')
    
    # 脉宽系数
    pw_factor = math.sqrt(10 / (st.session_state.PW * 1e9))
    st.write(f'脉宽系数(相对于10ns): {pw_factor:.4f}')
    
    # 损伤阈值
    damage_threshold = st.session_state.damage / pw_factor
    st.write(f'损伤阈值(考虑脉宽): {damage_threshold:.2f} J/cm²')
    
    # 能量密度与损伤阈值比较的颜色显示
    if energy_density <= damage_threshold * 0.5:
        st.success(f'能量密度在安全范围内 ({energy_density/damage_threshold*100:.1f}% 损伤阈值)')
    elif energy_density <= damage_threshold * 0.7:
        st.warning(f'能量密度接近警戒值 ({energy_density/damage_threshold*100:.1f}% 损伤阈值)')
    elif energy_density <= damage_threshold:
        st.warning(f'能量密度处于危险区域 ({energy_density/damage_threshold*100:.1f}% 损伤阈值)', icon='⚠️')
    else:
        st.error(f'能量密度超过损伤阈值 ({energy_density/damage_threshold*100:.1f}% 损伤阈值)')

elif st.session_state.page == 'M2及高斯光束传输与聚焦':
    st.subheader('M2及高斯光束传输')
    # 基本参数输入
    wavelength = st.number_input('波长(nm)', value=1064)
    waist_diameter = st.number_input('束腰直径(mm)', value=1.0)
    divergence = st.number_input('发散角(mrad)', value=1.36)
    location = st.number_input('传输距离(mm)', value=100.0)
    
    # M2计算
    M2 = math.pi * waist_diameter * divergence / (4 * wavelength * 1e-3)
    ZR = math.pi * (waist_diameter / 2) ** 2 / (wavelength * 1e-6) / M2
    beam_diameter = waist_diameter * math.sqrt((location / ZR) ** 2 + 1)
    
    st.write(f'M² = {M2:.4f}')
    st.write(f'瑞利长度 = {ZR:.2f} mm')
    st.write(f'传输距离处光斑直径 = {beam_diameter:.2f} mm')
    

    # 透镜变换计算
    st.subheader('透镜聚焦')
    distance_to_lens = st.number_input('束腰到透镜距离(mm)', value=100.0)
    focal_length = st.number_input('透镜焦距(mm)', value=100.0)
    
    # 计算透镜变换后的参数
    wavelength_mm = wavelength * 1e-6  # 转换为mm
    M2_after, d0_after, theta0_after, z0_after, zr_after = lensTransfer.solve(
        M2, waist_diameter, distance_to_lens, ZR, wavelength_mm, focal_length
    )
    
    # 添加空行
    #st.markdown("#") 
    st.write(f'束腰直径 = {d0_after:.2f} mm')
    st.write(f'束腰位置 = {z0_after:.2f} mm')
    st.write(f'发散角 = {theta0_after*1000:.2f} mrad')
    st.write(f'瑞利长度 = {zr_after*0.001:.2f} mm')

elif st.session_state.page == 'AI激光顾问':
    # 应用宽布局样式
    st.markdown('<style>.block-container{max-width: 1400px; padding-left: 1rem; padding-right: 1rem;}</style>', unsafe_allow_html=True)
    
    # 注入MathJax脚本以支持LaTeX公式渲染
    mathjax_script = """
    <script>
    // 检查是否已经加载
    if (typeof window.MathJax === 'undefined') {
        // 加载MathJax配置
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true,
                processEnvironments: true
            },
            svg: {
                fontCache: 'global'
            },
            skipStartupTypeset: false,
            startup: {
                pageReady() {
                    return MathJax.startup.defaultPageReady().then(function () {
                        console.log('MathJax初始化完成');
                    });
                }
            }
        };
        
        // 动态创建并加载脚本
        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
        script.async = true;
        document.head.appendChild(script);
    } else {
        // 如果已加载，尝试重新渲染页面中的数学公式
        if (typeof window.MathJax.typeset === 'function') {
            setTimeout(function() {
                window.MathJax.typeset();
            }, 500);
        }
    }
    </script>
    """
    
    st.markdown(mathjax_script, unsafe_allow_html=True)
    
    st.subheader('AI助手')
    
    # 用户登录区域
    if not st.session_state.is_verified:
        login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
        with login_col2:
            st.info("请输入您的用户名以使用AI聊天功能(可以输入test777,进行测试)")
            username = st.text_input("用户名")
            if st.button("验证用户"):
                if username:
                    is_verified, api_key = verify_user(username)
                    if is_verified:
                        st.session_state.is_verified = True
                        st.session_state.username = username
                        st.session_state.openai_api_key = api_key
                        st.success(f"欢迎, {username}! 验证成功。")
                        st.rerun()
                    else:
                        st.error("未找到该用户，请联系管理员注册。")
                else:
                    st.warning("请输入用户名")
    else:
        # 处理LaTeX公式的函数
        def process_markdown_with_latex(text):
            """将文本中的LaTeX公式标记为HTML以便MathJax处理"""
            # 创建HTML内容，注意添加了触发MathJax重新处理的脚本
            html_content = f"""
            <div class="math-content">
                {text}
            </div>
            <script>
                if (typeof window.MathJax !== 'undefined' && typeof window.MathJax.typeset === 'function') {{
                    try {{
                        window.MathJax.typeset();
                    }} catch (e) {{
                        console.error("MathJax渲染错误:", e);
                    }}
                }}
            </script>
            """
            return html_content
            
        # 显示用户信息和token统计
        user_col1, user_col2 = st.columns([3, 2])
        with user_col1:
            st.write(f"当前用户: **{st.session_state.username}**")
        with user_col2:
            token_count = st.session_state.total_tokens
            st.write(f"当前会话Token统计: **{token_count:,}**")
        
        # 创建聊天和设置的选项卡
        chat_tab, settings_tab = st.tabs(["聊天", "设置"])
        
        # 聊天界面选项卡
        with chat_tab:
            # 聊天区域 - 占据主要空间
            # 显示聊天历史
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    # 如果不包含数学公式，直接使用markdown
                    if '$' not in message["content"] and '\\(' not in message["content"]:
                        st.markdown(message["content"])
                    else:
                        # 对含有数学公式的内容使用特殊处理
                        processed_content = process_markdown_with_latex(message["content"])
                        st.markdown(processed_content, unsafe_allow_html=True)
            
            # 用户输入
            user_input = st.chat_input("请输入您的问题")
            if user_input:
                # 添加用户消息到历史记录
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    # 如果不包含数学公式，直接使用markdown
                    if '$' not in user_input and '\\(' not in user_input:
                        st.markdown(user_input)
                    else:
                        # 对含有数学公式的内容使用特殊处理
                        processed_input = process_markdown_with_latex(user_input)
                        st.markdown(processed_input, unsafe_allow_html=True)
                
                # 准备对话历史记录
                conversation_history = []
                for msg in st.session_state.chat_messages[:-1]:  # 不包括最新的用户消息
                    conversation_history.append({"role": msg["role"], "content": msg["content"]})
                
                # 获取AI回复
                with st.spinner("AI思考中..."):
                    think_response, ai_response = get_chatgpt_response(
                        prompt=user_input, 
                        api_key=st.session_state.openai_api_key,
                        base_url=st.session_state.base_url,
                        model=st.session_state.model,
                        system_role=st.session_state.system_role,
                        temperature=st.session_state.temperature,
                        top_p=st.session_state.top_p,
                        max_tokens=st.session_state.max_tokens,
                        presence_penalty=st.session_state.presence_penalty,
                        frequency_penalty=st.session_state.frequency_penalty,
                        conversation_history=conversation_history
                    )
                
                # 添加AI消息到历史记录
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant"):
                    # 如果有思维链内容，先展示思维链内容
                    if think_response:
                        st.markdown(f"**思维链内容:** {think_response}")

                    # 展示AI的回答内容
                    # 如果不包含数学公式，直接使用markdown
                    if '$' not in ai_response and '\\(' not in ai_response:
                        st.markdown(ai_response)
                    else:
                        # 对含有数学公式的内容使用特殊处理
                        processed_response = process_markdown_with_latex(ai_response)
                        st.markdown(processed_response, unsafe_allow_html=True)
        
        # 设置选项卡
        with settings_tab:
            # 基本设置部分
            st.subheader("模型设置")
            
            # 设置面板区域1 - 模型和API
            col1, col2 = st.columns(2)
            
            with col1:
                # 模型选择
                st.selectbox("选择模型", AVAILABLE_MODELS, 
                           index=AVAILABLE_MODELS.index(st.session_state.model) if st.session_state.model in AVAILABLE_MODELS else 0,
                           key="model_select",
                           on_change=lambda: setattr(st.session_state, 'model', st.session_state.model_select))
            
            with col2:
                # API线路选择
                endpoint_names = list(API_ENDPOINTS.keys())
                selected_endpoint = st.selectbox(
                    "选择API线路", 
                    endpoint_names,
                    index=0,
                    key="endpoint_select"
                )
                # 更新baseurl
                st.session_state.base_url = API_ENDPOINTS[selected_endpoint]
            
            # 设置面板区域2 - 角色预设
            st.subheader("角色设置")
            
            # 预设角色选择
            role_names = list(PREDEFINED_ROLES.keys())
            role_names.append("自定义")  # 将"自定义"添加到列表末尾而不是开头
            selected_role = st.selectbox(
                "选择角色预设", 
                role_names,
                index=0,  # 默认选择第一个预设角色
                key="role_preset"
            )
            
            # 根据选择展示角色定义
            if selected_role == "自定义":
                custom_role = st.text_area(
                    "自定义角色定义", 
                    value=st.session_state.system_role,
                    key="custom_role_input"
                )
                if st.button("应用自定义角色"):
                    st.session_state.system_role = custom_role
                    st.success("已应用自定义角色")
            else:
                # 应用预设角色
                if st.button(f"应用'{selected_role}'角色"):
                    st.session_state.system_role = PREDEFINED_ROLES[selected_role]
                    st.success(f"已应用'{selected_role}'角色预设")
            
            # 设置面板区域3 - 高级设置
            st.subheader("高级设置")
            adv_col1, adv_col2, adv_col3, adv_col4, adv_col5 = st.columns(5)
            
            with adv_col1:
                st.slider("随机性", 0.0, 2.0, st.session_state.temperature, 0.1, 
                        key="temp_slider", 
                        on_change=lambda: setattr(st.session_state, 'temperature', st.session_state.temp_slider))
                
            with adv_col2:
                st.slider("核采样", 0.1, 1.0, st.session_state.top_p, 0.1,
                        key="top_p_slider",
                        on_change=lambda: setattr(st.session_state, 'top_p', st.session_state.top_p_slider))    

            with adv_col3:
                st.slider("话题新鲜度", -2.0, 2.0, st.session_state.presence_penalty, 0.1,
                        key="presence_slider",
                        on_change=lambda: setattr(st.session_state, 'presence_penalty', st.session_state.presence_slider))
            
            with adv_col4:
                st.slider("频率惩罚度", -2.0, 2.0, st.session_state.frequency_penalty, 0.1,
                        key="freq_slider",
                        on_change=lambda: setattr(st.session_state, 'frequency_penalty', st.session_state.freq_slider))

            with adv_col5:
                st.number_input("回复长度限制", 100, 4000, st.session_state.max_tokens, 100,
                            key="max_tokens_input",
                            on_change=lambda: setattr(st.session_state, 'max_tokens', st.session_state.max_tokens_input))
                
    
            # 设置面板区域4 - 工具按钮
            st.subheader("聊天工具")
            tool_col1, tool_col2, tool_col3 = st.columns(3)
            
            with tool_col1:
                # 导出聊天记录
                if st.button("导出聊天记录", use_container_width=True) and st.session_state.chat_messages:
                    # 生成文件名
                    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    # 导出为Markdown
                    markdown_content = format_chat_to_markdown(st.session_state.chat_messages)
                    filename = f"聊天记录_{current_time}.md"
                    download_link = get_markdown_download_link(markdown_content, filename)
                    st.markdown(download_link, unsafe_allow_html=True)
            
            with tool_col2:
                # 清空聊天按钮
                if st.button("清空聊天记录", use_container_width=True):
                    clear_chat()
                    st.success("聊天记录已清空")
            
            with tool_col3:
                # 退出登录按钮
                if st.button("退出登录", use_container_width=True):
                    st.session_state.is_verified = False
                    st.session_state.username = ""
                    st.rerun()