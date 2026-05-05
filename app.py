import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Set the layout of the web app
st.set_page_config(page_title="Mekko Chart MVP", layout="wide")

st.title("📊 Mekko Chart Generator")

# --- UI: CHOOSE DATA FORMAT ---
st.markdown("### Step 1: How is your data formatted?")
data_format = st.radio(
    "Select your layout:",
    [
        "Format A: Absolute Numbers (Rows = Competitors, Columns = Markets)",
        "Format B: Pre-calculated Percentages (Rows = Markets, Column 1 = Market Size %, Columns 2+ = Competitor Shares %)"
    ]
)

with st.expander("See formatting examples (Click to expand)"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Format A Example:**")
        st.dataframe(pd.DataFrame({
            'North America': [500, 300], 'Europe': [200, 400]
        }, index=['Company A', 'Company B']))
    with col2:
        st.markdown("**Format B Example (Your Screenshot):**")
        st.dataframe(pd.DataFrame({
            'Share (%)': ['20%', '35%'], 'Company A': ['35%', '25%'], 'Company B': ['25%', '38%']
        }, index=['North America', 'Europe']))

# --- UI: FILE UPLOAD ---
st.markdown("### Step 2: Upload Data")
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Read the file
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file, index_col=0)
    else:
        df = pd.read_excel(uploaded_file, index_col=0)
        
    st.write("### Your Data Preview")
    st.dataframe(df)

    # --- DATA CLEANING ---
    # Strip '%' signs if they exist and convert everything to numbers
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # --- MATH & LOGIC BASED ON FORMAT ---
    if "Format A" in data_format:
        plot_labels = df.columns.tolist()
        competitors = df.index.tolist()
        
        segment_totals = df.sum(axis=0).values
        total_market = segment_totals.sum()
        segment_pcts = (segment_totals / total_market) * 100
        
        df_pct = df.div(segment_totals, axis=1) * 100
        plot_df = df_pct

    else:
        # Format B (Screenshot Style)
        plot_labels = df.index.astype(str).tolist()
        competitors = df.columns[1:].tolist() # Skip the first column (Share)
        
        # Market Share (Widths)
        segment_pcts = df.iloc[:, 0].values
        if segment_pcts.sum() <= 1.5: # If they uploaded 0.20 instead of 20
            segment_pcts = segment_pcts * 100
            
        # Competitor Shares (Heights)
        plot_df = df[competitors].T # Transpose so rows are competitors
        if plot_df.max().max() <= 1.5: # If they uploaded 0.35 instead of 35
            plot_df = plot_df * 100

    # Calculate X-Axis Positions (Centers of the blocks)
    cum_widths = np.cumsum(segment_pcts)
    x_centers = cum_widths - (segment_pcts / 2)

    # --- PLOTTING ---
    fig = go.Figure()

    for category in competitors:
        y_values = plot_df.loc[category].values 
        
        # Create text labels: show the percentage, but hide it if the block is too tiny (< 4%)
        text_labels = [f"{val:.0f}%" if val >= 4 else "" for val in y_values]

        fig.add_trace(go.Bar(
            name=str(category),
            x=x_centers,
            y=y_values,
            width=segment_pcts,
            text=text_labels,                                  
            textposition='inside',                             
            insidetextanchor='middle',                         
            textfont=dict(color='white', size=14, family='Arial'), 
            hovertemplate="<b>%{name}</b><br>Share: %{y:.1f}%<extra></extra>"
        ))

    # --- CREATE TOP HEADERS (e.g. "North America (20%)") ---
    annotations = []
    for x_pos, col_name, pct in zip(x_centers, plot_labels, segment_pcts):
        annotations.append(dict(
            x=x_pos,
            y=102, # Position slightly above the 100% mark
            text=f"<b>{col_name}</b><br>({pct:.0f}%)",
            showarrow=False,
            font=dict(size=12, color='black'),
            xanchor='center',
            yanchor='bottom'
        ))

    # --- CHART FORMATTING ---
    fig.update_layout(
        barmode='stack',
        title="Market Share by Segment",
        annotations=annotations, 
        xaxis=dict(
            title="",
            range=[0, 100],
            ticksuffix="%", 
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="",
            range=[0, 120], 
            ticksuffix="%",
            tickfont=dict(size=12)
        ),
        template="plotly_white",
        hovermode="x unified",
        bargap=0, 
        margin=dict(t=80) 
    )

    # Add a white border around each block
    fig.update_traces(marker_line_width=1.5, marker_line_color="white")

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)