# Guía rápida

AIDataReady revisa datos locales con contratos para RAG, ML y herramientas de
agentes. Necesitas Python 3.12 o posterior. Los ejemplos usan datos sintéticos.

Visita el [sitio oficial de AIDataReady](https://aidataready.lynvera.ai).

## Instalar

En macOS o Linux:

```bash
git clone https://github.com/lynvera-ai/aidataready.git
cd aidataready
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
aidataready version
```

Versión esperada: `0.1.0`. La instalación de dependencias suele necesitar internet.
Después, los ejemplos funcionan sin conexión. El paquete no está publicado en PyPI.

En Windows PowerShell, crea el entorno con `py -3.12 -m venv .venv` y usa:

```powershell
.venv\Scripts\python.exe -m pip install .
.venv\Scripts\aidataready.exe version
```

Sustituye `aidataready` por esa ruta en los siguientes comandos.
La instalación limpia en Windows sigue pendiente de verificación.

## Ejecutar una revisión

Desde la carpeta del proyecto:

```bash
aidataready check --config examples/rag.yaml
aidataready report --format html
```

El resumen comienza con `local-knowledge: PASS. Records: 2.`.
Abre `aidataready-report.html` en tu navegador. Puedes filtrar los resultados.
El reporte funciona sin servidor ni recursos externos.

## Ver un problema conocido

```bash
aidataready check --config examples/duplicate-ids.yaml --output duplicates.json
aidataready report --input duplicates.json --output duplicates.html
```

El resultado es FAIL: hay un identificador duplicado. El primer comando devuelve
código 1. Ejecuta el segundo por separado para abrir el detalle.

| Estado | Código de check | Significado |
| --- | ---: | --- |
| PASS | 0 | Cumple las reglas configuradas. |
| WARN | 0 | Hay una advertencia que revisar. |
| FAIL | 1 | Se encontró un incumplimiento. |
| ERROR | 2 | No se pudo completar la ejecución. |
| INCONCLUSIVE | 2 | Falta evidencia o el análisis tiene límites. |

Un resultado positivo no certifica la calidad de un modelo ni los permisos reales.

## Revisar tus datos

En una carpeta nueva, con el entorno activo:

```bash
aidataready init
```

Crea `data.csv` junto a `aidataready.yaml`:

```csv
id,name
1,Ana
2,Luis
```

Luego ejecuta:

```bash
aidataready check --config aidataready.yaml
```

El contrato inicial exige identificadores únicos y no vacíos. Agrega los campos
que necesites. Las rutas de datos se resuelven desde el archivo YAML.
`init` no sobrescribe archivos. Usa `--path otro.yaml` para elegir otro nombre.

## Continuar

Consulta los [perfiles](../profiles.md), la [API Python](../python-api.md),
[PostgreSQL](../postgresql.md) y la [solución de problemas](../troubleshooting.md).
Las referencias completas están en inglés.

La detección sensible es opcional y heurística. Los reportes omiten valores de
registros, pero muestran nombres de campos y fuentes. No compartas credenciales.

[Vuelve al índice](../README.md).
