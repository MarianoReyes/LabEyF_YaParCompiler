
# -*- coding: utf-8 -*-
from Postfix_AFN import PostifixToAFN 
import pickle
import re

# cargar bytes desde archivos binarios
with open('afns.pkl', 'rb') as f:
    afns_bytes = f.read()
with open('afn_final.pkl', 'rb') as f:
    afn_final_bytes = f.read()

# convertir bytes a objetos
afns = pickle.loads(afns_bytes)
afn_final = pickle.loads(afn_final_bytes)

palabras = []
archivo = input("Ingrese el nombre del archivo a resolver:\n--> ") 

with open(archivo, 'r') as f:
    contenido = f.read()
    
    # Utilizamos una expresión regular para hacer el split
    patron = re.compile(r'"[^"]*"|\S+')
    palabras = patron.findall(contenido)


def reemplazar_espacios(value):
    value = value.replace(' ', ',')
    return value


resultado_verificaciones = []
for palabra in palabras:
    palabra = reemplazar_espacios(palabra)
    valor = afn_final.simular_cadena(palabra)
    try:
        if valor == False:
            resultado_verificaciones.append(
                "'" + palabra + "'" + " --> No se reconoce")
        if valor[0] == True:
            for afn in afns:
                if valor[1] in afn[1].ef:
                    resultado_verificaciones.append(
                        "'" + palabra + "'" + " --> " + str(afn[0][0]).upper())
                    break
    except:
        pass

new_archivo = input("\nIngrese el nombre del archivo nuevo:\n--> ") 
# Escribir el resultado en el .txt
with open(new_archivo, 'w') as f:
    f.write(contenido)
    f.write('\n\n')
    for resultado in resultado_verificaciones:
        f.write(resultado)
        f.write('\n')

print("\nArchivo resuelto con exito")
