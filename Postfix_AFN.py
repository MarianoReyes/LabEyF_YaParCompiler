'''
Postfix a AFN
'''

from re import S
import re
import pandas as pd
from graphviz import Digraph


class PostifixToAFN():
    def __init__(self, postfix=None, counter=None, afns=None):
        self.postfix = postfix
        self.estados = []
        self.estados_list = []
        self.e0 = None
        self.ef = []
        self.transiciones = []
        self.transiciones_splited = []
        self.simbolos = []
        self.afn_final = []
        self.error = False
        self.counter = counter
        self.afns = afns

    def union_afns(self, nombre):
        print("\nJuntando todos los AFNs...")
        self.counter = self.counter+1
        self.e0 = self.counter
        for afn in self.afns:
            self.ef.append(afn.ef[0])
            self.transiciones_splited = self.transiciones_splited + afn.transiciones_splited
            self.estados = self.estados + afn.estados
            self.transiciones_splited.append([self.e0, "ε", afn.e0])

        dot = Digraph()
        for estado in self.estados:
            if estado in self.ef:
                dot.node(str(estado), shape="doublecircle")
            else:
                dot.node(str(estado), shape="circle")
        for transicion in self.transiciones_splited:
            if transicion[1] == "ε":
                dot.edge(str(transicion[0]), str(transicion[2]), label="ε")
            else:
                dot.edge(str(transicion[0]), str(
                    transicion[2]), label=transicion[1])
        dot.render(nombre, format='png', view=True)
        print("\nMega_Autómata listo.")

    # Método para graficar un AFN
    def graficar(self, nombre):
        dot = Digraph()
        for estado in self.estados:
            if estado in self.ef:
                dot.node(str(estado), shape="doublecircle")
            else:
                dot.node(str(estado), shape="circle")
        for transicion in self.transiciones_splited:
            if transicion[1] == "ε":
                dot.edge(str(transicion[0]), str(transicion[2]), label="ε")
            else:
                dot.edge(str(transicion[0]), str(
                    transicion[2]), label=transicion[1])
        dot.render(nombre, format='png', view=True)

    def operando(self, caracter):
        operandos_validos = ['ε', '-', '=', '.', '^', '+', '*', '"', ',']
        if caracter.isalpha() or caracter.isnumeric() or caracter in operandos_validos:
            return True
        else:
            return False

    def reemplazar_interrogacion(self):
        self.postfix = self.postfix.replace('?', 'ε?')

    def conversion(self, indice):
        self.reemplazar_interrogacion()
        print(self.postfix)
        simbolos = []
        postfix = self.postfix
        for i in postfix:
            if self.operando(i):
                if i not in simbolos:
                    simbolos.append(i)

        self.simbolos = sorted(simbolos)

        stack = []
        start = self.counter+1
        end = self.counter+2

        c1 = self.counter+1
        c2 = self.counter+1

        # implementation del algoritmo de thompson

        for i in postfix:
            # si es un simbolo
            if i in simbolos:
                self.counter = self.counter+1
                c1 = self.counter
                if c1 not in self.estados:
                    self.estados.append(c1)
                self.counter = self.counter+1
                c2 = self.counter
                if c2 not in self.estados:
                    self.estados.append(c2)
                self.afn_final.append({})
                self.afn_final.append({})
                stack.append([c1, c2])
                #self.afn_final[c1][i] = c2
                self.transiciones_splited.append([c1, i, c2])
            # si es un kleene
            elif i == '@':
                try:
                    r1, r2 = stack.pop()
                    self.counter = self.counter+1
                    c1 = self.counter
                    if c1 not in self.estados:
                        self.estados.append(c1)
                    self.counter = self.counter+1
                    c2 = self.counter
                    if c2 not in self.estados:
                        self.estados.append(c2)
                    self.afn_final.append({})
                    self.afn_final.append({})
                    stack.append([c1, c2])
                    #self.afn_final[r2]['ε'] = (r1, c2)
                    #self.afn_final[c1]['ε'] = (r1, c2)
                    if start == r1:
                        start = c1
                    if end == r2:
                        end = c2
                    self.transiciones_splited.append([r2, "ε", r1])
                    self.transiciones_splited.append([r2, "ε", c2])
                    self.transiciones_splited.append([c1, "ε", r1])
                    self.transiciones_splited.append([c1, "ε", c2])
                except:
                    self.error = True
                    print("\nExpresión Regex inválida, * mal aplicado")
            # si es una cerradura positiva
            elif i == '#':
                try:
                    r1, r2 = stack.pop()
                    self.counter = self.counter+1
                    c1 = self.counter
                    if c1 not in self.estados:
                        self.estados.append(c1)
                    self.counter = self.counter+1
                    c2 = self.counter
                    if c2 not in self.estados:
                        self.estados.append(c2)
                    # self.afn_final.append({})
                    # self.afn_final.append({})
                    stack.append([c1, c2])
                    self.afn_final[r2]['ε'] = (r1, c2)
                    if start == r1:
                        start = c1
                    if end == r2:
                        end = c2
                    self.transiciones_splited.append([r2, "ε", r1])
                    self.transiciones_splited.append([r2, "ε", c2])
                    self.transiciones_splited.append([c1, "ε", r1])
                except:
                    self.error = True
                    print("\nExpresión Regex inválida, + mal aplicado")

            # si es una concatenacion
            elif i == '%':
                try:
                    r11, r12 = stack.pop()
                    r21, r22 = stack.pop()
                    stack.append([r21, r12])
                    #self.afn_final[r22]['ε'] = r11
                    if start == r11:
                        start = r21
                    if end == r22:
                        end = r12
                    self.transiciones_splited.append([r22, "ε", r11])

                except:
                    self.error = True
                    print(
                        "\nExpresión Regex inválida, concatenación mal aplicada o operando inválido.")
            # si es un or
            elif i == "|":
                try:
                    self.counter = self.counter+1
                    c1 = self.counter
                    if c1 not in self.estados:
                        self.estados.append(c1)
                    self.counter = self.counter+1
                    c2 = self.counter
                    if c2 not in self.estados:
                        self.estados.append(c2)
                    self.afn_final.append({})
                    self.afn_final.append({})

                    r11, r12 = stack.pop()
                    r21, r22 = stack.pop()
                    stack.append([c1, c2])
                    #self.afn_final[c1]['ε'] = (r21, r11)
                    #self.afn_final[r12]['ε'] = c2
                    #self.afn_final[r22]['ε'] = c2
                    if start == r11 or start == r21:
                        start = c1
                    if end == r22 or end == r12:
                        end = c2
                    self.transiciones_splited.append([c1, "ε", r21])
                    self.transiciones_splited.append([c1, "ε", r11])
                    self.transiciones_splited.append([r12, "ε", c2])
                    self.transiciones_splited.append([r22, "ε", c2])
                except:
                    self.error = True
                    print("\nExpresión Regex inválida, | mal aplicado")
            # si es un uno o cero ?
            elif i == "?":
                self.counter = self.counter+1
                c1 = self.counter
                if c1 not in self.estados:
                    self.estados.append(c1)
                self.counter = self.counter+1
                c2 = self.counter
                if c2 not in self.estados:
                    self.estados.append(c2)
                self.afn_final.append({})
                self.afn_final.append({})

                r11, r12 = stack.pop()
                r21, r22 = stack.pop()
                stack.append([c1, c2])
                #self.afn_final[c1]['ε'] = (r21, r11)
                #self.afn_final[r12]['ε'] = c2
                #self.afn_final[r22]['ε'] = c2
                if start == r11 or start == r21:
                    start = c1
                if end == r22 or end == r12:
                    end = c2
                self.transiciones_splited.append([c1, "ε", r21])
                self.transiciones_splited.append([c1, "ε", r11])
                self.transiciones_splited.append([r12, "ε", c2])
                self.transiciones_splited.append([r22, "ε", c2])

        # asignacion de estados finales e iniciales
        self.e0 = start
        self.ef.append(end)

        # Guardar variables para impresión
        df = pd.DataFrame(self.afn_final)
        string_afn = df.to_string()
        for i in range(len(self.transiciones_splited)):
            self.transiciones.append(
                "(" + str(self.transiciones_splited[i][0]) + " - " + str(self.transiciones_splited[i][1]) + " - " + str(self.transiciones_splited[i][2]) + ")")
        self.transiciones = ', '.join(self.transiciones)

        for i in range(len(self.estados)):
            if i == len(self.estados)-1:
                ef = i
            self.estados_list.append(str(self.estados[i]))
        self.estados_list = ", ".join(self.estados_list)

        if self.error == False:
            nombre = 'afn_grafico_'+str(indice)
            self.graficar(nombre)  # imagen del AFN
        else:
            print("\nIngrese una expresión Regex válida")

    def cerradura_epsilon(self, estados):
        """
        Aplica la cerradura epsilon a los estados dados y devuelve todos los estados alcanzables.
        """
        # Inicializar una lista con los estados iniciales
        resultado = estados.copy()
        # Inicializar una pila con los estados iniciales
        pila = estados.copy()
        # Mientras la pila no esté vacía
        while pila:
            # Obtener el siguiente estado de la pila
            actual = pila.pop()
            # Obtener todas las transiciones epsilon desde el estado actual
            epsilon_transiciones = [
                t[2] for t in self.transiciones_splited if t[0] == actual and t[1] == "ε"]
            # Para cada estado alcanzable a través de una transición epsilon
            for e in epsilon_transiciones:
                # Si el estado no está en el resultado
                if e not in resultado:
                    # Agregar el estado al resultado y a la pila
                    resultado.append(e)
                    pila.append(e)
        # Devolver todos los estados alcanzables
        return resultado

    # metodo para simular una cadena en un afn
    def simular_cadena(self, cadena):
        estados_actuales = self.cerradura_epsilon([self.e0])
        estados_finales = []
        for simbolo in cadena:
            nuevos_estados = []
            for estado in estados_actuales:
                for transicion in self.transiciones_splited:
                    if estado == transicion[0] and simbolo == transicion[1]:
                        nuevos_estados.append(transicion[2])
            if not nuevos_estados:
                return False
            estados_actuales = self.cerradura_epsilon(nuevos_estados)
        estados_finales = self.cerradura_epsilon(estados_actuales)
        if isinstance(self.ef, list):
            for estado_final in self.ef:
                if estado_final in estados_finales:
                    return (True, estado_final)
            return False
        else:
            return self.ef in estados_finales
