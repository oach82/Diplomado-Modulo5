#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Triage de fallos asistido por IA (Dia 5).

Lee el reporte JUnit que genera pytest (resultados/junit.xml) y produce:
  1) Un resumen legible de que paso (pasadas, fallidas, tiempo).
  2) Por cada fallo: nombre del caso y mensaje de error resumido.
  3) Un PROMPT listo para pegar en Claude (con MCP de Playwright) que pide
     diagnosticar la causa raiz y proponer un arreglo.

Es la pieza "+ IA en el CI/CD": en vez de leer logs crudos, el pipeline (o tu)
genera un prompt estructurado para que la IA haga el primer triaje.

Uso:
    pytest --junitxml=resultados/junit.xml      # genera el reporte
    python tools/triage_ia.py                   # resume y arma el prompt
    python tools/triage_ia.py resultados/junit-sauce.xml   # otro archivo

No requiere red ni IA para correr: solo lee el XML y arma el texto. La IA la
pones tu pegando el prompt en Claude.
"""
import sys
import os
import xml.etree.ElementTree as ET

# En Windows la consola puede usar cp1252; forzamos UTF-8 para no romper.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RESET = "\x1b[0m"; BOLD = "\x1b[1m"; VERDE = "\x1b[32m"; ROJO = "\x1b[31m"
GRIS = "\x1b[90m"; CYAN = "\x1b[36m"; AMAR = "\x1b[33m"


def cargar(ruta):
    if not os.path.exists(ruta):
        print(f"{ROJO}No existe {ruta}.{RESET}")
        print(f"{GRIS}Genera el reporte primero: pytest --junitxml={ruta}{RESET}")
        sys.exit(1)
    return ET.parse(ruta).getroot()


def iter_testcases(root):
    # junit puede venir como <testsuites><testsuite>... o <testsuite> directo
    suites = root.iter("testsuite")
    for suite in suites:
        for tc in suite.iter("testcase"):
            yield tc


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "resultados/junit.xml"
    root = cargar(ruta)

    total = pasadas = fallidas = errores = saltadas = 0
    tiempo = 0.0
    fallos = []  # (nombre, tipo, mensaje)

    for tc in iter_testcases(root):
        total += 1
        tiempo += float(tc.get("time", 0) or 0)
        nombre = f"{tc.get('classname', '')}::{tc.get('name', '')}".strip(":")
        failure = tc.find("failure")
        error = tc.find("error")
        skip = tc.find("skipped")
        if failure is not None:
            fallidas += 1
            fallos.append((nombre, "failure", (failure.get("message") or "").strip()))
        elif error is not None:
            errores += 1
            fallos.append((nombre, "error", (error.get("message") or "").strip()))
        elif skip is not None:
            saltadas += 1
        else:
            pasadas += 1

    # -- Resumen --
    print(f"\n{BOLD}=== TRIAGE DE FALLOS (IA-ready) - {ruta} ==={RESET}")
    print(f"  Total      : {total}")
    print(f"  {VERDE}Pasadas    : {pasadas}{RESET}")
    print(f"  {ROJO if fallidas else VERDE}Fallidas   : {fallidas}{RESET}")
    print(f"  {ROJO if errores else VERDE}Errores    : {errores}{RESET}")
    print(f"  {GRIS}Saltadas   : {saltadas}{RESET}")
    print(f"  Tiempo     : {tiempo:.1f} s")

    if not fallos:
        print(f"\n  {VERDE}{BOLD}Todo en verde. No hay nada que triar.{RESET}\n")
        return 0

    print(f"\n{BOLD}-- Fallos detectados ------------------------{RESET}")
    for i, (nombre, tipo, msg) in enumerate(fallos, 1):
        corto = (msg[:160] + "...") if len(msg) > 160 else msg
        print(f"  {ROJO}{i}. {nombre}{RESET}")
        print(f"     {GRIS}[{tipo}] {corto}{RESET}")

    # ── Prompt para la IA ────────────────────────────────────
    lineas = [
        "Eres un ingeniero de QA. Estas pruebas E2E (Playwright + Screenplay + BDD, "
        "sobre una app de tienda) fallaron en el pipeline. Para cada fallo:",
        "1) Explica la causa raiz mas probable en una frase.",
        "2) Di si parece un bug de la app, un selector fragil o un problema de entorno.",
        "3) Propon un arreglo concreto (que archivo/paso tocar).",
        "Usa el servidor MCP de Playwright para abrir la app y verificar el selector si hace falta.",
        "",
        "Fallos:",
    ]
    for i, (nombre, tipo, msg) in enumerate(fallos, 1):
        lineas.append(f"- Caso {i}: {nombre}")
        lineas.append(f"  Error [{tipo}]: {msg or '(sin mensaje)'}")

    prompt = "\n".join(lineas)
    print(f"\n{BOLD}{CYAN}-- PROMPT PARA CLAUDE (copia y pega) --------{RESET}")
    print(f"{AMAR}{prompt}{RESET}")

    # Guardar el prompt en un archivo para el pipeline / adjuntarlo
    os.makedirs("resultados", exist_ok=True)
    with open("resultados/triage-prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"\n{GRIS}Prompt guardado en resultados/triage-prompt.txt{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
