import streamlit as st
import openrouteservice
import folium
from streamlit_folium import st_folium

# Chave da API do OpenRouteService (substitua pelo seu token)
ORS_API_KEY = "5b3ce3597851110001cf624830e578a0cba545f8903cebb5c3ff74c5"

# Cliente ORS
client = openrouteservice.Client(key=ORS_API_KEY)

# Título do App
st.title("Simulador de Solicitações com Rotas Alternativas (ORS)")

# Função para tratar coordenadas (substitui vírgula por ponto)
def process_input(input_value):
    if isinstance(input_value, str):
        input_value = input_value.replace(",", ".")  # Substituir vírgula por ponto
    try:
        return float(input_value)
    except ValueError:
        return None

# Função para formatar o tempo em horas e minutos
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours} horas e {minutes} minutos"

# Input: Coordenadas de origem
lat1 = st.text_input("Latitude de origem (ex.: -22.577387):")
lon1 = st.text_input("Longitude de origem (ex.:  -48.786028):")

# Input: Coordenadas de destino
lat2 = st.text_input("Latitude de destino (ex.: -22.260652):")
lon2 = st.text_input("Longitude de destino (ex.: -49.527165):")

# Input: Velocidade média
avg_speed = st.number_input("Digite a velocidade média (km/h):", min_value=1.0, step=1.0)

# Converter inputs para float
lat1 = process_input(lat1)
lon1 = process_input(lon1)
lat2 = process_input(lat2)
lon2 = process_input(lon2)

if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
    try:
        # Solicitação à API do ORS com múltiplas rotas
        coords = [(lon1, lat1), (lon2, lat2)]  # Coordenadas no formato (lon, lat)
        route = client.directions(
            coordinates=coords,
            profile='driving-hgv',  # Perfil para veículos pesados (caminhões)
            format='geojson',
            alternative_routes={
                "target_count": 3,   # Solicitar até 3 rotas alternativas
                "share_factor": 0.6  # Define o percentual de sobreposição mínima com a rota principal
            }
        )

        # Exibir as rotas alternativas no mapa
        st.write("**Rotas Disponíveis:**")

        # Criar o mapa usando Folium
        map_center = [(lat1 + lat2) / 2, (lon1 + lon2) / 2]  # Centraliza entre os pontos
        m = folium.Map(location=map_center, zoom_start=10)

        # Adicionar pontos de origem e destino no mapa
        folium.Marker(location=[lat1, lon1], tooltip="Origem", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=[lat2, lon2], tooltip="Destino", icon=folium.Icon(color="red")).add_to(m)

        # Iterar pelas rotas e exibir informações
        for i, feature in enumerate(route['features']):
            # Extrair distância e tempo
            distance_km = feature['properties']['segments'][0]['distance'] / 1000  # Distância em km
            travel_time_seconds = feature['properties']['segments'][0]['duration']  # Tempo em segundos
            formatted_time = format_time(travel_time_seconds)  # Formatar tempo em horas e minutos

            # Exibir informações da rota
            st.write(f"**Rota {i+1}:**")
            st.write(f"- Distância: {distance_km:.2f} km")
            st.write(f"- Tempo Estimado: {formatted_time}")

            # Adicionar rota ao mapa
            folium.GeoJson(
                feature['geometry'],
                name=f"Rota {i+1}",
                tooltip=f"Rota {i+1} - {distance_km:.2f} km, {formatted_time}"
            ).add_to(m)

        # Exibir o mapa no Streamlit
        st_folium(m, width=800, height=500)
    except Exception as e:
        st.error(f"Erro ao calcular a rota ou exibir o mapa: {e}")
else:
    st.warning("Por favor, insira valores válidos para as coordenadas.")
