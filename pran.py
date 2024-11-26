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


# Função para encontrar o ponto roteável mais próximo
def find_nearest_road(client, latitude, longitude):
    try:
        nearest = client.places(
            coordinates=[longitude, latitude],
            request="nearest"
        )
        return nearest['features'][0]['geometry']['coordinates'][::-1]  # Retorna [lat, lon]
    except Exception as e:
        return None

# Função para formatar o tempo em horas e minutos
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours} horas e {minutes} minutos"

# Entrada de coordenadas
lat1 = st.text_input("Latitude de origem (ex.: -23.55052):")
lon1 = st.text_input("Longitude de origem (ex.: -46.633308):")
lat2 = st.text_input("Latitude de destino (ex.: -22.906847):")
lon2 = st.text_input("Longitude de destino (ex.: -43.172896):")

if lat1 and lon1 and lat2 and lon2:
    try:
        lat1, lon1 = float(lat1), float(lon1)
        lat2, lon2 = float(lat2), float(lon2)

        # Encontrar pontos roteáveis mais próximos
        start = find_nearest_road(client, lat1, lon1) or [lat1, lon1]
        end = find_nearest_road(client, lat2, lon2) or [lat2, lon2]

        # Chamada à API para calcular a rota
        route = client.directions(
            coordinates=[start[::-1], end[::-1]],
            profile='driving-car',
            format='geojson',
            radiuses=[1000, 1000]
        )

        # Extrair informações da rota
        distance_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000
        duration_seconds = route['features'][0]['properties']['segments'][0]['duration']
        formatted_time = format_time(duration_seconds)

        # Exibir informações da rota
        st.write(f"**Distância Total:** {distance_km:.2f} km")
        st.write(f"**Tempo Total Estimado:** {formatted_time}")

        # Exibir o mapa
        m = folium.Map(location=start, zoom_start=8)
        folium.Marker(location=start, tooltip="Origem", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=end, tooltip="Destino", icon=folium.Icon(color="red")).add_to(m)
        folium.GeoJson(route['features'][0]['geometry']).add_to(m)
        st_folium(m, width=800, height=500)
    except Exception as e:
        st.error(f"Erro ao calcular a rota ou exibir o mapa: {e}")
else:
    st.warning("Insira coordenadas válidas para origem e destino.")
