"""Build the Lab12 report (Ajax y Servicios Web) and its delivery archive."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deliverables/lab12"
EV = OUT / "evidence"
SOURCE = ROOT / "lab11-hooks"


def read_text(name: str, encoding: str = "utf-8") -> str:
    path = EV / name
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


backend_tests = read_text("backend-tests.txt", "utf-8-sig")
frontend_tests = read_text("frontend-tests.txt", "utf-8-sig")
backend_check = read_text("backend-check.txt", "utf-8-sig")
cors_live = read_text("cors-live.txt")
crud_live = read_text("crud-live.txt")
frontend_build = read_text("frontend-build.txt")
delivery = json.loads(read_text("delivery-checks.json"))

doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.27), Inches(11.69)
section.top_margin = section.bottom_margin = Inches(0.68)
section.left_margin = section.right_margin = Inches(0.73)
for name in ["Normal", "Title", "Subtitle", "Heading 1", "Heading 2"]:
    style = doc.styles[name]
    style.font.name = "Calibri"
    style.font.color.rgb = RGBColor(0, 0, 0)
    for border in list(style.element.iter(qn("w:pBdr"))):
        border.getparent().remove(border)
    for color in style.element.iter(qn("w:color")):
        color.set(qn("w:val"), "000000")
        for attribute in ["themeColor", "themeTint", "themeShade"]:
            color.attrib.pop(qn("w:" + attribute), None)
doc.styles["Normal"].font.size = Pt(11)
doc.styles["Normal"].paragraph_format.space_after = Pt(7)
doc.styles["Normal"].paragraph_format.line_spacing = 1.07
doc.styles["Title"].font.size = Pt(25)
doc.styles["Heading 1"].font.size = Pt(17)
doc.styles["Heading 2"].font.size = Pt(12)
doc.core_properties.title = "Laboratorio 12 - Ajax y Servicios Web"
doc.core_properties.author = "Diego Magallanes Linares"


def p(text="", style=None):
    return doc.add_paragraph(text, style)


def heading(text, level=1, page=False):
    if page:
        doc.add_page_break()
    doc.add_heading(text, level)


def code(text, size=9):
    para = p()
    para.paragraph_format.space_after = Pt(6)
    para.paragraph_format.line_spacing = Pt(size + 1.6)
    for i, line in enumerate(text.strip().splitlines()):
        run = para.add_run(("\n" if i else "") + line)
        run.font.name = "Consolas"
        run.font.size = Pt(size)
    return para


def add_image(name: str, caption: str, width=6.4):
    path = EV / name
    if not path.exists():
        p(f"(Captura no encontrada: {name})")
        return
    doc.add_picture(str(path), width=Inches(width))
    cap = p(caption)
    cap.runs[0].italic = True if cap.runs else False
    cap.paragraph_format.space_after = Pt(10)


p("Laboratorio 12 - Ajax y Servicios Web", "Title")
p("Desarrollo de Aplicaciones Empresariales - Semana 12 (2026)", "Subtitle")
p(
    "Alumno: Diego Magallanes Linares\n"
    "Equipo: individual (1 integrante)\n"
    "Rama de trabajo: lab09-react\n"
    "Fecha de elaboración: 15 de noviembre de 2026"
)

heading("1. Objetivo y alcance del laboratorio")
p(
    "El objetivo del Laboratorio 12 es integrar el frontend React con el backend Django mediante "
    "servicios web (AJAX), habilitando CORS en el backend y consumiendo la API real con Axios "
    "para realizar operaciones CRUD sobre el recurso de exámenes. Asimismo, se implementa la "
    "gestión de los tres estados de una petición asíncrona: carga (loading), datos (ready) y "
    "error, cumpliendo con la guía y la rúbrica del laboratorio."
)
for item in [
    "Configurar CORS en Django para permitir peticiones desde el origen del frontend (Vite/React).",
    "Consumir la API REST de exámenes con Axios: listado (GET), creación (POST) y eliminación (DELETE).",
    "Gestionar estados de interfaz: esqueleto de carga, visualización de datos y mensaje de error con reintento.",
    "Generar evidencias de funcionamiento, pruebas automatizadas y entregables (informe, código y capturas).",
]:
    p(item, "List Bullet")

heading("2. Configuración del backend: CORS en Django (5 pts)")
p(
    "Se instaló y configuró django-cors-headers para autorizar solicitudes cross-origin desde el "
    "frontend. Se agregó la dependencia, se registró la aplicación y el middleware, y se "
    "definieron los orígenes permitidos."
)
p("Cambios realizados:", "Heading 2")
for item in [
    "Dependencia añadida en requirements.txt: django-cors-headers==4.7.0.",
    "Aplicación registrada en INSTALLED_APPS: corsheaders.",
    "Middleware agregado después de SecurityMiddleware: corsheaders.middleware.CorsMiddleware.",
    "Orígenes permitidos en CORS_ALLOWED_ORIGINS: http://localhost:5173 y http://127.0.0.1:5173.",
]:
    p(item, "List Bullet")
code(
    'INSTALLED_APPS = [\n'
    '    ...\n'
    '    "corsheaders",\n'
    '    "rest_framework",\n'
    '    ...\n'
    "]\n\n"
    "MIDDLEWARE = [\n"
    '    "django.middleware.security.SecurityMiddleware",\n'
    '    "corsheaders.middleware.CorsMiddleware",\n'
    '    "django.contrib.sessions.middleware.SessionMiddleware",\n'
    "    ...\n"
    "]\n\n"
    "CORS_ALLOWED_ORIGINS = [\n"
    '    "http://localhost:5173",\n'
    '    "http://127.0.0.1:5173",\n'
    "]"
)
p("Verificación de CORS en caliente:", "Heading 2")
code(cors_live or "(sin evidencia cors-live.txt)")
p(
    "Resultado: el backend responde 200/204 según el caso e incluye el encabezado "
    "Access-Control-Allow-Origin para el origen permitido; el preflight OPTIONS para POST es aceptado "
    "y los orígenes no autorizados son rechazados."
)

heading("3. Consumo de la API con Axios: CRUD de exámenes (5 pts)")
p(
    "En el frontend (lab11-hooks/) se implementó un cliente Axios centralizado que consume la API "
    "real del backend. La URL base se obtiene desde VITE_API_URL con valor por defecto "
    "http://127.0.0.1:8008 y se envía el token de autenticación en el encabezado Authorization "
    "(Token ...) leído desde localStorage (clave dae-s11-token)."
)
p("Cliente Axios y operaciones CRUD (src/lib/api.js):", "Heading 2")
code(
    'import axios from "axios";\n\n'
    'export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8008";\n'
    'export const TOKEN_KEY = "dae-s11-token";\n\n'
    'export const client = axios.create({\n'
    '  baseURL: API_BASE_URL,\n'
    '  headers: { Accept: "application/json" },\n'
    '});\n\n'
    'client.interceptors.request.use((config) => {\n'
    '  const token = window.localStorage.getItem(TOKEN_KEY) || "";\n'
    '  if (token) config.headers.Authorization = `Token ${token}`;\n'
    '  return config;\n'
    '});\n\n'
    'export async function fetchExams() {\n'
    '  const { data } = await client.get("/api/exams/");\n'
    '  return Array.isArray(data) ? data : data.results ?? [];\n'
    '}\n\n'
    'export async function createExam(payload) {\n'
    '  const { data } = await client.post("/api/exams/", payload);\n'
    '  return data;\n'
    '}\n\n'
    'export async function deleteExam(id) {\n'
    '  await client.delete(`/api/exams/${id}`);\n'
    '}'
)
p("Componentes y hook involucrados:", "Heading 2")
for item in [
    "useExams (src/hooks/useExams.js): hook con estados loading/ready/error, carga inicial, recarga y cancelación de respuestas obsoletas.",
    "ExamsList (src/components/ExamsList.jsx): muestra la lista real de exámenes, metadatos, estado vacío y acción de eliminar.",
    "ExamForm (src/components/ExamForm.jsx): formulario controlado con validación, preventDefault, envío POST y manejo de errores de API.",
    "App.jsx: integra la sección de exámenes, conecta las acciones de crear/eliminar y dispara recargas tras operaciones exitosas.",
]:
    p(item, "List Bullet")
p("Verificación CRUD en caliente:", "Heading 2")
code(crud_live or "(sin evidencia crud-live.txt)")

heading("4. Gestión de estados: carga, datos y error (5 pts)")
p(
    "La interfaz implementa explícitamente los tres estados de una petición asíncrona para el "
    "recurso de exámenes, cumpliendo el criterio de la guía:"
)
for item in [
    "Estado de carga (loading): se muestra el componente ExamsSkeleton mientras se obtienen los datos desde la API.",
    "Estado de datos (ready): se renderiza ExamsList con los exámenes obtenidos y el formulario ExamForm para crear nuevos registros.",
    "Estado de error (error): se muestra ErrorBanner con el mensaje de error y un botón de reintento que vuelve a ejecutar la carga.",
]:
    p(item, "List Bullet")
code(
    'export default function useExams(fetchExams) {\n'
    '  const [state, setState] = useState({ status: "loading", exams: [], error: null });\n'
    '  const [revision, setRevision] = useState(0);\n'
    '  const reload = useCallback(() => setRevision((c) => c + 1), []);\n\n'
    '  useEffect(() => {\n'
    '    let cancelled = false;\n'
    '    setState({ status: "loading", exams: [], error: null });\n'
    '    fetchExams()\n'
    '      .then((exams) => !cancelled && setState({ status: "ready", exams, error: null }))\n'
    '      .catch((error) => !cancelled && setState({ status: "error", exams: [], error }));\n'
    '    return () => { cancelled = true; };\n'
    '  }, [fetchExams, revision]);\n\n'
    '  return { ...state, reload };\n'
    '}'
)
p(
    "El estado de carga se evidencia con la captura del esqueleto (ExamsSkeleton) durante la consulta "
    "a la API. Los estados de datos y error se muestran en las capturas siguientes, junto con las "
    "operaciones de creación y eliminación realizadas desde la interfaz."
)

heading("5. Evidencias visuales (capturas de pantalla)")
p(
    "Se realizaron capturas en el navegador con el backend Django y el frontend Vite en ejecución, "
    "consumiendo la API real (http://127.0.0.1:8008/api/exams/) con token de autenticación."
)
add_image(
    "exams-loading.png",
    "Figura 1. Estado de carga (loading): se muestra el esqueleto (ExamsSkeleton) mientras se consultan los exámenes en la API.",
)
add_image(
    "exams-ready.png",
    "Figura 2. Estado listo (ready): listado de exámenes cargado desde la API real con Axios y sección de creación disponible.",
)
add_image(
    "exams-form.png",
    "Figura 3. Formulario de creación de examen (POST): entrada controlada lista para enviar un nuevo examen a la API.",
)
add_image(
    "exams-create-success.png",
    "Figura 4. Creación exitosa: el nuevo examen aparece en la lista tras el POST a la API y la recarga de datos.",
)
add_image(
    "exams-delete-success.png",
    "Figura 5. Eliminación desde la interfaz: se ejecuta la operación de borrado y se actualiza la lista de exámenes.",
)
add_image(
    "exams-error.png",
    "Figura 6. Estado de error: fallo simulado de red mostrando ErrorBanner con mensaje y opción de reintentar.",
)
add_image(
    "exams-error-401.png",
    "Figura 7. Evidencia adicional: respuesta 401 sin token, demostrando que el frontend consume el backend real y maneja errores de la API.",
)

heading("6. Pruebas y verificación técnica")
p("Resultados de verificación automatizada y compilación:", "Heading 2")
p(f"Backend (check): {backend_check.strip() or 'sin datos'}.")
p(f"Backend (tests): {backend_tests.strip().splitlines()[-1] if backend_tests.strip() else 'sin datos'}.")
p(f"Frontend (tests): {frontend_tests.strip().splitlines()[-2] if frontend_tests.strip() else 'sin datos'}.")
p(f"Frontend (build): {'compilación correcta' if 'built in' in frontend_build else 'ver frontend-build.txt'}.")
p("Evidencia de pruebas backend:", "Heading 2")
code("\n".join(backend_tests.strip().splitlines()[-8:]) or "(sin evidencia)")
p("Evidencia de pruebas frontend:", "Heading 2")
code(frontend_tests or "(sin evidencia)")
p("Evidencia de compilación frontend:", "Heading 2")
code(frontend_build or "(sin evidencia)")

heading("7. Entregables y repositorio (5 pts)")
p("Se generaron y organizaron los entregables solicitados por la guía del laboratorio:", "Heading 2")
for item in [
    "Informe en Word: deliverables/lab12/Lab12_Diego_Magallanes_Linares.docx (con capturas, descripciones y evidencias).",
    "Archivo de código: deliverables/lab12/Lab12_codigo.zip.",
    "Evidencias: deliverables/lab12/evidence/ (verificaciones CORS/CRUD, pruebas, build y capturas).",
    "Documento resumen: LAB12.md.",
    "Script de generación del informe: scripts/build_lab12_report.py.",
]:
    p(item, "List Bullet")
p("Rúbrica cubierta:", "Heading 2")
for k, label in [
    ("cors", "Configuración CORS en backend"),
    ("axios_crud", "Consumo con Axios y operaciones CRUD"),
    ("states", "Gestión de estados (loading, ready, error)"),
    ("delivery_repository", "Entregables y repositorio"),
]:
    pts = delivery.get("delivery", {}).get("rubric_breakdown", {}).get(k, "")
    p(f"{label}: {pts} puntos", "List Bullet")
p(f"Total: {delivery.get('delivery', {}).get('total', 20)} puntos")

heading("8. Instrucciones de ejecución local")
p("Backend (Django):", "Heading 2")
code(
    "cd C:\\Users\\Magal\\OneDrive\\Documentos\\ChatGPT\\Django\n"
    ".venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8008"
)
p("Frontend (React + Vite):", "Heading 2")
code(
    "cd C:\\Users\\Magal\\OneDrive\\Documentos\\ChatGPT\\Django\\lab11-hooks\n"
    "npm install\n"
    "npm run dev   # http://localhost:5173"
)
p(
    "El token de autenticación se almacena en localStorage con la clave dae-s11-token. "
    "Para pruebas locales se utilizó el token del usuario seed (profe)."
)

heading("9. Conclusión")
p(
    "El Laboratorio 12 se completó satisfactoriamente: se habilitó CORS en Django para el origen "
    "del frontend, se implementó un cliente Axios para consumir la API real de exámenes con "
    "operaciones GET, POST y DELETE, y se gestionaron correctamente los estados de carga, datos y "
    "error en la interfaz React. Las pruebas automatizadas, la compilación y las evidencias en "
    "caliente respaldan el cumplimiento de los criterios solicitados en la guía."
)

OUT.mkdir(parents=True, exist_ok=True)
doc.save(OUT / "Lab12_Diego_Magallanes_Linares.docx")

paths = [
    "LAB12.md",
    "config/settings.py",
    "requirements.txt",
    "quiz/",
    "lab11-hooks/src/App.jsx",
    "lab11-hooks/src/lib/api.js",
    "lab11-hooks/src/hooks/useExams.js",
    "lab11-hooks/src/hooks/usePlans.js",
    "lab11-hooks/src/components/ExamsList.jsx",
    "lab11-hooks/src/components/ExamsList.css",
    "lab11-hooks/src/components/ExamForm.jsx",
    "lab11-hooks/src/components/ExamForm.css",
    "lab11-hooks/src/components/ExamsSkeleton.jsx",
    "lab11-hooks/src/components/ErrorBanner.jsx",
    "lab11-hooks/src/test/App.test.jsx",
    "lab11-hooks/src/test/useExams.test.jsx",
    "lab11-hooks/src/test/ExamsList.test.jsx",
    "lab11-hooks/src/test/ExamForm.test.jsx",
    "deliverables/lab12/evidence/exams-loading.png",
    "deliverables/lab12/evidence/exams-ready.png",
    "deliverables/lab12/evidence/exams-form.png",
    "deliverables/lab12/evidence/exams-create-success.png",
    "deliverables/lab12/evidence/exams-delete-success.png",
    "deliverables/lab12/evidence/exams-error.png",
    "deliverables/lab12/evidence/exams-error-401.png",
    "deliverables/lab12/evidence/backend-check.txt",
    "deliverables/lab12/evidence/backend-tests.txt",
    "deliverables/lab12/evidence/cors-live.txt",
    "deliverables/lab12/evidence/crud-live.txt",
    "deliverables/lab12/evidence/frontend-tests.txt",
    "deliverables/lab12/evidence/frontend-build.txt",
    "deliverables/lab12/evidence/network-capture.txt",
    "deliverables/lab12/evidence/delivery-checks.json",
    "scripts/build_lab12_report.py",
]
with ZipFile(OUT / "Lab12_codigo.zip", "w", ZIP_DEFLATED) as z:
    for item in paths:
        source = ROOT / item
        if source.is_dir():
            for file in sorted(source.rglob("*")):
                if file.is_file() and "__pycache__" not in file.parts:
                    z.write(file, str(file.relative_to(ROOT)).replace("\\", "/"))
        elif source.exists():
            z.write(source, item)
print("Lab12 report and archive built.")
