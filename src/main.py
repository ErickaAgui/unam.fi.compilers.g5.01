from pathlib import Path

from rply import errors

from LexicalAnalyzer import Lexer


CONSTANT_TYPES = {'STRING', 'REAL', 'INTEGER', 'BOOLEAN'}


def clasificar_token(token):
    """Converts the internal lexer type to the category shown to the user."""
    tipo = token.gettokentype()

    if tipo == 'KEYWORD':
        return 'keyword'
    if tipo == 'IDENTIFIER':
        return 'identifier'
    if tipo == 'OPERATOR':
        return 'operator'
    if tipo in CONSTANT_TYPES:
        return 'constant'
    if tipo == 'PUNCTUATION':
        return 'punctuation'

    return tipo.lower()


def obtener_posicion(codigo, indice):
    """Returns a human-friendly 1-based line and column for ``indice``.

    RPLY provides the absolute source index in the error position.  Computing
    line and column from that index avoids incorrect columns after ignored
    whitespace and makes the value match what a user sees in the input.
    """
    indice = max(0, min(indice, len(codigo)))

    linea = codigo.count('\n', 0, indice) + 1
    ultimo_salto = codigo.rfind('\n', 0, indice)
    columna = indice + 1 if ultimo_salto == -1 else indice - ultimo_salto

    inicio_linea = ultimo_salto + 1
    siguiente_salto = codigo.find('\n', indice)
    if siguiente_salto == -1:
        siguiente_salto = len(codigo)

    texto_linea = codigo[inicio_linea:siguiente_salto]
    prefijo = codigo[inicio_linea:indice]

    # Expand tabs so the caret remains visually aligned in the terminal.
    texto_linea_visible = texto_linea.expandtabs(4)
    columna_visual = len(prefijo.expandtabs(4)) + 1

    return linea, columna, texto_linea_visible, columna_visual


def mostrar_error_lexico(codigo, error):
    """Displays the exact invalid position and a caret under the source text."""
    posicion = error.getsourcepos()
    indice = posicion.idx

    linea, columna, texto_linea, columna_visual = obtener_posicion(codigo, indice)

    if 0 <= indice < len(codigo):
        simbolo = repr(codigo[indice])
    else:
        simbolo = 'end of input'

    print(
        f"\nLEXICAL ERROR: unrecognized symbol {simbolo} "
        f"at line {linea}, column {columna}."
    )

    if texto_linea:
        print(f"  {texto_linea}")
        print("  " + " " * (columna_visual - 1) + "^")


def analizar(codigo):
    """Analyzes source text and displays the recognized token sequence."""
    lexer = Lexer().get_lexer()

    try:
        tokens = list(lexer.lex(codigo))
    except errors.LexingError as error:
        mostrar_error_lexico(codigo, error)
        return []

    if not tokens:
        print("\nNo tokens were found.")
        print("Total of tokens: 0")
        return []

    print("\nTOKENS IDENTIFIED:\n")
    for token in tokens:
        categoria = clasificar_token(token)
        print(f"{categoria:<12} {token.getstr()}")

    print("\nToken sequence:")
    print(" ".join(clasificar_token(token) for token in tokens))
    print(f"\nTotal of tokens: {len(tokens)}")

    return tokens


def normalizar_ruta(ruta):
    """Allows pasted Windows paths with or without surrounding quotes."""
    ruta = ruta.strip()
    if len(ruta) >= 2 and ruta[0] == ruta[-1] and ruta[0] in {'"', "'"}:
        ruta = ruta[1:-1]
    return ruta


def leer_archivo(ruta):
    """Reads a UTF-8 text file and returns its contents."""
    return Path(ruta).read_text(encoding='utf-8')


def analizar_archivo():
    """Requests a file path and allows retrying when it cannot be opened."""
    while True:
        ruta = normalizar_ruta(input("\nEnter the file path: "))

        try:
            codigo = leer_archivo(ruta)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as error:
            print(f"\nThe file could not be opened: {error}")
            print("1. Try again")
            print("2. Return to main menu")

            opcion = input("\nSelect an option: ").strip()
            if opcion == '1':
                continue
            if opcion == '2':
                return

            print("\nInvalid option. Returning to the main menu.")
            return

        print("\nSOURCE CODE:\n")
        print(codigo)
        analizar(codigo)
        return


def main():
    while True:
        print("\n------------------------------------------")
        print("            LEXICAL ANALYZER")
        print("       Facultad de Ingenieria - UNAM")
        print("------------------------------------------")
        print("\n1. Analyze a string")
        print("2. Analyze a file")
        print("3. Exit")

        opcion = input("\nSelect an option: ").strip()

        if opcion == '1':
            codigo = input("\nEnter the string to analyze:\n> ")
            analizar(codigo)

        elif opcion == '2':
            analizar_archivo()

        elif opcion == '3':
            print("\nProgram finished.")
            break

        else:
            print("\nInvalid option. Please try again.")


if __name__ == '__main__':
    main()
