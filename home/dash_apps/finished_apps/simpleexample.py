######################################################## Defining Imports
import pandas as pd
import plotly_express as px
from datetime import datetime as dt
from datetime import timedelta
import re
import dash_table.DataTable
from google.cloud import bigquery
from google.oauth2 import service_account
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash



# #########################################################   Configuring Big Query Client for Dash
# def configpath():
#     try:
#         project_id = 'qinsights'
#         client = bigquery.Client(project=project_id)
#     except:
#         client = None
#     return client
#
#
# ######################################################### Retrieving Data from Big Query
#
# client = configpath()
# if client is None:
#     print("Credentials is not found ")
# else:
#     try:
#         query = """
#                 select clientkey as Client_Key, date as Date, month as Month, monthnumber as Month_No, monthyear as Month_Year,
#                 year as Year,sum(claimcount) as Claim_Count,sum(Chargevoid) as Charges_Void,sum(ifnull(ChargeAmount,0)) as Charge_Amount,
#                  SUM(NetCharges) as Net_Charges, SUM(BillingGoal) as Charges_Goal from
#                 (select clientkey, date, year, month, monthnumber, monthyear, sum(ifnull(BillingClaims,0)) as claimcount, sum(ifnull(NetCharges,0)) as NetCharges, sum(ifnull(NetPayment,0)) as NetPayment,
#                 sum(ifnull(InsurancePayment,0)) as InsurancePayment, sum(ifnull(PatientPayment,0)) as PatientPayment, sum(ifnull(PostingGoal,0)) as ProExpNetPayment,
#                 sum(ifnull(PayTotalallowedAmount,0)) as PayTotalallowedAmount, sum(ifnull(chargesTotalAllowedAmount,0)) as chargesTotalAllowedAmount,
#                 round(sum(ifnull(BillingGoal,0)),0) as BillingGoal,
#                 sum(ifnull(WriteOff,0)) as WriteOff, sum(ifnull(withhold,0)) as withhold, sum(ifnull(OtherAdjustment,0)) as OtherAdjustment,
#                 sum(ifnull(Chargevoid,0)) as Chargevoid, sum(ifnull(ChargeAmount,0)) as ChargeAmount, sum(ifnull(voidedNetCollectionAmount,0)) as voidedNetCollectionAmount,
#                 sum(ifnull(NetCollectionAmount,0)) as NetCollectionAmount, sum(ifnull(TotalReserve,0)) as  TotalReserve, sum(ifnull(NetPaymentWithReserve,0)) as NetPaymentWithReserve
#                 from QinsightProductionData.Model_PaymentVoidDayWise
#                 group by clientkey, year, month, monthnumber, monthyear, date
#
#                 order by date DESC, monthnumber DESC, year DESC
#                 ) group by date, month, monthnumber, monthyear, year,clientkey
#                 order by date DESC, monthnumber DESC, year DESC"""
#
#         job_config = bigquery.QueryJobConfig()
#         job_config.use_query_cache = True
#         query_job = client.query(query, location="US", job_config=job_config)
#         df = query_job.to_dataframe()
#         print(df)
#
#     except Exception as e:
#         print(str(e))
# ######################################################## Data Preprocessing
#
# df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
# df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
#
# for col in df.columns:
#     if col == 'Claim_Count' or col == 'Charges_Void' or col == 'Charge_Amount' or col == 'Net_Charges' or col == 'Charges_Goal':
#         df[col] = round(df[col].astype(float))
#         df[col] = df[col].astype(int)
#
# print(
#     "####################################################Processed Datafrane###################################################")
# print(df)
# print(
#     "##########################################################################################################################")
##################################################### Dash Frame Work Starts

app = DjangoDash('SimpleExample')

################################################ Building App layout

# --------------------------------------------------------------- 1.)        RETRIEVE DATA
df = pd.read_excel("C:\\Users\\piyus\\PycharmProjects\\plotly-dash-django-udemy\\home\dash_apps\\finished_apps\\omg_charges_and_payments.xlsx")
print(df)
df['charge_date'] = pd.to_datetime(df['charge_date'], format='%Y-%b-%dT%H:%M:%S')
df['charge_date'] = pd.to_datetime(df['charge_date'], format='%Y-%b-%dT%H:%M:%S')
df['date_of_responsibility'] = pd.to_datetime(df['date_of_responsibility'], format='%Y-%b-%dT%H:%M:%S')
dff = df.groupby(['facility', 'provider', 'cpt_group', 'cpt', 'charge_date'], as_index=False)[
    ['charges', 'payments', 'total_outstanding']].sum()
# --------------------------------------------------------------- 2.)        BUILD LAYOUT


app.layout = html.Div([
    html.Div([
        # html.Div(
        #     html.Img(src='/assets/QInsight-logo.png'),
        #     className='one-third column'
        # ),
        html.Div(
            html.H3('QInsights Analytics', style={'text-align': 'center', 'font-family': 'Georgia, serif'}),
            className='two-thirds columns'
        ),
    ], className='row'),

    # dcc.Tabs(id='dashboard-tabs', value='tab-1', children=[
    #     dcc.Tab(label='Revenue Cycle Management', value='RCM',style={'font-size':'20px','font-family': 'Georgia, serif','text-align':'center'}),
    #     dcc.Tab(label='Accounts Receivable', value='AR',style={'font-size':'20px','font-family': 'Georgia, serif','text-align':'center'}),
    #     dcc.Tab(label='Rejections Analysis', value='REJ',style={'font-size':'20px','font-family': 'Georgia, serif','text-align':'center'}),
    # ]),
    html.Div(id='tabs-example-content'),
    html.Div([
        html.Div([
            html.P('Select a metric:',
                   style={'font-size': '14px', 'font-family': 'Georgia, serif', 'text-align': 'center'}),
            dcc.Dropdown(id='metricdropdown',
                         options=[
                             {'label': 'Facility', 'value': 'facility'},
                             {'label': 'provider', 'value': 'provider'},
                             {'label': 'cpt_group', 'value': 'cpt_group'}
                         ],
                         value='charges',
                         multi=False,
                         clearable=False,
                         style={'font-family': 'Georgia, serif', 'margin': '5px'}
                         ),
        ], className='four columns'),
        # html.Div([
        #     html.P('Select a facility:',style={'font-size':'14px','font-family': 'Georgia, serif','text-align':'center'}),
        #     dcc.Dropdown(id='facilitydropdown',
        #         options=[{'label':i, 'value':i} for i in dff.facility.unique()],
        #         placeholder='Select a facility...',
        #         value='TRIATRIA',
        #         multi=True,
        #         clearable=False,
        #         searchable=True,
        #         style={'font-family': 'Georgia, serif','margin':'5px'}
        #     ),
        # ], className='four columns'),
        #
        # html.Div([
        #     html.P('Select a provider:',style={'font-size':'14px','font-family': 'Georgia, serif','text-align':'center'}),
        #     dcc.Dropdown(id='providerdropdown',
        #         options=[{'label':i, 'value':i} for i in dff.provider.unique()],
        #         placeholder='Select a provider...',
        #         value='JEFFREY MARGOLIS',
        #         multi=True,
        #         clearable=False,
        #         searchable=True,
        #         style={'font-family': 'Georgia, serif','margin':'5px'}
        #     ),
        # ],className='four columns'),
    ], className='row'),

    html.Div([
        html.Div([
            html.P('Select a date range:'),
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(2010, 1, 1),
                max_date_allowed=dt(2020, 12, 31),
                initial_visible_month=dt.today(),
                start_date=dt(2020, 5, 1),
                end_date=dt(2020, 6, 10)
            )
        ],
            className='row', style={'text-align': 'center', 'align': 'center', 'font-family': 'Georgia, serif'}),
        # html.Div([
        #     dcc.Graph(id='barchart'),
        # ], className='four columns',style={'font-family': 'Georgia, serif','margin':'0px'}),
        #
        # html.Div([
        #     dcc.Graph(id='linechart'),
        # ], className='four columns',style={'font-family': 'Georgia, serif','margin':'0px'}),
        #
        # html.Div([
        #     dcc.Graph(id='piechart'),
        # ],className='four columns',style={'font-family': 'Georgia, serif','margin':'0px'}),
    ], className='row', style={'margin': '0px'}),

    html.Div([
        html.H3(id='output-total', children='', style={'text-align': 'center', 'font-family': 'Georgia, serif'})
    ]),

    html.Div([
        dash_table.DataTable(
            id='datatable_id',
            data=dff.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=False,
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=25,
            style_header={
                'text-align': 'center',
                'backgroundColor': 'rgb(129, 185, 170)'
            },
            style_cell={
                'text-align': 'center',
                'font-family': 'Georgia, serif',
                'backgroundColor': 'rgb(237, 255, 255)',
                'color': 'black'
            }
        ), ]
        , className='row'),
])


# ------------------------------------------------------------------ 3.)     BUILD FUNCTIONALITY
@app.callback(
    [Output('output-total', 'children'),
     Output('datatable_id', 'data')],
    [Input('datatable_id', 'selected_rows'),
     Input('metricdropdown', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')]
)
def update_data(chosen_rows, metricdropval, start_date, end_date):
    if len(chosen_rows) == 0:
        df_filterd = dff[
            dff['facility'].isin(['TRIATRIA', 'MHP ROYAL OAK J204RO', 'MHP MAD HEIGHTS J204', 'MHP FARM HILLS J204'])]
    else:
        print(chosen_rows)
        df_filterd = dff[dff.index.isin(chosen_rows)]

    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')
    if end_date is not None:
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')

    list_chosen_facilities = df_filterd['facility'].tolist()
    list_chosen_providers = df_filterd['provider'].tolist()

    df_filterd = df_filterd[(df_filterd['charge_date'] >= start_date) & (df_filterd['charge_date'] <= end_date)]
    # df_filterd = df_filterd[(df_filterd['facility'].isin([facilitydropval])) & (df_filterd['provider'].isin([providerdropval]))]

    # pie_chart=px.pie(
    #         data_frame=df_filterd,
    #         names='cpt_group',
    #         values=metricdropval,
    #         hole=.3,
    #         labels={'cpt_group':'CPT Group'}
    #         )
    # pie_chart.update_layout(uirevision='foo',
    # legend=dict(
    #         traceorder='normal',
    #         font=dict(
    #             family='Georgia, serif',
    #             size=10,
    #             color='black'
    #         ),
    #         itemsizing='constant',
    #         bordercolor='Black',
    #         borderwidth=1,
    #         itemclick='toggleothers')
    #     ,showlegend=True)
    #
    #
    # dff_by_provider = df_filterd.groupby(['provider'], as_index=False)[['charges', 'payments', 'total_outstanding']].sum()
    # dff_by_provider['abbr_provider'] = dff_by_provider['provider'].apply(lambda x: x[0] + '. ' + x.split(' ')[-1])
    #
    # bar_chart = px.bar(
    #         data_frame=dff_by_provider,
    #         x=metricdropval,
    #         y='abbr_provider',
    #         orientation='h',
    #         hover_data=['provider', metricdropval],
    #         color=metricdropval,
    #         color_continuous_scale=px.colors.sequential.Emrld,
    #         text=metricdropval,
    #         labels={metricdropval: metricdropval, 'abbr_provider': 'Provider'}
    #         )
    # bar_chart.update_layout(uirevision='foo', yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    # bar_chart.update_traces(texttemplate='%{text:$.2s}', textposition='outside')
    # bar_chart.update_xaxes(range=[dff_by_provider[metricdropval].min(), dff_by_provider[metricdropval].max()+(dff_by_provider[metricdropval].max()*0.25)])
    #
    #
    # dff_by_date = df_filterd.groupby(['provider','charge_date'], as_index=False)[['charges', 'payments', 'total_outstanding']].sum()
    #
    # line_chart = px.line(
    #         data_frame=dff_by_date,
    #         x='charge_date',
    #         range_x=[dff_by_date.charge_date.min(),dff_by_date.charge_date.max()],
    #         y=metricdropval,
    #         color='provider',
    #         labels={'provider':'Provider', 'charge_date':'Charge Date','charges':'Charges'},
    #         )
    # line_chart.update_layout(uirevision='foo',showlegend=False)

    if metricdropval == 'facility':
        metric_total = 'Total Charges: ${:,.2f}'.format(df_filterd.charges.sum())
        dff_facility = df.groupby(['facility', 'charge_date'], as_index=False)[
            ['charges', 'payments', 'total_outstanding']].sum()
        df_filterd = dff_facility[
            (dff_facility['charge_date'] >= start_date) & (dff_facility['charge_date'] <= end_date)]
        print("#############################################################")
        print(dff_facility)
        print("#############################################################")
        data_table_content = df_filterd.to_dict('records')
    elif metricdropval == 'provider':
        metric_total = 'Total Payments: ${:,.2f}'.format(df_filterd.payments.sum())
        dff_provider = df.groupby(['provider', 'charge_date'], as_index=False)[
            ['charges', 'payments', 'total_outstanding']].sum()
        df_filterd = dff_provider[
            (dff_provider['charge_date'] >= start_date) & (dff_provider['charge_date'] <= end_date)]
        data_table_content = dff_provider.to_dict('records')
    else:
        metric_total = 'Total Outstanding: ${:,.2f}'.format(df_filterd.total_outstanding.sum())
        dff_cpt_group = df.groupby(['cpt_group', 'charge_date'], as_index=False)[
            ['charges', 'payments', 'total_outstanding']].sum()
        df_filterd = dff_cpt_group[
            (dff_cpt_group['charge_date'] >= start_date) & (dff_cpt_group['charge_date'] <= end_date)]
        data_table_content = df_filterd.to_dict('records')

    # return (pie_chart,bar_chart,metric_total)
    return (metric_total, data_table_content)


if __name__ == '__main__':
    app.run_server(debug=True)