(* archivo 1 *)

let digito = 0|1|2|3|4|5|6|7|8|9
let negativo = -
let punto = .
let igual = =
let suma = +
let multiplicacion = *
let numero = negativo?digito(digito)@
let numero_hexadecimal = digito(digito)@(a|b|c|d|e|f|A|B|C|D|E|F)
let numero_flotante = digito(digito)@(punto)digito(digito)@
let potencia = ^
let numero_potenciado = digito(digito)@((punto)digito(digito)@)?(potencia)digito(digito)@

rule tokens =
  digito			{ print("digito\n") }
  | punto			{ print("punto\n") }
  | numero			{ print("numero\n") }
  | potencia			{ print("potencia\n") }
  | numero_potenciado			{ print("numero_potenciado\n") }
  | numero_hexadecimal			{ print("numero_hexadecimal\n") }
  | numero_flotante			{ print("numero_flotante\n") }
  | negativo			{ print("negativo\n") }
  | igual			{ print("igual\n") }
  | suma			{ print("suma\n") }
  | multiplicacion			{ print("multiplicacion\n") }
