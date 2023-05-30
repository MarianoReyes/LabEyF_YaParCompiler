
# -*- coding: utf-8 -*-
import pickle
import re
    
with open('action_table.pkl', 'rb') as f:
    action_table_bytes = f.read()
with open('goto_table.pkl', 'rb') as f:
    goto_table_bytes = f.read()
with open('production_list.pkl', 'rb') as f:
    production_list_bytes = f.read()

# convertir bytes a objetos
action_table = pickle.loads(action_table_bytes)
goto_table = pickle.loads(goto_table_bytes)
production_list = pickle.loads(production_list_bytes)

def parse_slr(input_tokens, action_table, goto_table, production_list):
    parse_stack = [0]  # Pila inicial con el estado 0
    # Agregar fin de entrada al final de input_tokens
    input_tokens.append('$')
    input_index = 0  # Índice para rastrear el token actual en input_tokens

    while True:
        try:
            current_state = parse_stack[-1]
            current_token = input_tokens[input_index]
            action = action_table.loc[current_state, current_token]
        except:
            print("\nError por TOKEN en la cadena analizada")
            break

        print("current state:", current_state, "-> current token:",
                current_token, "-> action:", action)

        try:

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
                # Analisis completado
                print('\nLa cadena de entrada es valida.')
                break
            else:
                # Error sintactico
                print('\nError sintactico: la cadena de entrada no es valida.')
                break
        except:
            print("\nError al momento de realizar el parseo de la entrada.")
            break

file_path = input("\nQue archivo de texto deseamos evaluar? -> ")

with open(file_path, 'r') as file:
    content = file.read()
    input_tokens = content.split()  # Dividir el contenido en palabras

parse_slr(input_tokens, action_table, goto_table, production_list)
    