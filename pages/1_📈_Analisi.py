import datetime

import streamlit as st
from utils.utils import *
import pandas as pd


#ogni tab ha una funzione separata

def create_tab_prodotti(tab_prodotti):
    col1, col2, col3 = tab_prodotti.columns(3)
    payment_info = execute_query(st.session_state["connection"],
                                 "SELECT SUM(amount) as 'Total Amount', MAX(amount) as 'Max Payment', AVG(amount) as 'Average Payment' FROM payments;")
    payment_info_dict = [dict(zip(payment_info.keys(), result)) for result in payment_info]
    col1.metric("Importo Totale", f'{compact_format(payment_info_dict[0]["Total Amount"])}')
    col2.metric("Massimo Importo", f'{compact_format(payment_info_dict[0]["Max Payment"])}')
    col3.metric("Importo Medio", f'{compact_format(payment_info_dict[0]["Average Payment"])}')

    with tab_prodotti.expander("Panoramica Prodotti", True):
        prod_col1, prod_col2, prod_col3 = st.columns(3)
        sort_param = prod_col1.radio("Ordina Per", ["code", "name", "quantity", "price"])
        sort_choice = prod_col2.selectbox("Ordine", ["Crescente", "Decrescente"])

        sort_dict = {"Crescente": "ASC", "Decrescente": "DESC"}

        if prod_col1.button("Mostra", type="primary"):
            query_base = "SELECT productCode AS 'code', productName AS 'name', quantityInStock AS quantity, buyPrice AS price, MSRP FROM products"
            query_sort = f'ORDER BY {sort_param} {sort_dict[sort_choice]};'
            prodotti = execute_query(st.session_state["connection"], query_base + " " + query_sort)
            df_prodotti = pd.DataFrame(prodotti)
            st.dataframe(df_prodotti, use_container_width=True)
    with tab_prodotti.expander("Pagamenti", True):
        query = "SELECT MIN(paymentDate) as min, MAX(paymentDate) as max FROM payments"
        date = execute_query(st.session_state["connection"], query)
        min_max = [dict(zip(date.keys(), result)) for result in date]

        min = min_max[0]["min"]
        max = min_max[0]["max"]


        date_range = st.date_input("Seleziona il range di date:", value=(min, max), min_value=min, max_value=max)

        if date_range[0] is not None and date_range[1] is not None:
            query = f"SELECT paymentDate, SUM(amount) as 'TotalAmount' FROM payments WHERE paymentDate > {date_range[0]} AND paymentDate <'{date_range[1]}' GROUP BY paymentDate"
            paymentdates = execute_query(st.session_state["connection"], query)
            df_paymentDate = pd.DataFrame(paymentdates)

            if df_paymentDate.empty:
                st.warning("Nessun dato trovato.", icon='⚠️')
            else:
                df_paymentDate['TotalAmount'] = df_paymentDate['TotalAmount'].astype(float)
                df_paymentDate['paymentDate'] = pd.to_datetime(df_paymentDate['paymentDate'])

                st.write(f"Periodo {date_range[0]} . {date_range[1]}")
        st.line_chart(df_paymentDate, x="paymentDate", y="TotalAmount")


if __name__ == "__main__":
    st.title("📈 Analisi")

    #creazione dei tab distinti
    tab_prodotti, tab_staff, tab_clienti = st.tabs(["Prodotti", "Staff", "Clienti"])

    if check_connection():
        create_tab_prodotti(tab_prodotti)
