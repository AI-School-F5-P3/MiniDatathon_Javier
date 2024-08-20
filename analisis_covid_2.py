import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

# Obtener los datos de la API
url = "https://api.covidtracking.com/v1/states/daily.json"
response = requests.get(url)
data = response.json()

# Convertir a DataFrame
df = pd.DataFrame(data)

# Convertir la fecha a formato datetime
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

# Agregar columnas para mes y año
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

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

# Agrupar por estado, año y mes, y calcular la suma de muertes
monthly_deaths = df.groupby(['state', 'year', 'month'])['deathIncrease'].sum().reset_index()

# Encontrar el mes con más muertes para cada estado
max_deaths_by_state = monthly_deaths.loc[monthly_deaths.groupby('state')['deathIncrease'].idxmax()]

# Ordenar los estados por número total de muertes
state_total_deaths = df.groupby('state')['deathIncrease'].sum().sort_values(ascending=False)

# 1. Gráfico de barras para los 10 estados con más muertes (Matplotlib)
plt.figure(figsize=(12, 6))
top_10_states = state_total_deaths.head(10)
plt.bar(top_10_states.index, top_10_states.values)
plt.title('Top 10 Estados con Mayor Número de Muertes por COVID-19')
plt.xlabel('Estado')
plt.ylabel('Número Total de Muertes')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Mapa de calor de muertes mensuales para los 10 estados más afectados (Seaborn)
top_10_states = state_total_deaths.head(10).index
top_10_monthly_deaths = monthly_deaths[monthly_deaths['state'].isin(top_10_states)]

# Crear una columna combinada de año y mes para evitar duplicados
top_10_monthly_deaths['year_month'] = top_10_monthly_deaths['year'].astype(str) + '-' + top_10_monthly_deaths['month'].astype(str).str.zfill(2)

pivot_data = top_10_monthly_deaths.pivot(index='state', columns='year_month', values='deathIncrease')

plt.figure(figsize=(16, 8))
sns.heatmap(pivot_data, cmap='YlOrRd', annot=True, fmt='.0f', cbar_kws={'label': 'Muertes'})
plt.title('Muertes Mensuales por COVID-19 en los 10 Estados Más Afectados')
plt.xlabel('Año-Mes')
plt.ylabel('Estado')
plt.tight_layout()
plt.show()

# 3. Gráfico de líneas para la evolución de muertes en los 5 estados más afectados (Plotly)
top_5_states = state_total_deaths.head(5).index
top_5_data = df[df['state'].isin(top_5_states)]

fig = px.line(top_5_data, x='date', y='death', color='state',
              title='Evolución de Muertes por COVID-19 en los 5 Estados Más Afectados',
              labels={'date': 'Fecha', 'death': 'Muertes Acumuladas', 'state': 'Estado'})
fig.show()

# 4. Gráfico de burbujas para el mes con más muertes por estado (Plotly)
fig = px.scatter(max_deaths_by_state, x='month', y='deathIncrease', size='deathIncrease', color='state',
                 hover_name='state', size_max=60,
                 title='Mes con Mayor Número de Muertes por COVID-19 en Cada Estado',
                 labels={'month': 'Mes', 'deathIncrease': 'Número de Muertes', 'state': 'Estado'})
fig.show()

# Imprimir los resultados
print("Meses con mayor incidencia de muertes por COVID-19 en cada estado:")
for _, row in max_deaths_by_state.iterrows():
    state = row['state']
    year = row['year']
    month = row['month']
    deaths = row['deathIncrease']
    print(f"{state}: {datetime(year, month, 1).strftime('%B %Y')} - {deaths:.0f} muertes")
  


# 1. Mapa de calor de hospitalizaciones por estado y mes
df['month_year'] = df['date'].dt.to_period('M').astype(str)  # Convertir a string
heatmap_data = df.groupby(['state', 'month_year'])['hospitalizedCurrently'].mean().unstack()

fig1 = px.imshow(heatmap_data, 
                 labels=dict(x="Mes", y="Estado", color="Hospitalizaciones promedio"),
                 title="Mapa de calor de hospitalizaciones por COVID-19 por estado y mes")
fig1.update_xaxes(side="top")
fig1.show()

# 2. Gráfico de líneas de hospitalizaciones para los 10 estados más afectados
top_10_states = df.groupby('state')['hospitalizedCurrently'].max().nlargest(10).index

fig2 = go.Figure()
for state in top_10_states:
    state_data = df[df['state'] == state].groupby('month_year')['hospitalizedCurrently'].mean()
    fig2.add_trace(go.Scatter(x=state_data.index, y=state_data.values, name=state, mode='lines+markers'))

fig2.update_layout(title="Hospitalizaciones mensuales en los 10 estados más afectados",
                   xaxis_title="Mes",
                   yaxis_title="Hospitalizaciones promedio")
fig2.show()

# 3. Gráfico de barras apiladas de la proporción de hospitalizaciones por región
df['region'] = pd.cut(df['hospitalizedCurrently'], 
                      bins=[0, 1000, 5000, 10000, float('inf')],
                      labels=['Baja', 'Media', 'Alta', 'Muy alta'])

regional_data = df.groupby(['month_year', 'region']).size().unstack(fill_value=0)
regional_data_pct = regional_data.div(regional_data.sum(axis=1), axis=0)

fig3 = px.bar(regional_data_pct, 
              title="Proporción de estados por nivel de hospitalización a lo largo del tiempo",
              labels={'value': 'Proporción de estados', 'month_year': 'Mes'})
fig3.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
fig3.show()