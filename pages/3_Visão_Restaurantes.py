# Bibliotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st
from PIL import Image
import numpy as np
from streamlit_folium import folium_static
st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

# ============================================
# Funções de Limpeza
# ============================================

def limpar_dados(df):
    """Remove NaNs, converte tipos e limpa strings do DataFrame."""
    df1 = df.copy()

    # Remove linhas com 'NaN ' (string) em colunas críticas
    colunas_nan = ['Delivery_person_Age', 'Road_traffic_density', 'City', 'Festival']
    for col in colunas_nan:
        df1 = df1.loc[df1[col] != 'NaN ', :].copy()

    # Conversões de tipo
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Limpa coluna multiple_deliveries
    df1 = df1[df1['multiple_deliveries'] != 'NaN '].copy()
    df1 = df1.dropna(subset=['multiple_deliveries']).copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Remove espaços extras das strings
    colunas_strip = ['ID', 'Road_traffic_density', 'Type_of_vehicle', 'City', 'Festival']
    for col in colunas_strip:
        df1.loc[:, col] = df1.loc[:, col].str.strip()

    # Limpa coluna Time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1


# ============================================
# Funções de Cálculo
# ============================================

def calcular_distancia(df):
    """Calcula a distância haversine entre restaurante e entrega."""
    cols = [
        'Restaurant_latitude', 'Restaurant_longitude',
        'Delivery_location_latitude', 'Delivery_location_longitude'
    ]
    df['distance'] = df.loc[:, cols].apply(
        lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
        ), axis=1
    )
    return df


def calcular_tempo_por_festival(df, festival, metrica):
    """Retorna média ou std do tempo de entrega filtrado por festival (Yes/No)."""
    df_aux = (
        df.loc[:, ['Time_taken(min)', 'Festival']]
        .groupby('Festival')
        .agg({'Time_taken(min)': ['mean', 'std']})
    )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    return np.round(df_aux.loc[df_aux['Festival'] == festival, metrica].iloc[0], 2)


def calcular_tempo_por_cidade_trafego(df):
    """Retorna DataFrame com média e std do tempo por cidade e tráfego."""
    df_aux = (
        df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
        .groupby(['City', 'Road_traffic_density'])
        .agg({'Time_taken(min)': ['mean', 'std']})
    )
    df_aux.columns = ['avg_time', 'std_time']
    return df_aux.reset_index()


# ============================================
# Funções de Gráfico
# ============================================

def grafico_bar_tempo_por_cidade(df):
    """Gráfico de barras com média e desvio do tempo por cidade."""
    df_aux = (
        df.loc[:, ['City', 'Time_taken(min)']]
        .groupby('City')
        .agg({'Time_taken(min)': ['mean', 'std']})
    )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Control',
        x=df_aux['City'],
        y=df_aux['avg_time'],
        error_y=dict(type='data', array=df_aux['std_time'])
    ))
    return fig


def grafico_pizza_distancia_por_cidade(df):
    """Gráfico de pizza com distância média por cidade."""
    df = calcular_distancia(df)
    avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(
        labels=avg_distance['City'],
        values=avg_distance['distance'],
        pull=[0, 0.1, 0]
    )])
    return fig


def grafico_sunburst_tempo_por_cidade_trafego(df):
    """Gráfico sunburst de tempo médio por cidade e tráfego."""
    df_aux = calcular_tempo_por_cidade_trafego(df)
    fig = px.sunburst(
        df_aux,
        path=['City', 'Road_traffic_density'],
        values='avg_time',
        color='std_time',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=np.average(df_aux['std_time'])
    )
    return fig


# ============================================
# Funções de Layout
# ============================================

def render_sidebar(df1):
    """Renderiza a barra lateral e retorna o DataFrame filtrado."""
    image_path = 'logo.png'
    image = Image.open(image_path)
    st.sidebar.image(image, width=500)

    st.sidebar.markdown("# Cury Company")
    st.sidebar.markdown('## Fastest Delivery in Town')
    st.sidebar.markdown("""---""")

    st.sidebar.markdown('## Selecione uma data limite')
    date_slider = st.sidebar.slider(
        'Até qual valor?',
        value=datetime(2022, 4, 13),
        min_value=datetime(2022, 2, 11),
        max_value=datetime(2022, 4, 6),
        format='DD-MM-YYYY'
    )

    st.sidebar.markdown("""---""")
    traffic_options = st.sidebar.multiselect(
        'Quais as condições do trânsito',
        ['Low', 'Medium', 'High', 'Jam'],
        default=['Low', 'Medium', 'High', 'Jam']
    )

    st.sidebar.markdown("""---""")
    st.sidebar.markdown('''
    **Developed by [Gabriel Clarete](https://www.linkedin.com/in/gabrielclarete/)**  
    <small>Built with Python & Streamlit</small>
    ''', unsafe_allow_html=True)


    # Aplica filtros
    df1 = df1.loc[df1['Order_Date'] < date_slider, :]
    df1 = df1.loc[df1['Road_traffic_density'].isin(traffic_options), :]

    return df1


def render_metricas(df1):
    """Renderiza as 6 métricas principais."""
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        delivery_unique = len(df1['Delivery_person_ID'].unique())
        col1.metric('Entregadores', delivery_unique)

    with col2:
        df1 = calcular_distancia(df1)
        avg_distance = np.round(df1['distance'].mean(), 2)
        col2.metric('Distância média', avg_distance)

    with col3:
        col3.metric('Tempo Médio (Festival)', calcular_tempo_por_festival(df1, 'Yes', 'avg_time'))

    with col4:
        col4.metric('STD Entrega (Festival)', calcular_tempo_por_festival(df1, 'Yes', 'std_time'))

    with col5:
        col5.metric('Tempo Médio (Sem Festival)', calcular_tempo_por_festival(df1, 'No', 'avg_time'))

    with col6:
        col6.metric('STD Entrega (Sem Festival)', calcular_tempo_por_festival(df1, 'No', 'std_time'))


def render_tab_visao_gerencial(df1):
    """Renderiza toda a aba Visão Gerencial."""
    with st.container():
        st.title("Métricas Gerais")
        render_metricas(df1)

    with st.container():
        st.markdown("""---""")
        st.markdown("#### Tempo médio de entrega por cidade")
        st.plotly_chart(grafico_bar_tempo_por_cidade(df1))

    with st.container():
        st.markdown("""---""")
        st.markdown("#### Distribuição do tempo")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(grafico_pizza_distancia_por_cidade(df1))
        with col2:
            st.plotly_chart(grafico_sunburst_tempo_por_cidade_trafego(df1))

    with st.container():
        st.markdown("""---""")
        st.markdown("#### Distribuição da Distância")
        df_aux = calcular_tempo_por_cidade_trafego(df1)
        st.dataframe(df_aux)


# ============================================
# Main
# ============================================

def main():
    st.header('Marketplace - Visão Restaurantes')

    df = pd.read_csv('dataset/train.csv')
    df1 = limpar_dados(df)
    df1 = render_sidebar(df1)

    tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

    with tab1:
        render_tab_visao_gerencial(df1)


if __name__ == '__main__':
    main()