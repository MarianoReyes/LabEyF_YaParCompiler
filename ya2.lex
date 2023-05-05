(* archivo 2 *)

let digito = 0|1|2|3|4|5|6|7|8|9
let negativo = -
let numero = negativo?digito(digito)@
let igual = =
let suma = +
let multiplicacion = *
let if = if
let for = for
let while = while
let letra = a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z
let identificador = letra(letra|digito)@

rule tokens =
  digito			{ print("digito\n") }
  | punto			{ print("punto\n") }
  | numero			{ print("numero\n") }
  | negativo			{ print("negativo\n") }
  | igual			{ print("igual\n") }
  | suma			{ print("suma\n") }
  | multiplicacion			{ print("multiplicacion\n") }
  | if	{ print("if\n") }
  | for	{ print("for\n") }
  | while	{ print("while\n") }
  | letra			{ print("letra\n") }
  | identificador	{ print("identificador\n") }
