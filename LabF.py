import re
from LR import coleccion_canonica
from LL import primeros, siguientes
from graficar import dibujar_lr0

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

    print("\nstates: ", states)
    print("\ntransitions: ", transitions)

    print("\nproductions: ", converted_productions)

    # LAB F DESDE AQUI

    def generate_slr_tables(states, transitions, productions):
        # Inicializar ACTION y GOTO tables
        action_table = {}
        goto_table = {}

        # Convertir el conjunto de estados en una lista ordenada
        ordered_states = sorted(states)

        for state in ordered_states:
            action_table[state] = {}
            goto_table[state] = {}

        # Rellenar las tablas ACTION y GOTO
        for state in states:
            for item in state:
                production = item.production
                position = item.position

                # Caso 1: Item completo (punto al final)
                if position == len(production[1]):
                    if production[0] == 'expression' and item.derived:
                        # Caso especial para la producción inicial
                        action_table[state]['$'] = 'accept'
                    else:
                        # Reducción (R)
                        follow_symbols = siguientes(productions, production[0])
                        for symbol in follow_symbols:
                            action_table[state][symbol] = 'R' + \
                                str(productions.index(production))

                else:
                    symbol = production[1][position]

                    # Caso 2: Transición a estado con GOTO (SHIFT)
                    if (state, symbol) in transitions:
                        next_state = transitions[(state, symbol)]
                        goto_table[state][symbol] = next_state

                    # Caso 3: Desplazamiento (SHIFT)
                    elif symbol.isalpha() or symbol.isnumeric():
                        next_state = state + 1  # Suponiendo que los estados se numeran secuencialmente
                        action_table[state][symbol] = 'S' + str(next_state)

        return action_table, goto_table

    # Obtener las tablas de análisis SLR
    action_table, goto_table = generate_slr_tables(
        states, transitions, converted_productions)

    # Imprimir las tablas
    print("ACTION table:")
    for state, actions in action_table.items():
        print(state)
        for symbol, action in actions.items():
            print(f"{symbol}: {action}")
        print()

    print("GOTO table:")
    for state, gotos in goto_table.items():
        print(state)
        for symbol, goto in gotos.items():
            print(f"{symbol}: {goto}")
        print()


else:
    print("Los Tokens del yalp no son iguales a los tokens del lex")
