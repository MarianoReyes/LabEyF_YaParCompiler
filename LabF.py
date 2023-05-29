import re
from LR import coleccion_canonica
from LL import primeros, siguientes, get_terminales_no_terminales
from graficar import dibujar_lr0
import pandas as pd
import numpy as np

# toma el nombre del archivo YALP como argumento y devuelve el contenido del archivo como una cadena


def leer_yalp(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content

# toma el contenido del archivo YALP como argumento y devuelve dos secciones separadas de tokens y producciones, eliminando la sección opcional de encabezado


def separar_yalp(content):
    try:
        sections = content.split('%%')
        tokens_section = sections[0]
        productions_section = sections[1]
        return tokens_section, productions_section
    except:
        print("\nNo se encontro el separador '%%' en el archivo yalp.")
        exit()

# procesa la sección de tokens del archivo YALP y devuelve una lista de tokens definidos en esa sección


def procesar_tokens(content):
    tokens = []
    lines = content.split('\n')
    for line in lines:
        if line.startswith("%token"):
            line_tokens = line[len("%token"):].strip().split(' ')
            tokens.extend(line_tokens)
        if not line.startswith("%token") and not line.startswith("IGNORE") and not line.startswith("/*") and line.strip():
            print("\nLos tokens no estan bien definidos.")
            exit()
    return tokens

# procesa la sección de producciones del archivo YALP y devuelve un diccionario que contiene las reglas de producción


def procesar_producciones(content):
    productions = {}
    content = re.sub(r'/\*.*?\*/', '', content,
                     flags=re.DOTALL)  # Eliminar comentarios
    lines = content.split('\n')
    current_production = None
    production_rules = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith(':'):
            if current_production:
                productions[current_production] = production_rules
                production_rules = []
            current_production = line[:-1]
        elif line.endswith(';'):
            line = line[:-1]
            if line != "":
                production_rules.append(line)
            productions[current_production] = production_rules
            production_rules = []
            current_production = None
        else:
            if (line.startswith('|') or line.startswith('->')) and current_production:
                line = line.strip().split('|')
                for item in line:
                    if item.strip() != "":
                        production_rules.append(item.strip())

            elif ('|' in line) and current_production:
                line = line.strip()
                production_rules.extend(line.split('|'))
            else:
                production_rules.append(line)
    return productions

# procesa el archivo completo


def procesar_yalp(filename):
    content = leer_yalp(filename)
    tokens_section, productions_section = separar_yalp(content)
    tokens = procesar_tokens(tokens_section)
    productions = procesar_producciones(productions_section)
    return tokens, productions

#  toma el diccionario de producciones y devuelve una versión modificada del mismo diccionario en la que cada regla de producción se ha convertido en una lista de elementos separados por espacio


def convert_productions(productions_dict):
    converted_productions = {}
    for key, value in productions_dict.items():
        converted_productions[key] = [rule.split() for rule in value]
    return converted_productions

# verifica si los tokens del yalp se encuentran en los tokens del lex


def same_content(tokens_lex, tokens):
    return sorted(tokens_lex) == sorted(tokens)


archivo = input("Ingrese el nombre del archivo a ejecutar: ")

# Abrir y leer el archivo
with open(archivo + ".yal", "r") as f:
    content = f.read()

# Dividir el contenido del archivo en líneas
lines = content.split("\n")

# Buscar la línea que contiene "rule tokens"
rule_tokens_index = None
for i, line in enumerate(lines):
    if re.match(r"^rule tokens = .*?$", line):
        rule_tokens_index = i
        break

# Extraer el contenido de las llaves luego de cada token en las líneas siguientes
tokens_lex = []
if rule_tokens_index is not None:
    for line in lines[rule_tokens_index + 1:]:
        match = re.search(r"\{\s*(.*?)\s*\}", line)
        if match and match.group(1):  # Check if the captured content is not empty
            tokens_lex.append(match.group(1))

tokens, productions_dict = procesar_yalp(archivo + '.yalp')
converted_productions = convert_productions(productions_dict)

print(tokens)
print(tokens_lex)

if same_content(tokens_lex, tokens):
    states, transitions = coleccion_canonica(converted_productions)

    # Imprimir estados y transiciones
    print('\nEstados:')
    for i, state in enumerate(states):
        print(f'{i}: {state}')

    print('\nTransiciones:')
    for transition in transitions:
        print(transition)

    # Funcion para dibujar el automata lr(0)
    dibujar_lr0(states, transitions)

    # Funciones Primero y Siguiente
    print("\nPrimero y Siguiente")

    def convert_productions(productions):
        converted_productions = {}
        for key, value in productions.items():
            converted_productions[key] = [prod.split() for prod in value]
        return converted_productions

    converted_prod = convert_productions(productions_dict)
    first = primeros(converted_prod)
    follow = siguientes(converted_prod, first)

    print("\nConjuntos Primeros:")
    for non_terminal, first_set in first.items():
        print(f"{non_terminal}: {first_set}")

    print("\nConjuntos Siguientes:")
    for non_terminal, follow_set in follow.items():
        print(f"{non_terminal}: {follow_set}")

    # print("\nstates: ", states)
    # print("\ntransitions: ", transitions)

    # LAB F DESDE AQUI

    def generate_slr_tables(states, transitions, productions, first_sets, follow_sets, non_terminals, terminals):
        start_symbol = list(productions.keys())[0]  # Símbolo de inicio

        # Crear tabla de ACCION y tabla de GOTO inicialmente vacías
        action_table = pd.DataFrame(index=range(
            len(states)), columns=terminals, dtype=object)

        goto_table = pd.DataFrame(index=range(len(
            states)), columns=non_terminals, dtype=object)  # Quitar el símbolo de dolar ($)

        # Crear una lista de producciones y un diccionario para mapear las producciones a su índice correspondiente
        production_list = []
        production_index = {}
        for key in productions.keys():
            for value in productions[key]:
                prod = (key, tuple(value))
                production_index[prod] = len(production_list)
                production_list.append(prod)

        # Lista para almacenar los errores
        error_list = []

        def handle_conflict(table, row, col, value):
            if table.loc[row, col] is not None:
                error_list.append(
                    f"Conflicto en ({row}, {col}): Valor actual: {table.loc[row, col]}, Nuevo valor: {value}")
            else:
                table.loc[row, col] = value

        # Rellenar las tablas
        for i, state in enumerate(states):
            for item in state:
                # caso especial para la reducción [S' -> S·]
                if item.production[0] == start_symbol + "'" and item.position == len(item.production[1]):
                    handle_conflict(action_table, i, '$', "ACC")
                # caso para [A -> α·]
                elif item.position == len(item.production[1]):
                    for symbol in follow_sets.get(item.production[0], []):
                        prod = (item.production[0], tuple(item.production[1]))
                        action_table.loc[i,
                                         symbol] = f"R{production_index.get(prod, -1)}"
            for trans in transitions:
                if trans[0] == i:
                    if trans[1] in terminals:  # caso para [A → α·aβ]
                        action_table.loc[i, trans[1]] = f"S{trans[2]}"
                    elif trans[1] in non_terminals:  # caso para ir_A
                        goto_table.loc[i, trans[1]] = trans[2]

        return action_table, goto_table, production_list

    terminals, no_terminals = get_terminales_no_terminales(
        converted_productions)

    # Obtener las tablas de análisis SLR
    action_table, goto_table, production_list = generate_slr_tables(
        states, transitions, converted_productions, first, follow, no_terminals, terminals)

    # Concatenamos las tablas para su impresion
    concatenated_table = pd.concat(
        [action_table, goto_table], axis=1, keys=['ACTION', 'GOTO'])

    # remplazamos NaN con "-"
    concatenated_table = concatenated_table.fillna('-')

    # imprimimos la tabla
    print('\nTABLA DE PARSEO SLR')
    print(concatenated_table)

    #print("\nproductions: ", converted_productions)
    #print("\nterminales: ", terminals)
    #print("\nno erminales: ", no_terminals)

    def parse_slr(input_tokens, action_table, goto_table, production_list):
        parse_stack = [0]  # Pila inicial con el estado 0
        # Agregar fin de entrada al final de input_tokens
        input_tokens.append('$')
        input_index = 0  # Índice para rastrear el token actual en input_tokens

        while True:
            current_state = parse_stack[-1]
            current_token = input_tokens[input_index]
            action = action_table.loc[current_state, current_token]

            if action.startswith('S'):
                # Desplazamiento (shift)
                next_state = int(action[1:])
                parse_stack.append(current_token)
                parse_stack.append(next_state)
                input_index += 1
            elif action.startswith('R'):
                # Reducción (reduce)
                production_num = int(action[1:])
                production = production_list[production_num]
                lhs, rhs = production

                # Desapilar símbolos
                num_symbols = len(rhs)
                parse_stack = parse_stack[:-2 * num_symbols]

                # Obtener el estado actual después de la reducción
                current_state = parse_stack[-1]
                next_state = goto_table.loc[current_state, lhs]

                parse_stack.append(lhs)
                parse_stack.append(next_state)
            elif action == 'ACC':
                # Análisis completado
                print('\nLa cadena de entrada es válida.')
                break
            else:
                # Error sintáctico
                print('\nError sintáctico: la cadena de entrada no es válida.')
                break

    file_path = input("\nQue archivo de texto deseamos evaluar? -> ")

    with open(file_path, 'r') as file:
        content = file.read()
        input_tokens = content.split()  # Dividir el contenido en palabras

    parse_slr(input_tokens, action_table, goto_table, production_list)


else:
    print("Los Tokens del yalp no son iguales a los tokens del lex")
