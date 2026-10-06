"""Metricas de productividad (Lead Time, frecuencia de despliegue, CI).
Uso:  GITHUB_TOKEN=xxxx python metrics.py usuario/repositorio
"""
import os
import statistics as st
import sys
from datetime import datetime

import requests

REPO = sys.argv[1]
API = f"https://api.github.com/repos/{REPO}"
HDR = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
       "Accept": "application/vnd.github+json"}


def get(path, **params):
    r = requests.get(API + path, headers=HDR, timeout=30,
                     params={"per_page": 100, **params})
    r.raise_for_status()
    return r.json()


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def horas(a, b):
    return (ts(b) - ts(a)).total_seconds() / 3600


def med(valores):
    return round(st.median(valores), 1) if valores else "s/d"


# --- Pull Requests mergeados a main ---------------------------------------
prs = [p for p in get("/pulls", state="closed", base="main") if p["merged_at"]]
lead_time = [horas(p["created_at"], p["merged_at"]) for p in prs]

espera_revision = []
for p in prs:
    envios = [r["submitted_at"] for r in get(f"/pulls/{p['number']}/reviews")
              if r.get("submitted_at")]
    if envios:
        espera_revision.append(horas(p["created_at"], min(envios)))

# --- Frecuencia de despliegue (merge a main = version integrada) ----------
if len(prs) > 1:
    fechas = [ts(p["merged_at"]) for p in prs]
    semanas = max((max(fechas) - min(fechas)).days / 7, 1)
    frecuencia = round(len(prs) / semanas, 2)
else:
    frecuencia = "s/d"

# --- Ejecuciones del pipeline en main --------------------------------------
runs = [r for r in get("/actions/runs", branch="main")["workflow_runs"]
        if r["conclusion"]]
duracion_ci = [horas(r["run_started_at"], r["updated_at"]) * 60 for r in runs]
fallidas = sum(r["conclusion"] == "failure" for r in runs)
tasa_fallos = round(100 * fallidas / len(runs), 1) if runs else "s/d"

print(f"PRs mergeados analizados ........ {len(prs)}")
print(f"Lead Time (mediana, horas) ...... {med(lead_time)}")
print(f"Espera 1ra revision (mediana, h)  {med(espera_revision)}")
print(f"Frecuencia (merges a main/sem) .. {frecuencia}")
print(f"Duracion del pipeline (min) ..... {med(duracion_ci)}")
print(f"Ejecuciones fallidas (%) ........ {tasa_fallos}")
