# Jacaranda | Lexer, Parser & SDT

Proyecto académico de la asignatura **Compiladores**, Facultad de Ingeniería, UNAM. Equipo 01, grupo 5.

Jacaranda reconoce tokens de un subconjunto de C, comprueba la estructura de las instrucciones y realiza algunas validaciones semánticas. El analizador **no ejecuta los programas ni implementa todo C**.

## Qué hace Jacaranda

- **Lexer:** identifica palabras reservadas, identificadores, constantes, operadores y signos de puntuación con RPLY.
- **Parser:** utiliza descenso recursivo para reconocer declaraciones, funciones, parámetros, bloques, condicionales, ciclos y expresiones; genera un *Parse Tree* y un AST.
- **SDT:** revisa tipos de datos, ámbitos, variables declaradas, funciones, argumentos y valores de retorno.
- **Interfaz:** permite analizar código, abrir archivos y visualizar el *Parse Tree*. El árbol se puede exportar en SVG, PNG o JPG.

## Instalación y ejecución

Se necesita Python 3.10 o superior, RPLY, Pillow y Tkinter para abrir la interfaz. Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python src/gui.py
```

En Windows también se puede utilizar `py` en lugar de `python`.

Para analizar un ejemplo desde la terminal:

```bash
python src/parser_main.py examples/parser/21_function_main.c
```

Para ejecutar las pruebas automatizadas:

```bash
python -m unittest discover -s tests -v
```

En la interfaz, **Analyze** corresponde al lexer; **Parser & SDT** realiza el análisis sintáctico y semántico; **View Parse Tree** permite consultar el árbol de derivación. La entrada debe ser sintácticamente válida para construirlo.

## Organización del proyecto

| Carpeta o archivo | Contenido |
|---|---|
| `src/LexicalAnalyzer.py` | Lexer original con RPLY |
| `src/Parser.py` | Parser descendente recursivo y árboles |
| `src/SemanticAnalyzer.py` | Comprobaciones semánticas y tablas de símbolos |
| `src/analysis_pipeline.py` | Conexión entre lexer, parser y SDT |
| `src/gui.py` y `src/ParseTreeViewer.py` | Interfaz gráfica y visualización del árbol |
| `src/main.py` y `src/parser_main.py` | Ejecución desde terminal |
| `examples/` | Entradas de prueba del lexer y del parser |
| `tests/` | Pruebas automatizadas |
| `Lexical Diagrams/` | Diagramas correspondientes al análisis léxico |
| `docs/` | Material académico y reportes disponibles |
| `requirements.txt` | Dependencias de Python |

## Documentación

Los detalles de la gramática, reglas SDT, ejemplos y límites del parser se encuentran en **[PARSER_README.md](PARSER_README.md)**.

Los reportes académicos y los materiales de la primera entrega se organizan en `docs/`. La documentación técnica actualizada del Parser & SDT se encuentra en el archivo enlazado arriba.

## Repositorio

https://github.com/ErickaAgui/unam.fi.compilers.g5.01
