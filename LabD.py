import pickle
import re
from tokens import Tokens
from Regex_Postfix import convertExpression
from Postfix_AFN import PostifixToAFN

# variable del archivo
archivo = input("Ingrese el archivo lex:\n--> ")

# creacion de la variable que almacena afns con su nombre
afns = []

print("\nCreando tokens...")

# a los tokens del archivo los covertimos en arreglo
tokenizer = Tokens()
tokenizer.getTokens(archivo)

for i in range(len(tokenizer.tokens)):
    for j in range(len(tokenizer.tokens)):
        if i != j and tokenizer.tokens[i][0] in tokenizer.tokens[j][1]:
            tokenizer.tokens[i] = (
                tokenizer.tokens[i][0], tokenizer.tokens[i][1], True)
            break
        else:
            tokenizer.tokens[i] = (
                tokenizer.tokens[i][0], tokenizer.tokens[i][1], False)

counter = -1
errores = 0

print("\nCreando afns...")

# por cada token en tokens creamos un afn si es simple
for i, token in enumerate(tokenizer.tokens):
    if token[2] == True:
        try:
            # Creamos el automata a partir de la expresión regular
            conversion = convertExpression(len(token[1]))

            # llamada de funcion para convertir a postfix
            conversion.RegexToPostfix(token[1])
            if conversion.ver == True:
                postfix = conversion.res

                # instancia de clase para convertir a AFN
                afn = PostifixToAFN(postfix=postfix, counter=counter)

                # llamada a metodo para convertir afn
                afn.conversion(token[0])

                counter = afn.counter
                afns.append((token, afn))

                if afn.error:
                    errores += 1

        except:
            print('\nNo podemos generar ese afn aun')

new_tokens = []

for i, token in enumerate(tokenizer.tokens):
    if token[2]:
        new_tokens.append((token[0], token[1], token[2]))
    if not token[2]:
        operands_operators = []
        regex_splitted = re.findall('\w+|[?()|\-=@#%+*"]', token[1])
        operands_operators.extend(regex_splitted)

        for i, element in enumerate(operands_operators):
            for afn in afns:
                if element == afn[0][0]:
                    operands_operators[i] = "("+afn[0][1]+")"
        new_regex = ''.join(operands_operators)

        new_tokens.append((token[0], new_regex, token[2]))


# por cada token compuesto en tokens creamos un afn
for i, token in enumerate(new_tokens):
    if token[2] == False:
        try:
            # Creamos el automata a partir de la expresión regular
            conversion = convertExpression(len(token[1]))

            # llamada de funcion para convertir a postfix
            conversion.RegexToPostfix(token[1])
            if conversion.ver == True:
                postfix = conversion.res

                # instancia de clase para convertir a AFN
                afn = PostifixToAFN(postfix=postfix, counter=counter)

                # llamada a metodo para convertir afn
                afn.conversion(token[0])

                counter = afn.counter
                afns.append((token, afn))

                if afn.error:
                    errores += 1

        except:
            print('\nNo podemos generar ese afn aun')

print("\nAfns listos...")

solo_afns = []
for afn in afns:
    solo_afns.append(afn[1])

# instancia de clase para convertir a AFN
afn_final = PostifixToAFN(counter=counter, afns=solo_afns)

# llamada a metodo para unir a todos los afns y graficarlos
if errores == 0:
    afn_final.union_afns("afn_grafico_mega_automata")
    counter = afn_final.counter
else:
    print("\nNo se genera el mega autómata porque 1 o más autómatas no se pudo generar.")
    exit()

# LAB D DESDE AQUI


# convertir objetos a bytes
afns_bytes = pickle.dumps(afns)
afn_final_bytes = pickle.dumps(afn_final)

# guardar bytes en archivos binarios
with open('afns.pkl', 'wb') as f:
    f.write(afns_bytes)
with open('afn_final.pkl', 'wb') as f:
    f.write(afn_final_bytes)


imports = '''
# -*- coding: utf-8 -*-
from Postfix_AFN import PostifixToAFN 
import pickle
import re
'''
codigo = '''
# cargar bytes desde archivos binarios
with open('afns.pkl', 'rb') as f:
    afns_bytes = f.read()
with open('afn_final.pkl', 'rb') as f:
    afn_final_bytes = f.read()

# convertir bytes a objetos
afns = pickle.loads(afns_bytes)
afn_final = pickle.loads(afn_final_bytes)

palabras = []
archivo = input("Ingrese el nombre del archivo a resolver:\\n--> ") 

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

new_archivo = input("\\nIngrese el nombre del archivo nuevo:\\n--> ") 
# Escribir el resultado en el .txt
with open(new_archivo, 'w') as f:
    f.write(contenido)
    f.write('\\n\\n')
    for resultado in resultado_verificaciones:
        f.write(resultado)
        f.write('\\n')

print("\\nArchivo resuelto con exito")
'''
with open('compilado.py', 'w') as archivo:
    archivo.write(imports)
    archivo.write(codigo)
