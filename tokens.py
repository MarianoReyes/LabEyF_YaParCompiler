import re


class Tokens():
    def __init__(self):
        # Lista para almacenar los tokens
        self.tokens = []

    def getTokens(self, archivo):
        # Abre el archivo y lee todo su contenido
        import re

        # Abre el archivo 'ya.lex' en modo de lectura
        with open(archivo, 'r') as f:
            # Lee todo el contenido del archivo
            content = f.read()

        # Encuentra todas las variables que aparecen después de la línea "rule tokens ="
        matches = re.findall(r'\s*(\w+)\s*{', content)

        # Almacena las variables en una lista
        variables = list(matches)

        with open(archivo, 'r') as f:
            # Leer todas las líneas del archivo
            lines = f.readlines()

            # Expresión regular para extraer el nombre y la expresión regular de cada token
            token_regex = r'let\s+([a-zA-Z0-9_-]+)\s+=\s+(.*)'

        # Recorrer todas las líneas del archivo
        for line in lines:
            # Buscar las líneas que contienen definiciones de tokens
            match = re.match(token_regex, line.strip())
            if match:
                # Extraer el nombre y la expresión regular del token
                name = match.group(1)
                regex = match.group(2)
                # Agregar el token a la lista de tokens
                if name in variables:
                    self.tokens.append((name, regex))
