from elastic_enterprise_search import AppSearch
from elastic_enterprise_search.exceptions import NotFoundError  # Corrected import
import json
import re
from elasticsearch import Elasticsearch
import pprint
from zulu import Zulu
import logging
import ecs_logging
import traceback
import mylib


myendpoint = "http://localhost:3002"
mybearer = "search-4rvs2psvvgnyjjoimjzq1cfa"
my_engine_name = "new-es-testing-recipes-engine"
#categoria = ["desayuno","merienda","snack"]
language_default = "es"
categoria = ["comida", "cena"]
app_search = AppSearch(
    myendpoint,
    bearer_auth=mybearer
)
default_page_size = 10
def print_menu_inicio():
    print("\tMenú Inicial")
    print("\t\t1.\tRealizar Búsqueda")
    print("\t\t2.\tSugerencias para comidas")

def print_menu():
    print("\t**Menú de Comidas**")

def get_first_choice():
    while True:
        try:
            first_choice = int(input("Ingrese su opción: "))
            if first_choice == 1 or first_choice == 2 or first_choice == 3:
                return first_choice
            else:
                print("Opción no valida")
        except ValueError:
            print("Entrada no válida. Debe ingresar un número entero.")

def get_meal_choice():
    while True:
        try:
            meal_choice = int(input("Ingrese su elección (1 para Comida-Cena, 2 para Desayuno-snack-merienda, 3 Salir): "))
            if meal_choice == 1 or meal_choice == 2 or meal_choice == 3:
                return meal_choice
            else:
                print("Opción no válida. Intente de nuevo.")
        except ValueError:
            print("Entrada no válida. Debe ingresar un número entero (1 o 2).")

def get_calorie_limit():
    while True:
        try:
            calorie_limit = int(input("Ingrese el límite máximo de calorías: "))
            if calorie_limit >= 0:
                return calorie_limit
            else:
                print("Límite de calorías no válido. Debe ser un número positivo.")
        except ValueError:
            print("Entrada no válida. Debe ingresar un número entero.")

def get_page_size():
    while True:
        try:
            page_size_limit = int(input("Ingrese el número máximo de recetas a recuperar "))
            if page_size_limit >= 0:
                return page_size_limit
            else:
                print("Límite de resultados no válido. Debe ser un número positivo.")
        except ValueError:
            print("Entrada no válida. Debe ingresar un número entero.")
def simple_query_choice():
    query =input("\t¿Qué quieres comer?: \t")
    return query

def get_simple_query(query):
    # print (f"Quiere recetas de {query}")
    # print(type(query))
    resp = app_search.search(
    engine_name=my_engine_name,
    search_fields={
        "titulo":{},
        "preparacion":{},
        "ingredientes": {}
    },
    query=query,
    page_size=default_page_size,
    sort={
        "kcal": "desc"
    }
    )
    return resp 

def get_suggested_meals_query(query,calorie_limit,page_size_limit):
    
    print (f"\tQuiere opciones de {query} de {calorie_limit} calorías max")
    cal_int = int(calorie_limit)
    resp = app_search.search(
    engine_name=my_engine_name,
    query=query,
    filters={
        "all": [
                { "categoria": [query]},
                {"kcal": {"to": cal_int}}
            ]
    },
    page_size=page_size_limit,
    sort={
            "kcal": "desc"
    }
    )
    return resp

def printing_results(results):
    for recipe in results:
        print("************************")
        print (recipe['titulo']['raw'])
        print("************************")
        print (f"\tCalorias: {recipe['kcal']['raw']}")
        print ("\n\n")
        print (recipe['ingredientes']['raw'])
        print ("\n\n")
        print (recipe['preparacion']['raw']) 
        print ("\n\n")
        print("-------------------------")
def main():
    # logging.basicConfig(filename='myapp.log', level=logging.INFO)
    # logger.('Started')
    # mylib.do_something()
    # logger.info('Finished')
    while True:
        print_menu_inicio()
        first_choice = get_first_choice()
        if first_choice == 3:
           print("Saliendo")
           exit()
        if first_choice == 2:
            print_menu()
            meal_choice = get_meal_choice()
            if meal_choice == 3:
                print("Saliendo")
                exit()
            calorie_limit = get_calorie_limit()
            page_size_limit = get_page_size()
            print (f"Comida elegida: {meal_choice}")
            print (f"Maximo calorias: {calorie_limit}")
            # Simulate recipe details based on meal choice
            if meal_choice == 1:
                query = "comida"
                response = get_suggested_meals_query(query,calorie_limit,page_size_limit)
                response_formatted = pprint.pformat(response)
                response_treated = json.dumps(response.body)
                #print(f"Response treated: \n{response_treated}")
                data_json = json.loads(response_treated)
                results = data_json['results']
                printing_results(results)
            if meal_choice == 2:
                query = "desayuno"
                response = get_suggested_meals_query(query,calorie_limit,page_size_limit)
                response_formatted = pprint.pformat(response)
                response_treated = json.dumps(response.body)
                #print(f"Response treated: \n{response_treated}")
                data_json = json.loads(response_treated)
                results = data_json['results']
                printing_results(results)
            if meal_choice == 3:
                print("Saliendo")
                exit()
        if first_choice == 1:
            query = simple_query_choice()
            query_str = str(query)
            response = get_simple_query(query_str)
            response_treated = json.dumps(response.body)
            #print(f"Response treated: \n{response_treated}")
            data_json = json.loads(response_treated)
            results = data_json['results']
            printing_results(results) 

        choice = input("\n¿Desea continuar? (s/n): ")
        if choice.lower() != 's':
            break

if __name__ == "__main__":
    main()
