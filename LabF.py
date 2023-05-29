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
        tokens_lex.extend(re.findall(r"\{\s*(.+?)\s*\}", line))

tokens, productions_dict = procesar_yalp(archivo + '.yalp')
converted_productions = convert_productions(productions_dict)

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
    # print("\nproductions: ", converted_productions)

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

        # Rellenar las tablas
        for i, state in enumerate(states):
            for item in state:
                # caso especial para la reducción [S' -> S·]
                if item.production[0] == start_symbol + "'" and item.position == len(item.production[1]):
                    action_table.loc[i, '$'] = "ACC"
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

        return action_table, goto_table

    terminals, no_terminals = get_terminales_no_terminales(
        converted_productions)

    # Obtener las tablas de análisis SLR
    action_table, goto_table = generate_slr_tables(
        states, transitions, converted_productions, first, follow, no_terminals, terminals)

    # Concatenamos las tablas para su impresion
    concatenated_table = pd.concat(
        [action_table, goto_table], axis=1, keys=['ACTION', 'GOTO'])

    # remplazamos NaN con "-"
    concatenated_table = concatenated_table.fillna('-')

    # imprimimos la tabla
    print('\nTABLA DE PARSEO SLR')
    print(concatenated_table)

    def parse_input(input_file, action_table, goto_table):
        # Read the input file
        with open(input_file, 'r') as file:
            input_string = file.readline().strip()  # Read the first line

        # Create an empty stack for parsing
        stack = [0]

        # Add end of input symbol ('$') to the input string
        input_string += '$'

        # Start parsing
        while True:
            # Get the current state from the top of the stack
            current_state = stack[-1]

            # Get the next input symbol
            next_symbol = input_string[0]

            # Get the action from the action table
            action = action_table.loc[current_state, next_symbol]

            if action.startswith('S'):
                # Shift: Move to the next state
                next_state = int(action[2:])
                stack.append(next_state)
                input_string = input_string[1:]  # Consume the input symbol

            elif action.startswith('R'):
                # Reduce: Apply the production
                production_index = int(action[2:])
                production = production_list[production_index]

                # Get the non-terminal and production length
                non_terminal, production_length = production

                # Pop the production symbols from the stack
                stack = stack[:-production_length]

                # Get the new current state from the top of the stack
                current_state = stack[-1]

                # Get the goto state from the goto table
                goto_state = goto_table.loc[current_state, non_terminal]

                # Push the non-terminal and goto state to the stack
                stack.append(non_terminal)
                stack.append(goto_state)

            elif action == 'ACCEPT':
                # Input string has been successfully parsed
                print('Input string is valid!')
                break

            else:
                # Error: Invalid input
                print('Invalid input string!')
                break

    # Define the production_list (list of productions)
    production_list = []

    # Call the parse_input function with the input file and the action and goto tables
    parse_input('input.txt', action_table, goto_table)


else:
    print("Los Tokens del yalp no son iguales a los tokens del lex")
