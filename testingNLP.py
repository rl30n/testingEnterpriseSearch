import spacy



spacy.download("es_core_news_sm")

# Cargar modelo
nlp = spacy.load("es_core_news_sm")

# Procesar el texto
texto = "Preparé una ensalada con lechuga, tomate, cebolla, pepino y aceite de oliva."
doc = nlp(texto)

# Extraer entidades
ingredientes = []
for ent in doc.ents:
    if ent.label_ == "Ingrediente":
        ingredientes.append(ent.text)

# Visualizar resultados
print("Ingredientes encontrados:", ingredientes)
