import re
from tokens import Tokens
from AFNv import *

# variable del archivo
archivo = 'ya.lex'

# creacion de la variable que almacena afns con su nombre
afns = []

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


for token in tokenizer.tokens:
    nombre = token[0]
    regex = token[1]

    trabajador = PostifixToAFN()

    # Aquí creas el AFN correspondiente
    postfix = trabajador.infix_to_postfix(regex)
    print(postfix)
    #afn = trabajador.postfix_to_afn(postfix)
    #afn.nombre = nombre
    # afns.append(afn)
