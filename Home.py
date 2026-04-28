import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲",
    layout='wide'
)

#image_path = 'C:/Users/gabri/repos/ftc_programacao_python'
image = Image.open('logo.png')
st.sidebar.image(image, width=500)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company | Growth Analytics")
st.sidebar.markdown('''
    **Developed by [Gabriel Clarete](https://www.linkedin.com/in/gabrielclarete/)**  
    <small>Built with Python & Streamlit</small>
    ''', unsafe_allow_html=True)


st.markdown("""
Growth Dashboard desenvolvido para acompanhar as métricas de crescimento
de entregadores e restaurantes.

### Como utilizar este dashboard?

**🏢 Visão Empresa**
- **Visão Gerencial:** métricas gerais de desempenho
- **Visão Tática:** indicadores semanais de crescimento
- **Visão Geográfica:** insights baseados em localização

**🚴 Visão Entregadores**
- Acompanhamento de indicadores semanais de crescimento

**🍽️ Visão Restaurantes**
- Indicadores semanais de crescimento dos restaurantes
""")