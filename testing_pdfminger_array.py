#!/usr/bin/env python
import pdfminer.high_level
import pdfminer.layout
import hashlib
import io
import os
from elastic_enterprise_search import AppSearch
from elastic_enterprise_search.exceptions import NotFoundError  # Corrected import
import json
import re
from elasticsearch import Elasticsearch
from zulu import Zulu

myendpoint = "http://localhost:3002"
mybearer = "private-ysf3m7f6o2bzxpn7mhj8g22z"
my_engine_name = "new-es-testing-recipes-engine"
categoria_desayuno = ["desayuno","merienda","snack"]
language_default = "es"
categoria_comida = ["comida", "cena"]
app_search = AppSearch(
    myendpoint,
    bearer_auth=mybearer
)
hash_algorithm = hashlib.sha256  # Choose your desired hash algorithm
try:
    engine_exists = app_search.get_engine(engine_name=my_engine_name)
except NotFoundError as e:
    app_search.create_engine(
        engine_name=my_engine_name,
        language=language_default,
    )
try: 
    response = app_search.list_engines()
    print (response)
except NotFoundError as e:
    print ("no hay engines")
try:
    response = app_search.put_schema(
        engine_name=my_engine_name,
        schema={
            "kcal": "number",
            "proteina_gr": "number",
            "carbohidrato_gr": "number",
            "grasas_gr": "number",
            "ingestion_date": "date"
        }
    )
except NotFoundError as e:
    print ("No se pudo actualizar el schema")
try:
    response = app_search.put_synonym_set(
        engine_name=my_engine_name,
        synonym_set_id=1,
        synonyms=   [
            "atún",
            "bonito"
        ]
    )
    print(response)
except NotFoundError as e:
    print ("no se pudo cargar el sinónimo")
# Ruta del archivo PDF
rutas_pdf = [
    "/Users/fucho/CT-App/docker-elk/ct_testing/solo_desayuno_merienda_snack.pdf",
    "/Users/fucho/CT-App/docker-elk/ct_testing/recetas_comidas_y_cena.pdf" 
]
desayuno_ruta_pdf = "/Users/fucho/CT-App/docker-elk/ct_testing/solo_desayuno_merienda_snack.pdf"
comida_ruta_pdf = "/Users/fucho/CT-App/docker-elk/ct_testing/recetas_comidas_y_cena.pdf"
my_documents = []
with open(desayuno_ruta_pdf, 'rb') as f:
    extracted_pages = pdfminer.high_level.extract_pages(f)

    for page_number, page in enumerate(extracted_pages):
        cont = 0
        for element in page:
            aux = isinstance(element, pdfminer.layout.LTTextBox)
            if aux:
               match cont:
                   case 0:
                        titulo_extraido = element.get_text()
                   case 2:
                        ingredientes_extraido = element.get_text()
                   case 4:
                        preparacion_extraido = element.get_text()
                   case 5:
                        aux1 = element.get_text()
                        if re.match("^CALOR", aux1):
                            informacion_extraido = element.get_text()
                            pattern1 = r"Recuerda que puedes cambiar cantidades para ajustarlo a tus calor\u00edas y macronutrientes\."
                            modified_text = re.sub(pattern1, "", informacion_extraido)

                        else:
                            preparacion_extraido = preparacion_extraido + aux1

                   case 6:
                       informacion_extraido = element.get_text()
                       pattern1 = r"Recuerda que puedes cambiar cantidades para ajustarlo a tus calor\u00edas y macronutrientes\."
                       modified_text = re.sub(pattern1, "", informacion_extraido)
                       
            cont = cont + 1                       

        # print (f"titulo: {titulo_extraido}")
        # print (f"ingredientes: {ingredientes_extraido}")
        # print (f"preparacion: {preparacion_extraido}")
        # print (f"informacion nutricional: {informacion_extraido}")
        info_macros = {}
        # print (modified_text)
        if modified_text:
            pattern2 = r"\s*(?P<calorias>\d+)KCAL\s+CH:\s+(?P<carbohidratos>\d+)G\s+P:\s+(?P<proteinas>\d+)G\s+G:\s+(?P<grasas>\d+)G\s*"
            match = re.search(pattern2, modified_text)
            # print (match)
            if match:
                # print (match.group("calorias"))
                calorias_metrica = int(match.group("calorias"))
                carbohidrato_metrica = int(match.group("carbohidratos"))
                proteina_metrica = int(match.group("proteinas"))
                grasa_metrica = int(match.group("grasas"))
                info_macros["carbohidratos"] = carbohidrato_metrica
                info_macros["proteinas"] = proteina_metrica
                info_macros["grasas"] = grasa_metrica
                # print("Valores extraídos:")
                # print(f"Calorías: {calorias_metrica}")
                # print(f"Carbohidratos: {carbohidrato_metrica}")
                # print(f"Proteínas: {proteina_metrica}")
                # print(f"Grasas: {grasa_metrica}")
            else:
                print("No se pudo extraer la información nutricional.")
        if info_macros and calorias_metrica:
            # Crear documento JSON con la información extraída
            timestamp_utc = Zulu.now()
            #print(f"titulo extraido: {titulo_extraido}")
            #print(f"ingredientes extraido: {ingredientes_extraido}")
            datos_json = {}
            datos_json["id"] = hashlib.sha256(titulo_extraido.encode('utf-8')).hexdigest()
            datos_json["titulo"] = titulo_extraido
            datos_json["ingredientes"] = ingredientes_extraido
            datos_json["preparacion"]= preparacion_extraido
            datos_json["informacion"] = modified_text
            datos_json["kcal"] = calorias_metrica
            datos_json["macronutrientes"] = info_macros
            datos_json["proteina_gr"] = proteina_metrica
            datos_json["carbohidrato_gr"] = carbohidrato_metrica
            datos_json["grasas_gr"] = grasa_metrica
            datos_json["categoria"] = categoria_desayuno
            #datos_json.append(categoria)
            datos_json["ingestion_date"] = timestamp_utc.isoformat() 
            # documento = {
            #     "id": hashlib.sha256(titulo_extraido.encode('utf-8')).hexdigest(),
            #     "titulo": titulo_extraido,
            #     "ingredientes": ingredientes_extraido,
            #     "preparacion": preparacion_extraido,
            #     "informacion": modified_text,
            #     "kcal": calorias_metrica,
            #     "macronutrientes": info_macros,
            #     "proteina_gr": proteina_metrica,
            #     "carbohidrato_gr": carbohidrato_metrica,
            #     "grasas_gr": grasa_metrica,
            #     "categoria": categoria,
            #     "ingestion_date": timestamp_utc.isoformat()
            #     }
           # **Quitar las triples comillas de las cadenas JSON**
            datos_json["titulo"] = datos_json["titulo"].strip('"')  # Eliminar comillas iniciales y finales
            datos_json["ingredientes"] = datos_json["ingredientes"].strip('"')  # Eliminar comillas iniciales y finales
            datos_json["preparacion"] = datos_json["preparacion"].strip('"')  # Eliminar comillas iniciales y finales
            datos_json["informacion"] = datos_json["informacion"].strip('"')  # Eliminar comillas iniciales y finales
 
            documento_json_formatted = json.dumps(datos_json, indent=4)
        
            #print (documento_json_formatted)
            documento = json.loads(documento_json_formatted)
            
            #print (documento)
            if len(my_documents) > 10:
                response = app_search.index_documents(engine_name=my_engine_name, documents =my_documents)
                print (response)
                my_documents.clear()
            else:
                my_documents.append(documento)

with open(comida_ruta_pdf, 'rb') as f:
    extracted_pages = pdfminer.high_level.extract_pages(f)

    for page_number, page in enumerate(extracted_pages):
        cont = 0
        for element in page:
            aux = isinstance(element, pdfminer.layout.LTTextBox)
            if aux:
               match cont:
                   case 0:
                        titulo_extraido = element.get_text()
                   case 2:
                        ingredientes_extraido = element.get_text()
                   case 4:
                        preparacion_extraido = element.get_text()
                   case 5:
                        aux1 = element.get_text()
                        if re.match("^CALOR", aux1):
                            informacion_extraido = element.get_text()
                            pattern1 = r"Recuerda que puedes cambiar cantidades para ajustarlo a tus calor\u00edas y macronutrientes\."
                            modified_text = re.sub(pattern1, "", informacion_extraido)

                        else:
                            preparacion_extraido = preparacion_extraido + aux1

                   case 6:
                       informacion_extraido = element.get_text()
                       pattern1 = r"Recuerda que puedes cambiar cantidades para ajustarlo a tus calor\u00edas y macronutrientes\."
                       modified_text = re.sub(pattern1, "", informacion_extraido)
                       
            cont = cont + 1                       

        # print (f"titulo: {titulo_extraido}")
        # print (f"ingredientes: {ingredientes_extraido}")
        # print (f"preparacion: {preparacion_extraido}")
        # print (f"informacion nutricional: {informacion_extraido}")
        info_macros = {}
        # print (modified_text)
        if modified_text:
            pattern2 = r"\s*(?P<calorias>\d+)KCAL\s+CH:\s+(?P<carbohidratos>\d+)G\s+P:\s+(?P<proteinas>\d+)G\s+G:\s+(?P<grasas>\d+)G\s*"
            match = re.search(pattern2, modified_text)
            # print (match)
            if match:
                # print (match.group("calorias"))
                calorias_metrica = int(match.group("calorias"))
                carbohidrato_metrica = int(match.group("carbohidratos"))
                proteina_metrica = int(match.group("proteinas"))
                grasa_metrica = int(match.group("grasas"))
                info_macros["carbohidratos"] = carbohidrato_metrica
                info_macros["proteinas"] = proteina_metrica
                info_macros["grasas"] = grasa_metrica
                # print("Valores extraídos:")
                # print(f"Calorías: {calorias_metrica}")
                # print(f"Carbohidratos: {carbohidrato_metrica}")
                # print(f"Proteínas: {proteina_metrica}")
                # print(f"Grasas: {grasa_metrica}")
            else:
                print("No se pudo extraer la información nutricional.")
        if info_macros and calorias_metrica:
            # Crear documento JSON con la información extraída
            timestamp_utc = Zulu.now()
            #print(f"titulo extraido: {titulo_extraido}")
            #print(f"ingredientes extraido: {ingredientes_extraido}")
            datos_json = {}
            datos_json["id"] = hashlib.sha256(titulo_extraido.encode('utf-8')).hexdigest()
            datos_json["titulo"] = titulo_extraido
            datos_json["ingredientes"] = ingredientes_extraido
            datos_json["preparacion"]= preparacion_extraido
            datos_json["informacion"] = modified_text
            datos_json["kcal"] = calorias_metrica
            datos_json["macronutrientes"] = info_macros
            datos_json["proteina_gr"] = proteina_metrica
            datos_json["carbohidrato_gr"] = carbohidrato_metrica
            datos_json["grasas_gr"] = grasa_metrica
            datos_json["categoria"] = categoria_comida
            #datos_json.append(categoria)
            datos_json["ingestion_date"] = timestamp_utc.isoformat() 
            # documento = {
            #     "id": hashlib.sha256(titulo_extraido.encode('utf-8')).hexdigest(),
            #     "titulo": titulo_extraido,
            #     "ingredientes": ingredientes_extraido,
            #     "preparacion": preparacion_extraido,
            #     "informacion": modified_text,
            #     "kcal": calorias_metrica,
            #     "macronutrientes": info_macros,
            #     "proteina_gr": proteina_metrica,
            #     "carbohidrato_gr": carbohidrato_metrica,
            #     "grasas_gr": grasa_metrica,
            #     "categoria": categoria,
            #     "ingestion_date": timestamp_utc.isoformat()
            #     }
           # **Quitar las triples comillas de las cadenas JSON**
            datos_json["titulo"] = datos_json["titulo"].strip('"')  # Eliminar comillas iniciales y finales
            datos_json["ingredientes"] = datos_json["ingredientes"].strip('"')  # Eliminar comillas iniciales y finales
            datos_json["preparacion"] = datos_json["preparacion"].strip('"')  # Eliminar comillas iniciales y finales
            datos_json["informacion"] = datos_json["informacion"].strip('"')  # Eliminar comillas iniciales y finales
 
            documento_json_formatted = json.dumps(datos_json, indent=4)
        
            #print (documento_json_formatted)
            documento = json.loads(documento_json_formatted)
            
            #print (documento)
            if len(my_documents) > 10:
                response = app_search.index_documents(engine_name=my_engine_name, documents =my_documents)
                print (response)
                my_documents.clear()
            else:
                my_documents.append(documento)

