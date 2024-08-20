import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Obtener los datos de la API
url = "https://api.covidtracking.com/v1/states/daily.json"
response = requests.get(url)
data = response.json()

# Convertir a DataFrame
df = pd.DataFrame(data)

# Convertir la fecha a formato datetime
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

# Agregar columnas para mes y año
df['month'] = df['date'].dt.to_period('M')

# Cargar el diccionario de estados
states_dict = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Reemplazar abreviaturas por nombres completos de estados
df['state'] = df['state'].map(states_dict)

# Agrupar por estado y mes, y calcular la suma de muertes y casos
monthly_data = df.groupby(['state', 'month']).agg({
    'deathIncrease': 'sum',
    'positiveIncrease': 'sum'
}).reset_index()

# Crear el gráfico
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=('Muertes por COVID-19', 'Casos de COVID-19'))

for state in monthly_data['state'].unique():
    state_data = monthly_data[monthly_data['state'] == state]

    # Gráfico de muertes
    fig.add_trace(
        go.Scatter(x=state_data['month'].astype(str), y=state_data['deathIncrease'],
                   name=state, mode='lines', showlegend=False),
        row=1, col=1
    )

    # Gráfico de casos
    fig.add_trace(
        go.Scatter(x=state_data['month'].astype(str), y=state_data['positiveIncrease'],
                   name=state, mode='lines'),
        row=2, col=1
    )

fig.update_layout(height=800, title_text="Muertes y Casos de COVID-19 por Estado y Mes",
                  hovermode="x unified")
fig.update_xaxes(title_text="Mes", row=2, col=1)
fig.update_yaxes(title_text="Número de Muertes", row=1, col=1)
fig.update_yaxes(title_text="Número de Casos", row=2, col=1)

fig.show()

# Imprimir un resumen de los datos
print("Resumen de datos por estado:")
for state in monthly_data['state'].unique():
    state_data = monthly_data[monthly_data['state'] == state]
    total_deaths = state_data['deathIncrease'].sum()
    total_cases = state_data['positiveIncrease'].sum()
    peak_death_month = state_data.loc[state_data['deathIncrease'].idxmax(), 'month']
    peak_case_month = state_data.loc[state_data['positiveIncrease'].idxmax(), 'month']

    print(f"\n{state}:")
    print(f"  Total de muertes: {total_deaths}")
    print(f"  Total de casos: {total_cases}")
    print(f"  Mes con más muertes: {peak_death_month}")
    print(f"  Mes con más casos: {peak_case_month}")
    