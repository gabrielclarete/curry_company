# Bibliotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

from streamlit_folium import folium_static
st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

# -----------------------------------------------
# Funções
# -----------------------------------------------

def country_maps (df1):
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                    .groupby(['City', 'Road_traffic_density'])
                    .median()
                    .reset_index())
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker ( [location_info['Delivery_location_latitude'],
                            location_info['Delivery_location_longitude']],
                            popup=location_info[['City', 'Road_traffic_density']]).add_to(map)          
    folium_static(map, width=1024, height=600)
        
def order_share_by_week (df1):
    df_aux01 = (df1.loc[:, ['ID', 'week_of_year']]
                    .groupby( 'week_of_year' )
                    .count()
                    .reset_index())
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                    .groupby('week_of_year')
                    .nunique()
                    .reset_index())

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def order_by_week (df1):
    #Criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime ( '%U' )
    df_aux = (df1.loc[:, ['ID','week_of_year']]
              .groupby('week_of_year')
              .count()
              .reset_index())
    fig = px.line( df_aux, x='week_of_year', y='ID')
    return fig

def traffic_order_city (df1):
    df_aux = ( df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                    .groupby (['City', 'Road_traffic_density'])
                    .count()
                    .reset_index() )
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def traffic_order_share (df1):
    df_aux = ( df1.loc [:,['ID', 'Road_traffic_density'] ]
                .groupby('Road_traffic_density')
                .count()
                .reset_index() )
    
    df_aux = df_aux.loc [df_aux['Road_traffic_density'] != "NaN", :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie (df_aux, values='entregas_perc', names='Road_traffic_density')
    return fig

def order_metric (df1):
    #Selecao de linhas
    df_aux = (df1.loc[:, ['ID', 'Order_Date']]
                .groupby('Order_Date')
                .count()
                .reset_index() )

    #Desenhar o gráfico de linhas
    fig = px.bar(df_aux,x='Order_Date', y='ID')
    return fig 

def clean_code (df1):
    """ Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NAN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de data
        5. Limpeza da coluna de tempo (remoção da variável numérica)
        
        Input: Dataframe
        Output: Dataframe """
    #Convertendo a coluna Delivery_person_Age de texto para número
    linhas_selecionadas = (df1 ['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1 ['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1 ['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1 ['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()


    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #Convertendo a coluna Delivery_person_Ratings para numero decimal (float)
    df1 ['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #Convertendo a coluna Order_Date de texto para data
    df1 ['Order_Date'] = pd.to_datetime ( df1 ['Order_Date'], format= '%d-%m-%Y')

    #Removendo a string 'NaN ' da coluna multiple_deliveries
    df1 = df1[df1['multiple_deliveries'] != 'NaN '].copy()

    #Removendo valor nulos da coluna multiple_deliveries
    df1 = df1.dropna(subset=['multiple_deliveries']).copy()

    #Convertendo a coluna multiple_deliveries para número inteiro
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #Removendo os ospaços dentro de strings
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc [:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    #Limpando a coluna  de time taken

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply (lambda x: x.split( '(min)' ) [1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

# -------------------------------------------  Início da Estrutura lógica do código -----------------------------------------
#--------------------------------------------
# Import dataset
df = pd.read_csv ('dataset/train.csv')
#--------------------------------------------
#--------------------------------------------
# Limpando os dados
df1 = clean_code(df)
#--------------------------------------------


#============================================
# Barra lateral
#============================================

st.header('Marketplace - Visão Cliente')
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=500)
st.sidebar.markdown("# Curry Company")
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider (
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low','Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('''
    **Developed by [Gabriel Clarete](https://www.linkedin.com/in/gabrielclarete/)**  
    <small>Built with Python & Streamlit</small>
    ''', unsafe_allow_html=True)

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc [linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1 ['Road_traffic_density'].isin (traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#============================================
# Layout
#============================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric( df1 )
        st.markdown('# Pedidos por Dia')
        st.plotly_chart(fig,use_container_width=True )
        
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            fig = traffic_order_share (df1)
            st.header("Pedidos por Condição de Trânsito")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("Pedidos por Cidade e Trânsito")
            fig = traffic_order_city (df1)
            st.plotly_chart(fig,use_container_width=True)
               
with tab2:
    with st.container():
        st.markdown ("# Pedidos por Semana")
        fig = order_by_week(df1)
        st.plotly_chart (fig, use_container_width=True)

    with st.container():
        st.markdown("# Distribuição de Pedidos por Semana")
        fig = order_share_by_week(df1)
        st.plotly_chart (fig, use_container_width=True)

with tab3:
    st.markdown("# Distribuição Geográfica de Pedidos")
    country_maps(df1)