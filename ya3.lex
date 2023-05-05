(* archivo 1 *)

let digito = 0|1|2|3|4|5|6|7|8|9
let negativo = -
let punto = .
let numero = negativo?digito(digito)@
let numero_flotante = digito(digito)@(punto)digito(digito)@
let if = if
let for = for
let letra = a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z
let identificador = letra(letra|digito)@(a|b|c)
let comilla = "
let espacio = ,
let cadena = comilla(letra|digito|espacio)@comilla

rule tokens =
  digito			{ print("digito\n") }
  | punto			{ print("punto\n") }
  | numero			{ print("numero\n") }
  | numero_flotante			{ print("numero_flotante\n") }
  | negativo			{ print("negativo\n") }
  | if	{ print("if\n") }
  | for	{ print("for\n") }
  | letra			{ print("letra\n") }
  | identificador	{ print("identificador\n") }
  | comilla	{ print("comilla\n") }
  | espacio	{ print("espacio\n") }
  | cadena	{ print("cadena\n") }

