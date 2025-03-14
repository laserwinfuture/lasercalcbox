import math
import numpy as np
import streamlit as st
import sys

sys.path.append("./lib_")  
import lensTransfer

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
    </style>
    """, unsafe_allow_html=True)


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


# 初始化session state
if 'page' not in st.session_state:
    st.session_state.page = '激光功率计算'  # 默认页面
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

# 创建侧边栏导航
st.sidebar.subheader('激光计算工具箱V0.1')
laser_power_button = st.sidebar.button('激光功率计算')
beam_quality_button = st.sidebar.button('光束质量计算')

# 添加空白占位，将文字推到底部
st.sidebar.markdown('---')
for _ in range(20):
    st.sidebar.write('')

# 在底部添加文字
st.sidebar.markdown('by Dr.shi  \n 13810392543')

if laser_power_button:
    st.session_state.page = '激光功率计算'
elif beam_quality_button:
    st.session_state.page = '光束质量计算'

if st.session_state.page == '激光功率计算':
    st.subheader('基本参数设置')
    
    # PRF设置
    col_prf1, col_prf2 = st.columns([3, 1])
    with col_prf1:
        prf_value = st.number_input('重复频率', value=1.0, format='%f')
    with col_prf2:
        prf_unit = st.selectbox('', ['Hz', 'kHz', 'MHz'], index=1)
    
    if prf_unit == 'Hz':
        st.session_state.PRF = prf_value
    elif prf_unit == 'kHz':
        st.session_state.PRF = prf_value * 1e3
    else:  # MHz
        st.session_state.PRF = prf_value * 1e6
        

    # 脉冲宽度设置
    col_pw1, col_pw2 = st.columns([3, 1])
    with col_pw1:
        pw_value = st.number_input('脉冲宽度', value=1.0, format='%f')
    with col_pw2:
        pw_unit = st.selectbox(' ', ['ps', 'ns', 'us'], index=1)
    
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
        power_unit = st.selectbox('   ', ['W', 'mW'], index=0)
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

elif st.session_state.page == '光束质量计算':
    st.subheader('光束质量计算')
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