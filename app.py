import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from io import BytesIO

months = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
]

st.set_page_config(layout='wide')

df = pd.read_csv('ejecucion_agosto.csv')

total_ap = (df.groupby('mes_num')['APR. VIGENTE'].sum() / 1_000_000_000_000).round(1)
total_ej = (df.groupby('mes_num')['OBLIGACION'].sum() / 1_000_000_000_000).round(1)
total_co = (df.groupby('mes_num')['COMPROMISO'].sum() / 1_000_000_000_000).round(1)
total_ej_perc = (df.groupby('mes_num')['perc_ejecucion'].sum() * 100).round(1)
total_co_perc = (df.groupby('mes_num')['perc_compr'].sum() * 100).round(1)

st.title("Ejecución")

sectores = df['Sector'].unique().tolist()
entidades = df['Entidad'].unique().tolist()

tab1, tab2, tab3 = st.tabs(["Vista general",
                            "Navegación detallada",
                            "Descarga de datos"])

with tab1:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Apr. Vigente (bil)", total_ap[8])
    with col2: 
        st.metric("Ejecutado (bil)", total_ej[8])
    with col3:
        st.metric("Comprometido (bil)", total_co[8])
    with col4:
        st.metric("% ejecutado", total_ej_perc[8])
    with col5:
        st.metric("% comprometido", total_co_perc[8])

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Valores (billones)", "Porcentaje (%)"))

    fig.add_trace(go.Scatter(x=months, 
                             y=total_ej.values, 
                             mode='lines+markers',
                            name='Ejecutado', showlegend=False,
                            line=dict(color='#dd722a')), row=1, col=1)
    fig.add_trace(go.Scatter(x=months, 
                             y=total_co.values, 
                             mode='lines+markers', 
                             name='Comprometido', showlegend=False,
                             line=dict(color='#2635bf')), row=1, col=1)

    fig.add_shape(type='line', x0=0, x1=7, y0=total_ap[8], y1=total_ap[8], line=dict(color='#2635bf', dash='dash'),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=months, 
                             y=total_ej_perc.values, 
                             mode='lines+markers', 
                             name='Ejecutado', 
                             line=dict(color='#dd722a')), row=1, col=2)
    fig.add_trace(go.Scatter(x=months, 
                             y=total_co_perc.values, 
                             mode='lines+markers', 
                             name='Comprometido', 
                             line=dict(color='#2635bf')),  row=1, col=2)


    fig.add_shape(type='line', x0=0, x1=7, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                row=1, col=2)

    fig.update_layout(
        title="Ejecución y compromiso general al mes de agosto",
        height=400, 
        width=900,
        legend=dict(
            orientation='h',   # Horizontal legend
            x=0.72,             # Center the legend
            y=1.1,             # Position it slightly above the plots
            xanchor='left',  # Center the legend horizontally
            yanchor='bottom'   # Align the legend vertically
        )
    )
    st.plotly_chart(fig)

    piv_s = (df[df['mes_num'] == 8].pivot_table(index='Sector',
                                   values=['APR. VIGENTE','OBLIGACION', 'COMPROMISO'],
                                   aggfunc='sum')
                                .assign(perc_ejecucion=lambda x: (x['OBLIGACION'] / x['APR. VIGENTE'] * 100).round(1),
                                        perc_compr=lambda x: (x['COMPROMISO'] / x['APR. VIGENTE'] * 100).round(1)))
    tops_ejec = piv_s.sort_values(by='perc_ejecucion', ascending=True).tail(10).reset_index()
    tops_compr = piv_s.sort_values(by='perc_compr', ascending=True).tail(10).reset_index()

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecutado (%)", "Comprometido (%)"))

# Plot absolute values as bar plots in the first subplot
    fig.add_trace(go.Bar(y=tops_ejec['Sector'], 
                         x=tops_ejec['perc_ejecucion'], 
                         name='Ejecutado', 
                         marker_color='#F7B261', 
                         orientation='h',
                        text=tops_ejec['Sector'],
                        textposition='inside',
                        hoverinfo='x'), row=1, col=1)
    fig.add_trace(go.Bar(y=tops_compr['Sector'], 
                         x=tops_compr['perc_compr'], 
                         name='Comprometido', 
                         marker_color='#81D3CD', 
                         orientation='h',
                        text=tops_compr['Sector'],
                        textposition='inside',
                        hoverinfo='x'), row=1, col=2)
    fig.add_shape(
        type='line',
        x0=100, x1=100, y0=-0.5, y1=9.5,  # Set x0, x1 for the vertical line position
        line=dict(color='#dd722a', width=1, dash='dash'),
        row=1, col=1
    )
    fig.add_shape(
        type='line',
        x0=100, x1=100, y0=-0.5, y1=9.5,  # Set x0, x1 for the vertical line position
        line=dict(color='#81D3CD', width=1, dash='dash'),
        row=1, col=2
    )
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(
        title="Top 10 sectores por ejecución (al mes de agosto) ",
        height=400, 
        width=900,
        legend=dict(
            orientation='h',   # Horizontal legend
            x=0.72,             # Center the legend
            y=1.1,             # Position it slightly above the plots
            xanchor='left',  # Center the legend horizontally
            yanchor='bottom'   # Align the legend vertically
        )
    )
    st.plotly_chart(fig)

    piv_e = (df[df['mes_num'] == 8].pivot_table(index='Entidad',
                                   values=['APR. VIGENTE','OBLIGACION', 'COMPROMISO'],
                                   aggfunc='sum')
                                .assign(perc_ejecucion=lambda x: (x['OBLIGACION'] / x['APR. VIGENTE'] * 100).round(1),
                                        perc_compr=lambda x: (x['COMPROMISO'] / x['APR. VIGENTE'] * 100).round(1))
                                .assign(perc_perdida=lambda x:100 - x['perc_compr']))
    tops_ejec = piv_e.sort_values(by='perc_ejecucion', ascending=True).tail(10).reset_index()
    tops_compr = piv_e.sort_values(by='perc_compr', ascending=True).tail(10).reset_index()
    tops_perd = piv_e.sort_values(by='perc_perdida', ascending=True).tail(10).reset_index()
    bots_ejec = piv_e.sort_values(by='perc_ejecucion', ascending=False).tail(10).reset_index()



    fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecutado (%)", "Pérdida de aprop. (%)"))

# Plot absolute values as bar plots in the first subplot
    fig.add_trace(go.Bar(y=tops_ejec['Entidad'], 
                         x=tops_ejec['perc_ejecucion'], 
                         name='Ejecutado', 
                         marker_color='#F7B261', 
                         orientation='h',
                        text=tops_ejec['Entidad'],
                        textposition='inside',
                        hoverinfo='x'), row=1, col=1)
    fig.add_trace(go.Bar(y=tops_compr['Entidad'], 
                         x=tops_compr['perc_compr'], 
                         name='Comprometido', 
                         marker_color='#81D3CD', 
                         orientation='h',
                        text=tops_compr['Entidad'],
                        textposition='inside',
                        hoverinfo='x'), row=1, col=2)
    fig.add_shape(
        type='line',
        x0=100, x1=100, y0=-0.5, y1=9.5,  # Set x0, x1 for the vertical line position
        line=dict(color='#dd722a', width=1, dash='dash'),
        row=1, col=1
    )
    fig.add_shape(
        type='line',
        x0=100, x1=100, y0=-0.5, y1=9.5,  # Set x0, x1 for the vertical line position
        line=dict(color='#81D3CD', width=1, dash='dash'),
        row=1, col=2
    )
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(
        title="Top 10 entidades por ejecución (al mes de agosto)",
        height=400, 
        width=900,
        legend=dict(
            orientation='h',   # Horizontal legend
            x=0.72,             # Center the legend
            y=1.1,             # Position it slightly above the plots
            xanchor='left',  # Center the legend horizontally
            yanchor='bottom'   # Align the legend vertically
        )
    )
    st.plotly_chart(fig)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecutado (%)", "Comprometido (%)"))

# Plot absolute values as bar plots in the first subplot
    fig.add_trace(go.Bar(y=bots_ejec['Entidad'], 
                         x=bots_ejec['perc_ejecucion'], 
                         name='Ejecutado', 
                         marker_color='#F7B261', 
                         orientation='h',
                        hovertext=bots_ejec['Entidad'],
                        hoverinfo='x+text'), row=1, col=1)
    fig.add_trace(go.Bar(y=tops_perd['Entidad'], 
                         x=tops_perd['perc_compr'], 
                         name='Pérdida de apropiación', 
                         marker_color='#81D3CD', 
                         orientation='h',
                        hovertext=tops_perd['Entidad'],
                        hoverinfo='x+text'), row=1, col=2)
    fig.add_shape(
        type='line',
        x0=100, x1=100, y0=-0.5, y1=9.5,  # Set x0, x1 for the vertical line position
        line=dict(color='#dd722a', width=1, dash='dash'),
        row=1, col=1
    )
    fig.add_shape(
        type='line',
        x0=100, x1=100, y0=-0.5, y1=9.5,  # Set x0, x1 for the vertical line position
        line=dict(color='#81D3CD', width=1, dash='dash'),
        row=1, col=2
    )
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(
        title="Top 10 entidades con menor ejecución y mayor pérdida de apropiación (al mes de agosto)",
        height=400, 
        width=900,
        legend=dict(
            orientation='h',   # Horizontal legend
            x=0.7,             # Center the legend
            y=1.1,             # Position it slightly above the plots
            xanchor='left',  # Center the legend horizontally
            yanchor='bottom'   # Align the legend vertically
        )
    )
    st.plotly_chart(fig)
    
with tab2:
    sector = st.selectbox("Seleccione un sector: ", sectores)

    fil_sector = df[df['Sector'] == sector]
    piv_sector = (fil_sector.pivot_table(index='mes_num',
                   aggfunc='sum',
                   values=['OBLIGACION', 'APR. VIGENTE', 'COMPROMISO'])
                            .div(1_000_000_000, axis=0)
                            .assign(perc_ejecucion=lambda x: (x['OBLIGACION'] / x['APR. VIGENTE'] * 100),
                                    perc_compr=lambda x: x['COMPROMISO'] / x['APR. VIGENTE'] * 100)
                            .round(1))
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Apr. Vigente (mmil)", piv_sector.loc[8, "APR. VIGENTE"])
    with col2: 
        st.metric("Ejecutado (mmil)", piv_sector.loc[8, "OBLIGACION"])
    with col3:
        st.metric("Comprometido (mmil)", piv_sector.loc[8, "COMPROMISO"])
    with col4:
        st.metric("% ejecutado", piv_sector.loc[8, "perc_ejecucion"])
    with col5:
        st.metric("% comprometido", piv_sector.loc[8, "perc_compr"])


    mean_growth_rate = (piv_sector.loc[8, "perc_ejecucion"] / 8) / 100

    # Step 2: Forecast the next 4 values
    last_value = piv_sector['perc_ejecucion'].iloc[-1]
    forecast_values = [last_value * (1 + mean_growth_rate)**i for i in range(1, 5)]

    # Combine original and forecasted values
    full_values = piv_sector['perc_ejecucion'].tolist() + forecast_values
    full_values = [round(i, 1) for i in full_values]

    # Step 3: Create a line plot
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecutado (%)", "Comprometido (%)"))

    # Plot the first 8 values (blue solid line)
    fig.add_trace(go.Scatter(
        x=months[:9],  # x-axis for all values (1 to 12)
        y=full_values[:9],         # All values (original + forecast)
        mode='lines+markers',  # Line and markers
        name='Observado', showlegend=False,
        line=dict(color='#2635bf', width=2),  # Solid blue line for all values
        marker=dict(color=['#2635bf']*9, size=8)  # Red markers for forecasted values
    ), row=1, col=1)

    # Highlight the forecasted part with a red dashed line (the last 4 points)
    fig.add_trace(go.Scatter(
        x=months[8:],  # x-axis for forecasted values
        y=full_values[8:],     # The forecasted values
        mode='lines+markers',          # Just lines (no markers here)
        name='Pronóstico', showlegend=False,
        line=dict(color='#dd722a', width=2, dash='dash'),
        marker=dict(color='#dd722a', size=8),  # Dashed line for forecast
    ), row=1, col=1)

    mean_growth_rate = (piv_sector.loc[8, "perc_compr"] / 8) / 100

    # Step 2: Forecast the next 4 values
    last_value = piv_sector['perc_compr'].iloc[-1]
    forecast_values = [last_value * (1 + mean_growth_rate)**i for i in range(1, 5)]

    # Combine original and forecasted values
    full_values = piv_sector['perc_compr'].tolist() + forecast_values
    full_values = [round(i, 1) for i in full_values]

    fig.add_trace(go.Scatter(
        x=months[:9],  # x-axis for all values (1 to 12)
        y=full_values[:9],         # All values (original + forecast)
        mode='lines+markers',  # Line and markers
        name='Observado',
        line=dict(color='#2635bf', width=2), # Solid blue line for all values
        marker=dict(color=['#2635bf']*9, size=8)  # Red markers for forecasted values
    ), row=1, col=2)



    # Highlight the forecasted part with a red dashed line (the last 4 points)
    fig.add_trace(go.Scatter(
        x=months[8:],  # x-axis for forecasted values
        y=full_values[8:],     # The forecasted values
        mode='lines+markers',          # Just lines (no markers here)
        name='Pronóstico',
        line=dict(color='#dd722a', width=2, dash='dash'),
        marker=dict(color='#dd722a', size=8),  # Dashed line for forecast
    ), row=1, col=2)

    fig.add_shape(type='line', x0=1, x1=12, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                row=1, col=2)
    fig.add_shape(type='line', x0=1, x1=12, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                row=1, col=1)
    fig.update_yaxes(range=[0, max(100, max(full_values))]) 

    fig.update_layout(
        title=f"Ejecución y compromiso al mes de agosto por sector: {sector}",
        height=400, 
        width=900,
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.1,
            xanchor="right",
            x=1   # Align the legend vertically
        )
    )

    # Show the plot
    st.plotly_chart(fig)

    perd_aprop = 100 - full_values[-1]

    if perd_aprop > 0:
        st.error(f"Hay una pérdida de apropiación del {round(perd_aprop, 2)}% para el sector {sector}.")
    else:
        st.success(f"No hay pérdida de apropiación para el sector {sector}.")


    entidad = st.selectbox("Seleccione una entidad: ", entidades)
    fil_entidad = df[df['Entidad'] == entidad]
    piv_entidad = (fil_entidad.pivot_table(index='mes_num',
                   aggfunc='sum',
                   values=['OBLIGACION', 'APR. VIGENTE', 'COMPROMISO'])
                            .div(1_000_000_000, axis=0)
                            .assign(perc_ejecucion=lambda x: (x['OBLIGACION'] / x['APR. VIGENTE'] * 100),
                                    perc_compr=lambda x: x['COMPROMISO'] / x['APR. VIGENTE'] * 100)
                            .round(1))
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Apr. Vigente (mmil)", piv_entidad.loc[8, "APR. VIGENTE"])
    with col2: 
        st.metric("Ejecutado (mmil)", piv_entidad.loc[8, "OBLIGACION"])
    with col3:
        st.metric("Comprometido (mmil)", piv_entidad.loc[8, "COMPROMISO"])
    with col4:
        st.metric("% ejecutado", piv_entidad.loc[8, "perc_ejecucion"])
    with col5:
        st.metric("% comprometido", piv_entidad.loc[8, "perc_compr"])

    mean_growth_rate = (piv_entidad.loc[8, "perc_ejecucion"] / 8) / 100

    # Step 2: Forecast the next 4 values
    last_value = piv_entidad['perc_ejecucion'].iloc[-1]
    forecast_values = [last_value * (1 + mean_growth_rate)**i for i in range(1, 5)]

    # Combine original and forecasted values
    full_values = piv_entidad['perc_ejecucion'].tolist() + forecast_values
    full_values = [round(i, 1) for i in full_values]

    # Step 3: Create a line plot
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecutado (%)", "Comprometido (%)"))

    # Plot the first 8 values (blue solid line)
    fig.add_trace(go.Scatter(
        x=months[:9],  # x-axis for all values (1 to 12)
        y=full_values[:9],         # All values (original + forecast)
        mode='lines+markers',  # Line and markers
        name='Observado', showlegend=False,
        line=dict(color='#2635bf', width=2),  # Solid blue line for all values
        marker=dict(color=['#2635bf']*9, size=8)  # Red markers for forecasted values
    ), row=1, col=1)

    # Highlight the forecasted part with a red dashed line (the last 4 points)
    fig.add_trace(go.Scatter(
        x=months[8:],  # x-axis for forecasted values
        y=full_values[8:],     # The forecasted values
        mode='lines+markers',          # Just lines (no markers here)
        name='Pronóstico', showlegend=False,
        line=dict(color='#dd722a', width=2, dash='dash'),
        marker=dict(color='#dd722a', size=8),  # Dashed line for forecast
    ), row=1, col=1)

    mean_growth_rate = (piv_entidad.loc[8, "perc_compr"] / 8) / 100

    # Step 2: Forecast the next 4 values
    last_value = piv_entidad['perc_compr'].iloc[-1]
    forecast_values = [last_value * (1 + mean_growth_rate)**i for i in range(1, 5)]

    # Combine original and forecasted values
    full_values = piv_entidad['perc_compr'].tolist() + forecast_values
    full_values = [round(i, 1) for i in full_values]

    fig.add_trace(go.Scatter(
        x=months[:9],  # x-axis for all values (1 to 12)
        y=full_values[:9],         # All values (original + forecast)
        mode='lines+markers',  # Line and markers
        name='Observado', showlegend=True,
        line=dict(color='#2635bf', width=2),  # Solid blue line for all values
        marker=dict(color=['#2635bf']*9, size=8)  # Red markers for forecasted values
    ), row=1, col=2)



    # Highlight the forecasted part with a red dashed line (the last 4 points)
    fig.add_trace(go.Scatter(
        x=months[8:],  # x-axis for forecasted values
        y=full_values[8:],     # The forecasted values
        mode='lines+markers',          # Just lines (no markers here)
        name='Pronóstico', showlegend=True,
        line=dict(color='#dd722a', width=2, dash='dash'),
        marker=dict(color='#dd722a', size=8),  # Dashed line for forecast
    ), row=1, col=2)

    fig.add_shape(type='line', x0=1, x1=12, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                row=1, col=2)
    fig.add_shape(type='line', x0=1, x1=12, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                row=1, col=1)
    fig.update_yaxes(range=[0, max(100, max(full_values))]) 

    fig.update_layout(
        title=f"Ejecución y compromiso al mes de agosto por entidad: {entidad}",
        height=400, 
        width=900,
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.1,
            xanchor="right",
            x=1 # Align the legend vertically
        )
    )

    # Show the plot
    st.plotly_chart(fig)

    perd_aprop = 100 - full_values[-1]

    if perd_aprop > 0:
        st.error(f"Hay una pérdida de apropiación del {round(perd_aprop, 2)}% para la entidad {entidad}.")
    else:
        st.success(f"No hay pérdida de apropiación para la entidad {entidad}.")

    
with tab3:
    binary_output = BytesIO()
    df.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar excel',
                    data = binary_output.getvalue(),
                    file_name = 'datos_ejecucion_agosto.xlsx')
