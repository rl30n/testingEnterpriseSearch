from elastic_enterprise_search import AppSearch
from elastic_enterprise_search.exceptions import NotFoundError  # Corrected import
import json
import re
from elasticsearch import Elasticsearch
import pprint
import jsonify

myendpoint = "http://localhost:3002"
mybearer = "private-ysf3m7f6o2bzxpn7mhj8g22z"
my_engine_name = "es-testing-recipes-engine"
#categoria = ["desayuno","merienda","snack"]
language_default = "es"
categoria = ["comida", "cena"]
app_search = AppSearch(
    myendpoint,
    bearer_auth=mybearer
)

def display_menu_eleccion_comida():
    print("\nMenu Principal:")
    print("1. Comida Cena")
    print("2. Desayuno - Merienda - Snack")
    print("3. Salir")

    choice = input("Ingrese su opción: ")
    return choice

def display_menu_calorias():
    print("Calorias Máximas")
    choice = input("Ingrese su opción: ")
    return choice

def get_query(query):
    
    print (f"Quiere opciones de {query}")
    resp = app_search.search(
    engine_name=my_engine_name,
    body={
        "query": "",
        "filters" : {
            "categoria": [query]
        },
        "page": {
            "size": 5  
        },
        "sort": {
            "kcal": "desc"
        }
    }
    )
    return resp



def main():
    while True:
        choice = display_menu_eleccion_comida()

        if choice == '1':
            query = "comida"
            response = get_query(query)
            response_formatted = pprint.pformat(response)
            response_treated = json.dumps(response.body)
            print(f"Response treated: \n{response_treated}")
            data_json = json.loads(response_treated)
            results = data_json['results']
            for recipe in results:
                print (recipe['titulo']['raw'])
                print (recipe['kcal']['raw'])
        elif choice == '2':
            query = "desayuno"
            response = get_query(query)
            response_formatted = pprint.pformat(response)
            response_treated = json.dumps(response.body)
            print(f"Response treated: \n{response_treated}")
            data_json = json.loads(response_treated)
            results = data_json['results']
            for recipe in results:
                print (recipe['titulo']['raw'])
                print (recipe['kcal']['raw'])
        elif choice == '3':
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    stored_text = ""  # Variable para almacenar el texto ingresado
    main()
