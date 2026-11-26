# JACARANDA · Equipo 01 · UNAM FI · Compiladores

Este repositorio contiene las **tres entregas** de Jacaranda sin perder el trabajo anterior.

## Proyecto final (1 de diciembre de 2026)

**Intérprete educativo de un subconjunto de C.** La nueva implementación utiliza **Lark 1.3.1** para generar lexer y parser LALR y conserva una etapa propia de comprobación semántica, seguida de ejecución por recorrido del árbol. El lexer de RPLY y el parser descendente recursivo de las entregas anteriores **no se eliminaron**: permanecen en `src/` para preservar el historial y poder comparar enfoques.

```bash
python -m pip install -r requirements.txt
python final_project/src/main.py final_project/examples/03_loops.c
python final_project/src/gui.py
python -m unittest discover -s final_project/tests -v
```

Resultado esperado del ejemplo de ciclos: `15`, `0`, `1`, `2` en el área de salida, precedidos por validación sintáctica y semántica exitosa.

La documentación completa está en [`final_project/README.md`](final_project/README.md) y el reporte en `final_project/docs/01-Compilers-FinalProject.pdf` (completar capturas propias antes de entregarlo).

## Entregas previas

- Lexer con RPLY: `src/LexicalAnalyzer.py`, `src/main.py`, `src/gui.py` (la interfaz anterior) y `docs/lexer/`.
- Parser descendente recursivo y SDT manual: `src/Parser.py`, `src/SemanticAnalyzer.py`, `src/analysis_pipeline.py`, `src/parser_main.py`, `src/ParseTreeViewer.py` y `docs/parser_sdt/`.
- Diagrama léxico: `lexical_diagrams/`; diagramas del parser manual: `parser_diagrams/`.
- Ejemplos de entregas previas: `examples/lexer/`, `examples/parser_sdt/`.

Las dos implementaciones NO tienen exactamente las mismas capacidades, interfaces o bibliotecas. El intérprete de Lark está separado en `final_project/` para evitar sobrescribir los módulos originales y poder hacer una revisión mediante pull request.

## Entrega al profesor

- Subir este árbol a una **rama nueva** del repositorio del equipo y abrir pull request hacia `main`.
- Revisar que el intérprete corre en Windows y que la GUI funciona.
- Agregar capturas reales bien recortadas al reporte LaTeX (sin mostrar todo el escritorio).
- Subir el reporte PDF actualizado y la presentación al directorio `final_project/docs/`.
- Compartir el repositorio público; entrega indicada en la consigna: **1 de diciembre de 2026**.
