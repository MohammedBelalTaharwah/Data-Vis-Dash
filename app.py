import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# 1. تجهيز البيانات (نفس الخطوات السابقة)
df = pd.read_csv('Retail_Light.csv')
df = df[(df['Quantity'] > 0) & (df['Price'] > 0)].copy()
df['TotalPrice'] = df['Quantity'] * df['Price']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Month_Year'] = df['InvoiceDate'].dt.to_period('M').astype(str)

# أخذ قائمة بالدول المتاحة للفلتر (سنستبعد بعض الدول التي بياناتها قليلة جداً لتجنب الأخطاء)
top_countries = df['Country'].value_counts().head(15).index.tolist()
filtered_df = df[df['Country'].isin(top_countries)]

# 2. تهيئة تطبيق Dash
app = dash.Dash(__name__)
server = app.server

# 3. تصميم واجهة المستخدم (Layout)
app.layout = html.Div([
    html.H1("Online Retail Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial'}),
    
    # أداة الفلترة: Dropdown لاختيار الدولة
    html.Div([
        html.Label("Select a Country:"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in top_countries],
            value='Germany', # القيمة الافتراضية
            clearable=False
        )
    ], style={'width': '40%', 'margin': 'auto', 'paddingBottom': '20px'}),
    
    # مساحة الرسومات البيانية
    html.Div([
        dcc.Graph(id='revenue-trend-chart', style={'display': 'inline-block', 'width': '50%'}),
        dcc.Graph(id='top-products-chart', style={'display': 'inline-block', 'width': '50%'})
    ])
])

# 4. ربط الفلتر بالرسومات البيانية (Callbacks)
@app.callback(
    [Output('revenue-trend-chart', 'figure'),
     Output('top-products-chart', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_charts(selected_country):
    # فلترة البيانات بناءً على الدولة المختارة
    country_data = filtered_df[filtered_df['Country'] == selected_country]
    
    # الرسم الأول: خط زمني للإيرادات الشهرية
    trend_data = country_data.groupby('Month_Year')['TotalPrice'].sum().reset_index()
    fig_trend = px.line(trend_data, x='Month_Year', y='TotalPrice', markers=True,
                        title=f'Monthly Revenue Trend for {selected_country}')
    fig_trend.update_traces(hovertemplate='Month: %{x}<br>Revenue: $%{y:,.2f}')
    
    # الرسم الثاني: أعلى 5 منتجات مبيعاً
    top_products = country_data.groupby('Description')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=False).head(5)
    fig_products = px.bar(top_products, x='Quantity', y='Description', orientation='h',
                          title=f'Top 5 Products in {selected_country}',
                          color='Quantity', color_continuous_scale='Blues')
    fig_products.update_layout(yaxis={'categoryorder':'total ascending'})
    
    return fig_trend, fig_products

# 5. تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)