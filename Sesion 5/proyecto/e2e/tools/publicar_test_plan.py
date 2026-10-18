#!/usr/bin/env python3
"""
Publica los resultados de la automatizacion en los TEST POINTS de un
Azure Test Plan, para que cada Test Case cambie a Passed/Failed en la
pestana Execute del plan (no solo en la pestana Tests del run).

POR QUE ESTE SCRIPT:
  PublishTestResults@2 deja el resultado en el "Test Run" del pipeline, pero
  NO mueve el Test Point del Test Plan. Para actualizar el Test Point hay que
  llamar a la REST API de Azure Test (Runs + Results) asociando plan, suite y
  punto. Eso es lo que hace este script.

COMO FUNCIONA:
  1. Lee el junit.xml y saca, por cada <testcase>, su test_case_id (la
     propiedad que escribe el conftest desde el tag @TC<id>) y si paso o fallo.
  2. Para cada Test Case, consulta sus Test Points en el plan/suite dados.
  3. Crea un Test Run asociado al plan y publica el resultado en ese punto.

VARIABLES DE ENTORNO que necesita (las define el pipeline):
  - SYSTEM_COLLECTIONURI : ej. https://dev.azure.com/mi-org/   (lo da Azure)
  - SYSTEM_TEAMPROJECT   : nombre del proyecto                  (lo da Azure)
  - AZURE_DEVOPS_PAT     : Personal Access Token con permiso "Test management
                           (Read & write)" -> se guarda como secret del pipeline
  - TEST_PLAN_ID         : ID del Test Plan (ej. 17 en tu captura era el suite)
  - TEST_SUITE_ID        : ID del Suite dentro del plan
  - JUNIT_PATH           : ruta al junit.xml (default: resultados/junit.xml)

USO LOCAL (ejemplo):
  export SYSTEM_COLLECTIONURI="https://dev.azure.com/mi-org/"
  export SYSTEM_TEAMPROJECT="ProyectoTienda"
  export AZURE_DEVOPS_PAT="xxxxx"
  export TEST_PLAN_ID="12"
  export TEST_SUITE_ID="17"
  python tools/publicar_test_plan.py
"""
import base64
import json
import os
import sys
import xml.etree.ElementTree as ET
from urllib import request as urlrequest
from urllib.error import HTTPError

API = "7.1"  # version de la REST API


def _env(nombre, requerido=True, default=None):
    v = os.environ.get(nombre, default)
    if requerido and not v:
        print(f"[ERROR] Falta la variable de entorno {nombre}")
        sys.exit(2)
    return v


def _auth_header(pat):
    token = base64.b64encode(f":{pat}".encode()).decode()
    return f"Basic {token}"


def _call(metodo, url, pat, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urlrequest.Request(url, data=datos, method=metodo)
    req.add_header("Authorization", _auth_header(pat))
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urlrequest.urlopen(req) as r:
            texto = r.read().decode()
            ctype = r.headers.get("Content-Type", "")
            url_final = r.geturl()
            # Si Azure responde 200 pero con HTML (pagina de login), el PAT fue
            # rechazado silenciosamente. Mostramos pistas concretas para depurar.
            if "application/json" not in ctype and texto.lstrip().startswith("<"):
                print(f"  [debug] HTTP 200 pero Content-Type={ctype!r}")
                print(f"  [debug] URL final tras redirecciones: {url_final}")
                print(f"  [debug] primeros 160 chars de la respuesta: {texto[:160].strip()!r}")
                raise RuntimeError(
                    "La respuesta es HTML (pagina de inicio de sesion), no JSON. "
                    "Esto pasa cuando Azure NO acepta el PAT. Causas, en orden: "
                    "(1) el PAT no tiene el scope 'Test Management (Read & write)'; "
                    "(2) la organizacion exige otro metodo de auth y los PAT estan "
                    "restringidos por politica; (3) el PAT es de otra organizacion."
                )
            return json.loads(texto or "{}")
    except HTTPError as e:
        cuerpo_err = e.read().decode()[:300]
        print(f"  [debug] {metodo} {url} -> HTTP {e.code}")
        if e.code in (401, 203, 302):
            raise RuntimeError(
                f"Autenticacion rechazada (HTTP {e.code}). El PAT llego pero NO tiene "
                f"permiso para la API de Test Plans. CAUSA MAS COMUN: al PAT le falta "
                f"el scope 'Test Management (Read & write)'. En el token, haz 'Show all "
                f"scopes' y marca Test Management -> Read & write (o usa 'Full access'). "
                f"Work Items o Advanced Security NO cubren Test Management."
            )
        print(f"[ERROR] {metodo} {url} -> {e.code}: {cuerpo_err}")
        raise


def leer_junit(ruta):
    """Devuelve {test_case_id: 'Passed'|'Failed'} a partir del junit.xml."""
    resultados = {}
    arbol = ET.parse(ruta)
    for tc in arbol.iter("testcase"):
        tc_id = None
        for prop in tc.iter("property"):
            if prop.get("name") == "test_case_id":
                tc_id = prop.get("value")
        if not tc_id:
            continue
        fallo = any(True for _ in tc.iter("failure")) or any(True for _ in tc.iter("error"))
        resultados[tc_id] = "Failed" if fallo else "Passed"
    return resultados


def main():
    base = _env("SYSTEM_COLLECTIONURI").rstrip("/")
    proyecto = _env("SYSTEM_TEAMPROJECT")
    pat = _env("AZURE_DEVOPS_PAT")
    plan_id = _env("TEST_PLAN_ID")
    suite_id = _env("TEST_SUITE_ID")
    junit = _env("JUNIT_PATH", requerido=False, default="resultados/junit.xml")

    # ── DIAGNOSTICO (no revela el token, solo si llega y su longitud) ──
    print("── Diagnostico de configuracion ──")
    print(f"  SYSTEM_COLLECTIONURI = {base}")
    print(f"  SYSTEM_TEAMPROJECT   = {proyecto}")
    print(f"  TEST_PLAN_ID         = {plan_id}")
    print(f"  TEST_SUITE_ID        = {suite_id}")
    if pat:
        print(f"  AZURE_DEVOPS_PAT     = (recibido, longitud {len(pat)} chars)")
        # Los PAT de Azure DevOps hay de dos formatos: el clasico (~52 chars,
        # minusculas+numeros) y el nuevo (~84 chars, empieza con 'Es...'). Ambos
        # son validos. Lo que importa NO es la longitud, sino el SCOPE del token:
        # para la API de Test Plans se necesita 'Test Management (Read & write)'.
        if len(pat) < 40:
            print("  [AVISO] El PAT parece DEMASIADO CORTO: revisa que lo pegaste completo.")
    else:
        print("  AZURE_DEVOPS_PAT     = (VACIO -> el secret no esta llegando al step)")
    print("───────────────────────────────────")

    if not os.path.exists(junit):
        print(f"[ERROR] No existe el junit en {junit}")
        sys.exit(2)

    resultados = leer_junit(junit)
    if not resultados:
        print("[AVISO] El junit no tiene test_case_id (revisa los tags @TC). Nada que publicar.")
        return
    print(f"Resultados leidos: {resultados}")

    # 0) Chequeo rapido: pedir los datos del plan. Si responde JSON, el token
    #    es valido y el plan existe en ESTE proyecto.
    url_plan = f"{base}/{proyecto}/_apis/testplan/plans/{plan_id}?api-version={API}"
    try:
        info = _call("GET", url_plan, pat)
        print(f"PAT OK. Plan {plan_id}: '{info.get('name')}'")
    except Exception as e:
        print(f"[ERROR] No pude encontrar el plan {plan_id} en el proyecto '{proyecto}': {e}")
        # Si el token sirve pero el plan no esta aqui, listamos los planes que SI
        # existen en este proyecto, para ver si el plan esta en OTRO proyecto o
        # si el ID es distinto.
        try:
            url_planes = f"{base}/{proyecto}/_apis/testplan/plans?api-version={API}"
            planes = _call("GET", url_planes, pat).get("value", [])
            if planes:
                print(f"  Planes que SI existen en el proyecto '{proyecto}':")
                for p in planes:
                    print(f"    - ID {p.get('id')}: '{p.get('name')}'")
                print("  -> Si tu plan 'Tienda v1 - Regresion' NO esta en esta lista,")
                print("     esta en OTRO proyecto. Ajusta SYSTEM_TEAMPROJECT o corre el")
                print("     pipeline en el proyecto correcto. Si esta con otro ID, ajusta TEST_PLAN_ID.")
            else:
                print(f"  El proyecto '{proyecto}' no tiene Test Plans. ¿Es el proyecto correcto?")
        except Exception as e2:
            print(f"  [AVISO] Tampoco pude listar los planes del proyecto: {e2}")
        return

    # 1) Mapear testCaseId -> pointId. Los casos pueden estar repartidos en
    #    suites distintos (Carrito, Catalogo, Pedidos), asi que recorremos TODOS
    #    los suites del plan. Usamos la API 'testplan' (la 'test/Plans/.../suites'
    #    quedo obsoleta y da 404 en organizaciones nuevas).
    por_caso = {}       # testCaseId -> pointId
    suite_de_caso = {}  # testCaseId -> suiteId (para construir la URL de resultados)

    def _agregar_puntos_de_suite(sid):
        # TestPoint de la API moderna 'testplan'
        url = f"{base}/{proyecto}/_apis/testplan/Plans/{plan_id}/Suites/{sid}/TestPoint?api-version={API}"
        try:
            for p in _call("GET", url, pat).get("value", []):
                # En testplan, el caso viene en p['testCaseReference']['id']
                ref = p.get("testCaseReference") or {}
                caso = str(ref.get("id") or p.get("testCase", {}).get("id"))
                if caso and caso != "None":
                    por_caso[caso] = p.get("id")
                    suite_de_caso[caso] = sid
        except Exception as e:
            print(f"[AVISO] No pude leer TestPoints del suite {sid}: {e}")

    # Listar todos los suites del plan (API testplan) y recorrerlos.
    url_suites = f"{base}/{proyecto}/_apis/testplan/Plans/{plan_id}/suites?api-version={API}"
    try:
        suites = _call("GET", url_suites, pat).get("value", [])
        print(f"Suites del plan {plan_id}: {[s.get('id') for s in suites]}")
        for s in suites:
            sid = s.get("id")
            if sid:
                _agregar_puntos_de_suite(sid)
    except Exception as e:
        print(f"[AVISO] No pude listar los suites del plan {plan_id}: {e}")
        # Respaldo: al menos el suite configurado
        _agregar_puntos_de_suite(suite_id)

    print(f"Test Points encontrados (testCaseId -> pointId): {por_caso}")

    # 2) Crear un Test Run asociado al plan con los puntos que vamos a reportar
    puntos_a_reportar = [por_caso[c] for c in resultados if c in por_caso]
    if not puntos_a_reportar:
        print("[AVISO] Ningun test_case_id coincide con un Test Point del suite. "
              "Revisa que los @TC apunten a casos de ESTE plan/suite.")
        return

    url_run = f"{base}/{proyecto}/_apis/test/runs?api-version={API}"
    run = _call("POST", url_run, pat, {
        "name": f"E2E Tienda - automatizado (build {os.environ.get('BUILD_BUILDNUMBER', 'local')})",
        "plan": {"id": str(plan_id)},
        "pointIds": [int(x) for x in puntos_a_reportar],
        "automated": True,
    })
    run_id = run["id"]
    print(f"Test Run creado: {run_id}")

    # 3) Traer los resultados del run (se crean uno por punto) y actualizarlos
    url_res = f"{base}/{proyecto}/_apis/test/Runs/{run_id}/results?api-version={API}"
    results = _call("GET", url_res, pat).get("value", [])

    # mapea pointId -> outcome que queremos
    outcome_por_punto = {}
    for c, outcome in resultados.items():
        pid = por_caso.get(c)
        if pid is not None:
            outcome_por_punto[pid] = outcome

    actualizaciones = []
    for r in results:
        pid = r.get("testPoint", {}).get("id")
        pid = int(pid) if pid is not None else None
        outcome = outcome_por_punto.get(pid)
        if outcome:
            actualizaciones.append({
                "id": r["id"],
                "outcome": outcome,
                "state": "Completed",
                "comment": "Resultado publicado por la automatizacion E2E (pytest-bdd).",
            })

    if actualizaciones:
        _call("PATCH", url_res, pat, actualizaciones)
        print(f"Actualizados {len(actualizaciones)} resultados en el run {run_id}.")

    # 4) Cerrar el run
    _call("PATCH", f"{base}/{proyecto}/_apis/test/runs/{run_id}?api-version={API}",
          pat, {"state": "Completed"})
    print("Test Run cerrado. Revisa la pestana Execute del Test Plan.")


if __name__ == "__main__":
    main()
