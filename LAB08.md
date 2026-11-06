# Laboratorio 08 Django REST Framework

**Estudiante:** Diego Magallanes Linares. **Equipo:** individual, un integrante.
**Rama:** `lab08-restframework`. Revisión de entrega: 6 de noviembre de 2026.

La API publica Exam, Question y Choice mediante ModelSerializer, ModelViewSet y
DefaultRouter. Se completaron la guía del campus y el README del laboratorio extra.
El [Word resuelto](deliverables/lab08/Lab08_Diego_Magallanes_Linares.docx) conserva
la guía original y añade desarrollo, capturas reales, tabla de operaciones y conclusiones.

## Procedencia y trabajo realizado

Se integró el código de [dae-s08-api-headless](https://github.com/Hellscythe25/dae-s08-api-headless),
revisión `5bdd1fac96c114d1b6e190f1e7994ad564f4d145`, sobre el proyecto acumulativo.
El material inicial incluía modelos, dos recursos, serializadores, pasarela,
pruebas y un cliente incompleto. Con asistencia de Codex se completaron
`exit_code_for`, `build_question_payload`, permisos y el tercer recurso; se
reforzaron validaciones y se prepararon evidencias y documentación. No se atribuye
el código inicial a una creación propia desde cero. No se ejecutó un modelo local
real; su adaptador opcional está cubierto por las pruebas proporcionadas.

## Instalación y ejecución

Requiere Python 3.12 o superior. Desde un clon nuevo:

```powershell
git clone --branch lab08-restframework https://github.com/DiegoMagallanes11/Motor-de-plantillas-con-Django.git
cd Motor-de-plantillas-con-Django
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/setup_local.py
.\.venv\Scripts\python.exe manage.py seed_quiz
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8008
```

`setup_local.py` prepara la configuración local y aplica migraciones. `seed_quiz`
**sustituye los cuestionarios locales de práctica** por dos exámenes, ocho
preguntas y 32 opciones; no toca blog ni noticias. Conserva los tokens existentes.
Los tokens se guardan en `.private/quiz_tokens.json`, excluido de Git.

En otra ventana de PowerShell:

```powershell
$quizTokens = Get-Content .private/quiz_tokens.json | ConvertFrom-Json
$env:QUIZ_URL = 'http://127.0.0.1:8008'
$env:QUIZ_TOKEN = $quizTokens.human
.\.venv\Scripts\python.exe quizctl.py exams list
.\.venv\Scripts\python.exe quizctl.py --json questions list --search prefetch_related
.\.venv\Scripts\python.exe quizctl.py --dry-run questions create --exam 1 --text '¿Qué es REST?' --choice 'Un estilo:ok' --choice 'Un lenguaje'
.\.venv\Scripts\python.exe quizctl.py ops
```

Rutas locales:

- API navegable: `http://127.0.0.1:8008/api/`.
- Contrato OpenAPI: `http://127.0.0.1:8008/api/schema/`.
- Documentación interactiva: `http://127.0.0.1:8008/api/docs/`.
- Las páginas de noticias y ORM de los laboratorios anteriores se mantienen.

La API admite `Authorization: Token <token local>`. Para usar los formularios de
la API navegable, también puede iniciarse sesión con el usuario staff local
`diego` creado por `setup_local.py`; su contraseña está en `.private/admin-access.txt`.
Las cuentas `profe` y `agente` de la carga inicial usan token y no tienen contraseña
utilizable. No publicar los archivos privados ni capturar sus valores.

## Modelos relaciones y validación

Exam tiene `title`, `created_at` y varias preguntas. Question contiene `exam`,
`text`, `created_at` y varias opciones. Choice contiene `question`, `text` e
`is_correct`. Los ids y fechas son de solo lectura; Exam incluye además un
`question_count` calculado. Question representa exam por id y choices anidadas.

Una pregunta necesita al menos dos opciones y exactamente una correcta. Omitir
choices en PATCH conserva las existentes; enviarlas sustituye el conjunto
completo dentro de una transacción. También se exige texto en las opciones
anidadas de un PATCH. El recurso independiente de opciones valida el estado
resultante de la pregunta al crear, modificar o borrar; impide mover opciones
entre preguntas. La regla pertenece a los serializadores y no se ejecuta
automáticamente al escribir directamente por ORM.

## Permisos

| Identidad | Leer | Crear y modificar | Borrar |
| --- | --- | --- | --- |
| Persona staff | Sí | Sí | Sí |
| Grupo agente | Sí | Sí | No, 403 |
| Otro autenticado | Sí | No, 403 | No, 403 |
| Sin token ni sesión | No, 401 | No, 401 | No, 401 |

El grupo agente tiene prioridad incluso si el usuario es staff. Los métodos
desconocidos se deniegan. Los permisos se aplican en el servidor.

## Filtros y paginación

`/api/questions/?exam=1` filtra por examen; `?search=prefetch_related` busca en
text. `?page=1` devuelve cinco de las ocho preguntas y `?page=2` las otras tres.
Los ids dependen de la carga local. Un filtro como `?exam=no` devuelve 400.
`select_related` y `prefetch_related` cargan las relaciones de las preguntas.

## Verificación y evidencias

La ejecución del 21 de octubre quedó registrada en
[evidence](deliverables/lab08/evidence/):

- `01-red-tests.txt`: 17 pruebas iniciales; tres fallos y nueve errores antes de completar las funciones.
- `02-green-core.txt`: 39 pruebas del núcleo aprobadas.
- `03-full-suite.txt`: 100 pruebas aprobadas, incluidas las sesiones previas y HTTP real.
- `contract-tests.txt`: comprobaciones posteriores del contrato aprobadas.
- `http-results.json`: 34 peticiones reales con curl y sus cuerpos y estados completos.
- `browser-results.json` y capturas: cinco operaciones desde formularios DRF y 404 tras borrar.
- `cli-results.json`, `agent-results.json`, `agent-audit.jsonl`: cliente y pasarela sin tokens.
- `editor.jpg`: estructura real del proyecto en VS Code, capturada en la revisión final.

Para reproducir:

```powershell
.\.venv\Scripts\python.exe manage.py test --verbosity 2
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py spectacular --file deliverables/lab08/schema.yml --validate
# Con el servidor 8008 activo y los tokens locales cargados por seed_quiz:
.\.venv\Scripts\python.exe scripts/verify_lab08.py
```

El verificador crea y elimina sus registros temporales; valida el conteo final.
Las capturas de la API se obtuvieron con `scripts/capture_lab08.cjs` y
`scripts/complete_lab08_browser.cjs` mediante Playwright y Edge. Estos auxiliares
de captura requieren el runtime de escritorio y usan rutas locales documentadas
en su código; no son dependencias para ejecutar Django.

Al borrar en formato JSON se recibe **204 sin cuerpo**. El renderizador HTML
de DRF transporta la página de borrado con 200 y muestra 204 en su panel; esa
diferencia se documenta en lugar de confundir ambos estados.

## Contrato cliente y frontera del agente

El [schema.yml](deliverables/lab08/schema.yml) generado declara los tres recursos,
parámetros, autenticación y respuestas. `quizctl.py ops` consulta el contrato real.
El cliente convierte `:ok` en `is_correct=True`; la validación permanece en la API.
Sus códigos de salida son 0 éxito, 1 uso u otro error, 2 validación400,
3 autenticación o permiso401/403, 4 no encontrado404, 5 servidor5xx y 6 sin conexión.

`agent/gateway.py` acepta únicamente intenciones con operaciones de su lista
cerrada presentes en OpenAPI. R0 lee y R1 crea con el token agente. R2 devuelve
un plan con hash y requiere aprobación vigente y token humano para ejecutarse.
Se rechazaron una cadena de código y `run_sql`. La pregunta con instrucciones
hostiles se devuelve dentro de `untrusted_data` y no cambia los permisos.

Se comprobó la renovación del plan tras modificar el objetivo, el rechazo sin
token humano, el 403 usando token agente como humano y un borrado temporal
aprobado con 204. El hash liga la aprobación a la descripción observada del
objetivo; no es una transacción distribuida ni elimina la carrera entre comprobar
y borrar. El servidor sigue siendo la última frontera.

## Tabla de la API

La base usada fue `http://127.0.0.1:8008`. Las filas siguientes proceden de las
respuestas reales guardadas. Los ids son los de aquella ejecución, no ids fijos
para todas las instalaciones. Q1 se reproduce tras la tabla. Las respuestas
íntegras están en `evidence/http-results.json`; aquí se resumen sus campos.

| Recurso | Dirección | Método | Cuerpo JSON | Respuesta real |
| --- | --- | --- | --- | --- |
| exams | `/api/exams/` | GET | Sin cuerpo | 200; count=3; results paginado |
| exams | `/api/exams/5/` | GET | Sin cuerpo | 200; id, title, created_at, question_count; id=5 |
| exams | `/api/exams/` | POST | {"title": "HTTP Lab08"} | 201; id, title, created_at, question_count; id=5 |
| exams | `/api/exams/5/` | PATCH | {"title": "HTTP Lab08 actualizado"} | 200; id, title, created_at, question_count; id=5 |
| exams | `/api/exams/5/` | DELETE | Sin cuerpo | 204; Sin contenido |
| questions | `/api/questions/` | GET | Sin cuerpo | 200; count=9; results paginado |
| questions | `/api/questions/11/` | GET | Sin cuerpo | 200; id, exam, text, choices, created_at; id=11 |
| questions | `/api/questions/` | POST | Q1 (debajo) | 201; id, exam, text, choices, created_at; id=11 |
| questions | `/api/questions/11/` | PATCH | {"text": "REST sobre HTTP"} | 200; id, exam, text, choices, created_at; id=11 |
| questions | `/api/questions/11/` | DELETE | Sin cuerpo | 204; Sin contenido |
| choices | `/api/choices/` | GET | Sin cuerpo | 200; count=35; results paginado |
| choices | `/api/choices/40/` | GET | Sin cuerpo | 200; id, question, text, is_correct; id=40 |
| choices | `/api/choices/` | POST | {"question": 11, "text": "Un sistema operativo", "is_correct": false} | 201; id, question, text, is_correct; id=40 |
| choices | `/api/choices/40/` | PATCH | {"text": "Un compilador"} | 200; id, question, text, is_correct; id=40 |
| choices | `/api/choices/40/` | DELETE | Sin cuerpo | 204; Sin contenido |

Cuerpo Q1:

```json
{
  "exam": 5,
  "text": "¿Qué es REST?",
  "choices": [
    {
      "text": "Un estilo",
      "is_correct": true
    },
    {
      "text": "Un lenguaje",
      "is_correct": false
    }
  ]
}
```

## Conclusiones

1. Los ModelSerializer y ViewSets permitieron publicar tres modelos relacionados con rutas coherentes y validación centralizada.
2. Las opciones anidadas facilitaron crear preguntas completas. La validación del recurso independiente evitó romper la regla de una única correcta.
3. Las cinco operaciones devolvieron 200, 201 y 204 en JSON; los errores deliberados produjeron 400, 401, 403 y 404 según el caso.
4. OpenAPI, la tabla y los registros HTTP permiten contrastar el contrato con la implementación. Las cien pruebas registradas y las peticiones externas sustentan la entrega.
5. El agente no puede borrar con su identidad. Su pasarela exige aprobación para operaciones destructivas y trata los textos de preguntas como datos.

La entrega al campus y la inscripción en el grupo individual deben efectuarse
desde la cuenta del estudiante. Este repositorio no constituye un despliegue público de Django.
