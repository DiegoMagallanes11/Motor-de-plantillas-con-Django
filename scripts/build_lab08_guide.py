"""Complete the supplied Lab 08 Word guide while retaining its artwork."""
import ast
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(r"C:\Users\Magal\Downloads\GLAB-S08-MMONTGOMERY-2026-02.docx")
OUT = ROOT / "deliverables" / "lab08"
EV = OUT / "evidence"
QA = ROOT / "deliverables" / "qa" / "lab08"
QA.mkdir(parents=True, exist_ok=True)
rows = json.loads((EV / "http-results.json").read_text(encoding="utf-8"))
actions = json.loads((EV / "agent-results.json").read_text(encoding="utf-8"))
browser = json.loads((EV / "browser-results.json").read_text())
document = Document(SOURCE)
original = list(document.paragraphs)
# Correct the supplied cover's instructor/course overlap, without changing art.
for paragraph in original[12:17]:
    paragraph._p.getparent().remove(paragraph._p)
original[18].paragraph_format.space_before = Pt(18)
for paragraph in original[51:]:
    paragraph._p.getparent().remove(paragraph._p)
document.core_properties.author = "Diego Magallanes Linares"
document.core_properties.title = "Guía resuelta Laboratorio 08 Django REST Framework"


def p(text="", bold=False, size=11):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(7)
    paragraph.paragraph_format.line_spacing = 1.08
    run = paragraph.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.bold = bold
    return paragraph


def heading(text, new_page=False):
    if new_page:
        document.add_page_break()
    paragraph = p(text, True, 13)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.space_before = Pt(8)


def code(text):
    paragraph = p(text.strip("\n"), size=8.3)
    paragraph.paragraph_format.line_spacing = 1
    for run in paragraph.runs:
        run.font.name = "Consolas"


def table(headers, values, widths):
    result = document.add_table(rows=1, cols=len(headers))
    result.alignment = WD_TABLE_ALIGNMENT.CENTER
    result.autofit = False
    for column, width in zip(result.columns, widths):
        column.width = Inches(width)
    for cell, text in zip(result.rows[0].cells, headers):
        cell.text = text
    for row in values:
        for cell, text in zip(result.add_row().cells, row):
            cell.text = str(text)
    repeat = OxmlElement("w:tblHeader")
    result.rows[0]._tr.get_or_add_trPr().append(repeat)
    for index, row in enumerate(result.rows):
        for column, cell in enumerate(row.cells):
            cell.width = Inches(widths[column])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            properties = cell._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for edge in ("top", "left", "bottom", "right"):
                border = OxmlElement(f"w:{edge}")
                for key, value in {"val": "single", "sz": "4", "color": "D9D9D9"}.items():
                    border.set(qn("w:" + key), value)
                borders.append(border)
            properties.append(borders)
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "E6EEF2" if index == 0 else "FFFFFF")
            properties.append(shade)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(4)
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(0, 0, 0)
                    run.bold = index == 0
    p("", size=3)


def picture(name, caption, height=3.8, crop=None):
    image_path = EV / name
    image = Image.open(image_path)
    if crop:
        image = image.crop(crop)
        image_path = QA / ("crop-" + Path(name).stem + ".png")
        image.save(image_path)
    width = min(6.5, height * image.width / image.height)
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run().add_picture(str(image_path), width=Inches(width))
    paragraph = p(caption, size=9)
    paragraph.runs[0].italic = True


def find(label):
    return next(row for row in rows if row["label"] == label)


def resource(name, singular, image):
    heading("Paso 11 Tabla de la API de " + name, True)
    p("Base de las pruebas: http://127.0.0.1:8008. Se envió JSON con el token de la persona. Los valores y códigos siguientes proceden de curl, no de respuestas supuestas.")
    values = []
    for operation in ("list", "retrieve", "create", "patch", "delete"):
        row = find(operation + " " + (name if operation == "list" else singular))
        body = "Sin cuerpo" if row["body"] is None else (
            "Q1, reproducido debajo" if operation == "create" and singular == "question"
            else json.dumps(row["body"], ensure_ascii=False)
        )
        result = row["response"]
        response = str(row["status"])
        if result is None:
            response += "; sin contenido"
        elif "results" in result:
            response += f"; count={result['count']}; results paginado"
        else:
            response += f"; id={result['id']}"
            if "choices" in result:
                response += f"; {len(result['choices'])} opciones"
        values.append([row["method"], row["path"], body, response])
    table(["Método", "Dirección", "Cuerpo", "Respuesta real"], values, [.8, 1.65, 2.4, 1.65])
    created = find("create " + singular)
    p("Cuerpo Q1" if singular == "question" else "Ejemplo de creación", True)
    code(json.dumps(created["body"], ensure_ascii=False, indent=2))
    p("La respuesta de creación expone: " + ", ".join(created["response"].keys()) + ". El detalle JSON íntegro, incluidas fechas e ids, está en evidence/http-results.json.")
    picture(image, "Captura real del recurso en la API navegable.", height=2.8, crop=(140, 85, 1300, 650))


heading("VIII Desarrollo resuelto", True)
p("Estudiante: Diego Magallanes Linares", True)
p("Equipo: individual, 1 integrante. Revisión de entrega: 6 de noviembre de 2026. Las evidencias de ejecución corresponden al 21 de octubre de 2026.")
p("Tema: Django REST Framework. Práctica calificada Nro. 2.")
p("Repositorio del curso: DiegoMagallanes11/Motor-de-plantillas-con-Django. Rama de esta entrega: lab08-restframework.")
p("Se conservaron las páginas de la guía y se completó su desarrollo con resultados verificables. La API expone exámenes, preguntas y opciones, valida una única respuesta correcta y documenta las operaciones por HTTP. La suite completa pasó con 100 pruebas, incluidas las sesiones anteriores.")
heading("Origen del código y participación")
p("Se incorporó el repositorio de referencia indicado por el estudiante: https://github.com/Hellscythe25/dae-s08-api-headless, revisión 5bdd1fac96c114d1b6e190f1e7994ad564f4d145. El material ya contenía modelos, serializadores, dos recursos, contrato, cliente incompleto, pasarela y pruebas.")
p("Con asistencia de Codex se completaron las dos funciones del cliente, los permisos y el tercer recurso choices; se reforzó la validación, se integró con el proyecto acumulativo, se ejecutaron pruebas y se preparó esta documentación. No se atribuye a otros integrantes participación inexistente ni se presenta el código inicial como escrito desde cero por el estudiante.")
heading("Relación entre la guía y el repositorio extra")
p("La guía exige la API con tres recursos y su tabla HTTP. El README agrega OpenAPI, cliente de consola y frontera del agente. Se cubrieron ambos alcances. El adaptador opcional a un modelo local se comprobó con las pruebas entregadas, sin afirmar que se haya ejecutado un modelo real.")

heading("Pasos 1 y 2 Preparación y configuración", True)
p("La aplicación quiz se añadió al proyecto existente, manteniendo news y blog. Se instalaron Django REST Framework 3.18.3, drf-spectacular 0.30.0 y requests 2.34.2 junto con Django 6.0.9 y Pillow 12.3.0.")
code(r"""git switch -c lab08-restframework
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_quiz
python manage.py runserver 127.0.0.1:8008""")
code('''REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "quiz.permissions.AgentPermission",
    ],
    "DEFAULT_PAGINATION_CLASS":
        "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}''')
p("Se registraron rest_framework, rest_framework.authtoken, drf_spectacular y quiz en INSTALLED_APPS. La clave de Django sigue en el entorno, sin credenciales escritas en settings.py. Los tokens se guardan únicamente en .private/quiz_tokens.json, excluido de Git.")
p("La carga deja dos exámenes, ocho preguntas y treinta y dos opciones. Cada pregunta tiene cuatro opciones y una sola correcta. La cuenta profe es la persona con permisos de escritura; agente pertenece al grupo del mismo nombre. Se conservan los tokens entre cargas, pero seed_quiz sustituye los datos de cuestionarios de práctica.")

heading("Pasos 3 y 4 Modelos serializadores y relaciones", True)
table(["Modelo", "Relaciones y campos"], [
    ["Exam", "id, title, created_at. Tiene varias questions."],
    ["Question", "id, exam, text, created_at. Exam es ForeignKey; tiene varias choices."],
    ["Choice", "id, question, text, is_correct. Opción vinculada a una pregunta."],
], [1.1, 5.4])
p("Se conserva el nombre inglés Choice del repositorio para representar una opción. Los tres serializadores derivan de ModelSerializer. Los ids, fechas y question_count son de solo lectura; no se permite que el cliente los asigne.")
code('''class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]
        read_only_fields = ["id"]

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    class Meta:
        model = Question
        fields = ["id", "exam", "text", "choices", "created_at"]
        read_only_fields = ["id", "created_at"]''')
p("El examen viaja por identificador. Las opciones viajan anidadas dentro de la pregunta para crear o sustituir el conjunto completo de respuestas en una petición. ChoiceResourceSerializer expone además question por id cuando se usa el recurso independiente /api/choices/.")
p("En PATCH, omitir choices conserva las opciones existentes. Enviar choices sustituye el conjunto completo después de validarlo. Las escrituras se ejecutan dentro de una transacción; un error en las opciones no guarda parcialmente el nuevo enunciado.")

heading("Paso 5 Validación propia e integridad de las opciones", True)
code('''def validate_choices(self, value):
    if len(value) < 2:
        raise serializers.ValidationError(
            "Una pregunta necesita al menos dos opciones."
        )
    if sum(1 for choice in value if choice.get("is_correct")) != 1:
        raise serializers.ValidationError(
            "Debe haber exactamente una opción correcta."
        )
    return value''')
p("Se exige al menos dos opciones y exactamente una marcada como correcta. La regla se revisa en POST y cuando PATCH o PUT reemplazan las opciones. También se exige texto en cada opción anidada, aunque la operación de la pregunta sea parcial.")
table(["Operación", "Regla aplicada"], [
    ["Crear pregunta", "Valida el conjunto completo antes de guardar."],
    ["Cambiar solo text", "Mantiene y comprueba las opciones actuales."],
    ["Reemplazar choices", "Valida y sustituye atómicamente el conjunto."],
    ["Crear opción independiente", "Evalúa cómo quedaría la pregunta tras agregarla."],
    ["Marcar otra opción correcta", "400 si produciría dos correctas."],
    ["Borrar o desmarcar la correcta", "400 si la pregunta quedaría sin respuesta correcta."],
    ["Mover una opción a otra pregunta", "400; se debe editar la pregunta completa."],
], [2.2, 4.3])
p("La regla pertenece a la API y sus serializadores; una escritura directa por ORM no invoca automáticamente esos serializadores. Las pruebas incluyen validaciones fallidas sin cambios parciales en la base.")

heading("Paso 6 ViewSets enrutador y permisos", True)
code('''router = DefaultRouter()
router.register("exams", ExamViewSet, basename="exam")
router.register("questions", QuestionViewSet, basename="question")
router.register("choices", ChoiceViewSet, basename="choice")

path("api/", include("quiz.urls")),
path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"))''')
p("Los tres conjuntos de vistas derivan de ModelViewSet mediante AtomicWriteViewSet. El enrutador genera list, retrieve, create, update, partial_update y destroy. No se declararon rutas manuales para cada recurso.")
table(["Identidad", "Leer", "Crear o modificar", "Eliminar"], [
    ["Persona is_staff", "Sí", "Sí", "Sí"],
    ["Grupo agente", "Sí", "Sí", "No; 403"],
    ["Autenticado sin rol", "Sí", "No; 403", "No; 403"],
    ["Sin token o token inválido", "401", "401", "401"],
], [2.3, .7, 1.7, 1.8])
p("El grupo agente tiene prioridad incluso si una cuenta llegara a ser staff. Los métodos no reconocidos se deniegan. La decisión está en el servidor: saltarse la pasarela no habilita DELETE con el token del agente.")
picture("browser-root.png", "Figura 1. Raíz real de la API navegable con los tres recursos.", height=2.7, crop=(140, 80, 1300, 630))

heading("Paso 7 Operaciones en la API navegable", True)
table(["Acción", "Código observado"], [
    ["Listar exámenes", "200"], ["Crear examen temporal", "201"],
    ["Ver su detalle", "200"], ["Modificar title con PATCH", "200"],
    ["Eliminar", "Representación DRF: 204; entrega HTML: 200"],
    ["Consultar el eliminado", "404"],
], [3.2, 3.3])
p("Se usaron los formularios de la API navegable, incluida la pestaña Raw data para PATCH. DRF convierte el estado de transporte de su representación HTML de DELETE a 200 para poder dibujar la página, pero muestra 204 en el panel. Al pedir application/json, el borrado sí devuelve 204 sin cuerpo, como confirma curl.")
picture("browser-created-201.png", "Figura 2. Creación real desde el formulario con estado 201.", height=2.4, crop=(140, 80, 1300, 540))
picture("browser-patch-200.png", "Figura 3. PATCH real del título con estado 200.", height=2.4, crop=(140, 80, 1300, 455))

resource("exams", "exam", "browser-exams.png")
resource("questions", "question", "browser-questions.png")
resource("choices", "choice", "browser-choices.png")

heading("Pasos 8 y 9 Cliente externo y errores HTTP", True)
p(f"Se ejecutaron {len(rows)} peticiones reales con curl. Las tablas anteriores recogen las cinco operaciones pedidas para cada recurso: GET colección, GET detalle, POST, PATCH y DELETE. Los errores y los cuerpos JSON también se registraron. Las filas de respuesta resumen el JSON; http-results.json conserva el contenido íntegro.")
for label in ("missing required field", "wrong type", "two correct choices"):
    row = find(label)
    p(label + " — HTTP " + str(row["status"]), True)
    code("Request: " + json.dumps(row["body"], ensure_ascii=False) + "\n\nResponse: " + json.dumps(row["response"], ensure_ascii=False))
p("Además se verificaron 401 sin autenticación, 403 al intentar borrar con el agente, 404 al consultar registros eliminados y 400 al agregar una segunda opción correcta. Las peticiones no válidas no persistieron preguntas nuevas.")

heading("Paso 10 Filtro búsqueda y paginación", True)
table(["Petición", "Resultado real"], [
    ["GET /api/questions/?exam=<id válido>", "200; 4 preguntas del examen."],
    ["GET /api/questions/?search=prefetch_related", "200; 1 pregunta coincidente."],
    ["GET /api/questions/?page=1", "200; count=8; results con 5 elementos; next no nulo."],
    ["GET /api/questions/?page=2", "200; results con 3 elementos; previous no nulo."],
    ["GET /api/questions/?exam=no", "400; debe ser un entero positivo."],
], [3.65, 2.85])
code('''filter_backends = [filters.SearchFilter]
search_fields = ["text"]

queryset = Question.objects.select_related("exam").prefetch_related("choices")
queryset = queryset.filter(exam_id=int(exam))''')
p("El parámetro exam se valida antes de convertirlo. SearchFilter busca sobre text. La paginación de cinco elementos permite observar dos páginas con los ocho registros de referencia. select_related y prefetch_related evitan consultar de nuevo el examen y las opciones por cada pregunta.")
p("Los datos temporales de las pruebas se eliminaron; se conservaron los dos exámenes y las ocho preguntas de referencia. No se alteraron las noticias ni los datos de ORM de sesiones previas.")

heading("Extensión del README Contrato y cliente de consola", True)
p("Se generó y validó schema.yml con drf-spectacular. El contrato declara los tres recursos, parámetros, autenticación y respuestas de éxito y error. La documentación navegable está en /api/docs/ y el formato de máquina en /api/schema/.")
code("python manage.py spectacular --file deliverables/lab08/schema.yml --validate\npython quizctl.py exams list\npython quizctl.py --json questions list --search prefetch_related\npython quizctl.py --dry-run questions delete 3\npython quizctl.py ops")
p("exit_code_for traduce el estado HTTP al contrato del cliente. build_question_payload convierte el sufijo :ok en is_correct=True y conserva el resto de los textos. La validación de cuántas opciones son correctas sigue correspondiendo al servidor.")
table(["Salida", "Significado"], [
    [0, "Éxito HTTP 2xx o dry-run correctamente descrito"],
    [1, "Otro error o uso incorrecto"], [2, "Validación HTTP 400"],
    [3, "HTTP 401 o 403"], [4, "HTTP 404"], [5, "HTTP 5xx"], [6, "Sin conexión"],
], [.6, 5.9])
p("Las pruebas del cliente cubren errores de conexión, falta de token, JSON estable, creación válida, error de validación y dry-run sin escritura. El comando ops lee las operaciones reales del contrato; no mantiene una lista copiada a mano.")

heading("Extensión del README Frontera del agente", True)
table(["Intención", "Resultado real"], [
    [json.dumps(row["intent"], ensure_ascii=False), row["result"]["status"]]
    for row in actions["intents"]
], [4.75, 1.75])
p("La pregunta con IGNORA TUS INSTRUCCIONES se conserva como dato dentro de untrusted_data. Leerla no concede permiso para ejecutar código ni para borrar exámenes. La pasarela usa una lista cerrada de operaciones, comprueba su presencia en OpenAPI y valida las claves y tipos de los argumentos.")
table(["Prueba de aprobación", "Resultado"], [
    ["Plan para borrar una pregunta temporal", actions["plan"]["status"]],
    ["Se cambia el texto antes de aprobar", actions["stale"]["status"] + "; se requiere el plan nuevo"],
    ["Se aprueba sin token de persona", actions["no_human"]["status"]],
    ["Se entrega token del agente como si fuera humano", "403 del servidor; no se borra"],
    ["Se aprueba el plan vigente con token de persona", actions["applied"]["status"] + "; HTTP 204"],
], [4.45, 2.05])
p("Cada decisión queda registrada en agent-audit.jsonl sin tokens. El hash del repositorio liga la aprobación a una descripción del objetivo observada por la pasarela; no se presenta como una transacción distribuida ni como garantía de que no haya cambios concurrentes entre comprobar y borrar. Los permisos del servidor siguen siendo la última frontera.")

heading("Pruebas antes y después y estructura", True)
table(["Ejecución", "Resultado registrado"], [
    ["Cliente y permisos iniciales, 17 pruebas", "3 fallos y 9 errores, reproducidos antes de completar los TODO."],
    ["Núcleo API, serializadores, permisos y cliente", "39 pruebas correctas en la primera revisión."],
    ["Suite completa final", "100 pruebas correctas, incluidas las sesiones anteriores y HTTP real."],
    ["Contrato OpenAPI", "Validado; pruebas de operaciones y tokenAuth correctas."],
    ["curl", f"{len(rows)} peticiones con los estados esperados."],
    ["API navegable", "Cinco operaciones verificadas y 404 después del borrado."],
], [3.4, 3.1])
code("Ran 100 tests in 6.012s\nOK\npython manage.py makemigrations --check --dry-run\n# No changes detected")
if (EV / "editor.jpg").exists():
    picture("editor.jpg", "Figura 4. Estructura real del proyecto y serializadores en el editor.", height=3.5)
p("El repositorio incluye quiz/models.py, serializers.py, views.py, permissions.py y urls.py; quizctl.py; agent/; pruebas; migraciones; dependencias y herramientas de reproducción. Los tokens y la base local se excluyen de Git.")

heading("Paso 12 Entrega y correspondencia con la rúbrica", True)
p("Rama: https://github.com/DiegoMagallanes11/Motor-de-plantillas-con-Django/tree/lab08-restframework")
p("La guía resuelta, las evidencias y el contrato se publican junto con el código. La subida al campus y la inscripción personal en el grupo individual de Personas → Grupos corresponden al estudiante; no se presentan como acciones realizadas.")
table(["Criterio de 5 puntos", "Evidencia"], [
    ["ModelSerializer y validación propia", "Tres modelos; opciones anidadas; exactamente una correcta; campos de lectura."],
    ["Tres recursos por ViewSets y router", "exams, questions y choices presentes en /api/ y OpenAPI."],
    ["Cinco operaciones por HTTP", "curl en cada recurso, API navegable, errores y códigos registrados."],
    ["Repositorio y tabla de la API", "Tabla con recurso, dirección, método, cuerpo y respuesta acorde a evidencia."],
], [2.65, 3.85])
p("La fila 1.3 es una medición de acreditación y no agrega puntos a los veinte del laboratorio, según la guía.")
heading("Uso de IA y participación individual")
p("Diego Magallanes Linares es el único integrante. Se utilizó Codex para revisar el material, integrar y completar el código de referencia, ejecutar verificaciones y preparar el entregable. Se aceptaron las modificaciones después de contrastarlas con las pruebas y con respuestas HTTP reales. No se fabricaron capturas, intentos personales ni una ejecución de un modelo local.")

heading("Conclusiones", True)
for text in [
    "1. Django REST Framework permitió exponer los modelos Exam, Question y Choice como recursos HTTP mediante ModelSerializer, ModelViewSet y DefaultRouter, manteniendo el proyecto acumulativo en una rama propia del mismo repositorio.",
    "2. Representar el examen por id y las opciones anidadas permitió crear una pregunta completa en una sola petición. La validación de exactamente una opción correcta se mantuvo tanto al reemplazar opciones como al gestionarlas por el recurso independiente.",
    "3. Las peticiones reales confirmaron 200 para lectura y PATCH, 201 para creación y 204 sin contenido para DELETE en JSON. Los casos inválidos devolvieron 400, 401, 403 y 404 según correspondía. Separar el estado HTML de la API navegable evitó documentar incorrectamente un borrado JSON como 200.",
    "4. La búsqueda, el filtrado por examen y la paginación mostraron resultados verificables sobre ocho preguntas conocidas. El contrato OpenAPI y la tabla de la API hacen explícitos los parámetros, cuerpos y respuestas que utilizan los clientes.",
    "5. El cliente de consola tradujo los errores HTTP a códigos de salida estables y permitió simular escrituras con dry-run. El agente no pudo borrar con su propia identidad: la pasarela exigió aprobación y el servidor rechazó DELETE con su token.",
    "6. Las cien pruebas aprobadas y las evidencias de navegador y curl permitieron comprobar el resultado sin confiar solo en capturas. Mantener tokens fuera del repositorio y documentar la procedencia del código hizo la entrega reproducible y transparente.",
]:
    p(text)
heading("Referencias y archivos de evidencia")
for text in [
    "Guía GLAB-S08-MMONTGOMERY-2026-02.docx proporcionada por el estudiante.",
    "Repositorio de referencia: https://github.com/Hellscythe25/dae-s08-api-headless",
    "Serializadores DRF: https://www.django-rest-framework.org/api-guide/serializers/",
    "Enrutadores DRF: https://www.django-rest-framework.org/api-guide/routers/",
    "Contrato: https://drf-spectacular.readthedocs.io/en/latest/customization.html",
]:
    p(text, size=9)
p("Evidencias: deliverables/lab08/evidence. Contrato: deliverables/lab08/schema.yml. Incluye resultados completos HTTP, CLI, pasarela, pruebas y capturas reales.", size=9)

target = OUT / "Lab08_Diego_Magallanes_Linares.docx"
document.save(target)
with ZipFile(SOURCE) as source_zip, ZipFile(target) as target_zip:
    preserved = [name for name in source_zip.namelist() if name.startswith(("word/media/", "word/header"))]
    assert all(source_zip.read(name) == target_zip.read(name) for name in preserved)
print(str(target))
