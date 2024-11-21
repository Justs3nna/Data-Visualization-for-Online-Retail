import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the dataset
data = pd.read_excel('Online Retail.xlsx')

# Preprocessing
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'], format='%d %m %Y %H:%M')  # Ensure correct date format
data['TotalSales'] = data['Quantity'] * data['UnitPrice']  # Calculate total sales

# Initialize Dash App
app = dash.Dash(__name__)

# Layout for Dashboard
app.layout = html.Div(style={'backgroundColor': '#f0f8ff', 'padding': '30px'}, children=[
    # Header
    html.H1("Online Retail Dashboard", style={
        'textAlign': 'center', 'color': '#1E3A8A', 'fontSize': '40px', 'fontWeight': 'bold', 'marginBottom': '40px'
    }),

    # Filter Controls
    html.Div([
        # Date Picker Range
        html.Div([
            html.Label("Select Date Range:", style={'color': '#1E3A8A', 'fontSize': '18px'}),
            dcc.DatePickerRange(
                id='date-range',
                start_date=data['InvoiceDate'].min(),
                end_date=data['InvoiceDate'].max(),
                display_format='YYYY-MM-DD',
                style={'width': '60%', 'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '5px'}
            )
        ], style={'marginBottom': '30px', 'display': 'inline-block', 'width': '45%'}),

        # Country Filter
        html.Div([
            html.Label("Filter by Country:", style={'color': '#1E3A8A', 'fontSize': '18px'}),
            dcc.Dropdown(
                id='country-filter',
                options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                placeholder="Select a Country",
                style={'width': '60%', 'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '5px'}
            )
        ], style={'marginBottom': '30px', 'display': 'inline-block', 'width': '45%'}),

        # Product Filter
        html.Div([
            html.Label("Filter by Product:", style={'color': '#1E3A8A', 'fontSize': '18px'}),
            dcc.Dropdown(
                id='product-filter',
                options=[{'label': product, 'value': product} for product in data['Description'].dropna().unique()],
                placeholder="Select a Product",
                style={'width': '60%', 'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '5px'}
            )
        ], style={'marginBottom': '40px', 'display': 'flex', 'justifyContent': 'center'}),

    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '40px'}),

    # Key Metrics
    html.Div([
        html.Div([
            html.H3("Total Sales", style={'color': '#1E3A8A'}),
            html.H4(id='total-sales', style={'color': '#1E3A8A'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '20px', 'borderRadius': '5px', 'backgroundColor': '#ffffff'}),

        html.Div([
            html.H3("Top-Selling Product", style={'color': '#1E3A8A'}),
            html.H4(id='top-product', style={'color': '#1E3A8A'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '20px', 'borderRadius': '5px', 'backgroundColor': '#ffffff'}),

        html.Div([
            html.H3("Total Quantity Sold", style={'color': '#1E3A8A'}),
            html.H4(id='total-quantity', style={'color': '#1E3A8A'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '20px', 'borderRadius': '5px', 'backgroundColor': '#ffffff'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '40px'}),

    # Graphs and Visualizations
    dcc.Graph(id='sales-by-country', style={'height': '500px', 'borderRadius': '10px'}),
    dcc.Graph(id='sales-over-time', style={'height': '500px', 'borderRadius': '10px'}),
    dcc.Graph(id='top-products', style={'height': '500px', 'borderRadius': '10px'}),
    dcc.Graph(id='sales-scatter', style={'height': '500px', 'borderRadius': '10px'}),
])

# Callback for updating the graphs and key metrics
@app.callback(
    [Output('sales-by-country', 'figure'),
     Output('sales-over-time', 'figure'),
     Output('top-products', 'figure'),
     Output('sales-scatter', 'figure'),
     Output('total-sales', 'children'),
     Output('top-product', 'children'),
     Output('total-quantity', 'children')],
    [Input('country-filter', 'value'),
     Input('product-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_graphs(selected_country, selected_product, start_date, end_date):
    filtered_data = data

    # Apply date range filter
    filtered_data = filtered_data[(filtered_data['InvoiceDate'] >= pd.to_datetime(start_date)) & 
                                   (filtered_data['InvoiceDate'] <= pd.to_datetime(end_date))]

    # Apply country filter
    if selected_country:
        filtered_data = filtered_data[filtered_data['Country'] == selected_country]

    # Apply product filter
    if selected_product:
        filtered_data = filtered_data[filtered_data['Description'] == selected_product]

    # Key Metrics
    total_sales = filtered_data['TotalSales'].sum()
    total_quantity = filtered_data['Quantity'].sum()
    top_product = filtered_data.groupby('Description')['Quantity'].sum().idxmax()

    # Graph 1: Total Sales by Country
    country_sales = filtered_data.groupby('Country')['TotalSales'].sum().reset_index()
    fig1 = px.bar(country_sales, x='Country', y='TotalSales',
                  title="Total Sales by Country", labels={'TotalSales': 'Total Sales'},
                  color='Country', color_discrete_sequence=px.colors.qualitative.Set1)

    # Graph 2: Total Sales Over Time
    fig2 = px.line(filtered_data, x='InvoiceDate', y='TotalSales', color='Country',
                   title="Total Sales Over Time", labels={'TotalSales': 'Total Sales'},
                   line_shape='linear', markers=True, color_discrete_sequence=px.colors.qualitative.Set1)

    # Graph 3: Top-Selling Products
    product_sales = filtered_data.groupby('Description')['Quantity'].sum().reset_index()
    top_products = product_sales.sort_values(by='Quantity', ascending=False).head(10)
    fig3 = px.pie(top_products, names='Description', values='Quantity', title="Top-Selling Products")

    # Graph 4: Sales by Region (Scatter plot for Country vs Quantity Sold)
    fig4 = px.scatter(filtered_data, x='Country', y='Quantity', color='Country',
                      title="Sales by Region", labels={'Quantity': 'Quantity Sold'})

    return fig1, fig2, fig3, fig4, f'${total_sales:,.2f}', top_product, total_quantity

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
