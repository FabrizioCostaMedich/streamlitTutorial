import streamlit as st
from utils.utils import *


def get_list(attributo):
    query = f"SELECT DISTINCT {attributo} FROM products"
    result = execute_query(st.session_state["connection"], query)
    result_list = []
    for row in result.mappings():
        result_list.append(row[attributo])
    return result_list


def get_info():
    return get_list("productLine"), get_list("productScale"), get_list("productVendor")

def check_info(prod_dict):
    for value in prod_dict.values():
        if value=='':
            return False
    return True

def insert(prod_dict):
    if check_info(prod_dict):
        attributi = ", ".join(prod_dict.keys())
        valori = tuple(prod_dict.values())
        query = f"INSERT INTO products ({attributi}) VALUES {valori}"
        try:
            execute_query(st.session_state["connection"], query)
            st.session_state["connection"].commit()
        except Exception as e:
            st.error(e)
            return False
        return True
    else:
        return False

def create_form():
    with st.form("Nuovo Prodotto"):
        st.header(':blue[Aggiungi Prodotto:]')

        code = st.text_input("Codice", placeholder="S**_****")
        nome = st.text_input("Nome", placeholder="Inserisci il nome del prodotto")

        categorie, scale, venditori = get_info()

        categoria = st.selectbox("Scala", categorie)
        scala = st.selectbox("Scala", scale)
        venditore = st.selectbox("Venditore", venditori)

        descrizione = st.text_area("Descrizione", placeholder="Inserisci una descrizione")
        qta = st.slider("Quantità", 0, 10000)
        prezzo = st.number_input("Prezzo", 1.0)
        msrp = st.number_input("MSRP")

        insert_dict = {"productCode": code, "productName": nome, "productLine": categoria, "productScale": scala,
                       "productVendor": venditore, "productDescription": descrizione, "quantityInStock": qta,
                       "buyPrice": prezzo, "MSRP": msrp}

        submitted = st.form_submit_button("Submit")

        if submitted:
            if insert(insert_dict):
                st.success("HAI INSERITO I DATI CON SUCCESSO: ", icon='✅')
                st.write(insert_dict)
            else:
                st.error("ERRORE NELL'INSERIMENTO DEI DATI", icon='⚠️')



if __name__ == "__main__":
    st.title("🖊 Aggiungi")

    if check_connection():
        create_form()
