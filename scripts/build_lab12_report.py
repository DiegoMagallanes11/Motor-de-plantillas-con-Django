"""Build the Lab12 report (Ajax y Servicios Web) and its delivery archive."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'deliverables/lab12'
EV = OUT / 'evidence'
SOURCE = ROOT / 'lab11-hooks'

backend_tests = (EV / 'backend-tests.txt').read_text(encoding='utf-8-sig')
frontend_tests = (EV / 'frontend-tests.txt').read_text(encoding='utf-8-sig')
backend_check = (EV / 'backend-check.txt').read_text(encoding='utf-8-sig')
cors_live = (EV / 'cors-live.txt').read_text(encoding='utf-8')
crud_live = (EV / 'crud-live.txt').read_text(encoding='utf-8')
delivery = json.loads((EV / 'delivery-checks.json').read_text(encoding='utf-8'))

doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.27), Inches(11.69)
section.top_margin = section.bottom_margin = Inches(.68)
section.left_margin = section.right_margin = Inches(.73)
for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2']:
    style = doc.styles[name]
    style.font.name = 'Calibri'
    style.font.color.rgb = RGBColor(0, 0, 0)
    for border in list(style.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    for color in style.element.iter(qn('w:color')):
        color.set(qn('w:val'), '000000')
        for attribute in ['themeColor', 'themeTint', 'themeShade']:
            color.attrib.pop(qn('w:' + attribute), None)
doc.styles['Normal'].font.size = Pt(11)
doc.styles['Normal'].paragraph_format.space_after = Pt(7)
doc.styles['Normal'].paragraph_format.line_spacing = 1.07
doc.styles['Title'].font.size = Pt(25)
doc.styles['Heading 1'].font.size = Pt(17)
doc.styles['Heading 2'].font.size = Pt(12)
doc.core_properties.title = 'Laboratorio 12 Ajax y Servicios Web'
doc.core_properties.author = 'Diego Magallanes Linares'

def p(text='', style=None):
    return doc.add_paragraph(text, style)

def heading(text, page=False):
    if page:
        doc.add_page_break()
    doc.add_heading(text, 1)

def code(text, size=9):
    para = p()
    para.paragraph_format.space_after = Pt(7)
    para.paragraph_format.line_spacing = Pt(size + 1.6)
    for i, line in enumerate(text.strip().splitlines()):
        run = para.add_run(('\n' if i else '') + line)
        run.font.name = 'Consolas'
        run.font.size = Pt(size)
    return para

p('Laboratorio 12', 'Title')
p('Ajax y Servicios Web', 'Subtitle')
p('Desarrollo de Aplicaciones Empresariales\nSemana 12 · Periodo 2026')
p('Alumno: Diego Magallanes Linares\nDocente: Michael Montgomery Rosell\nFecha de elaboración: 15 de noviembre de 2026')
heading('Resultado del desarrollo')
p('El laboratorio 12 conecta el backend de Django con el frontend React del laboratorio 11. El backend habilita CORS para el origen del frontend con django-cors-headers; el frontend crea un cliente Axios único y consume la API real de exámenes (GET, POST y DELETE), con el hook useExams que gestiona los tres estados de carga, los datos y el error. La aplicación compila y las pruebas registradas pasan.')
p('Backend: ' + backend_check.strip() + '. Suite completa: ' + backend_tests.strip().splitlines()[3].strip() + '.')
p('Frontend: ' + frontend_tests.strip().splitlines()[2].strip() + '. La compilación se completó sin errores.')
heading('Objetivos')
for text in [
    'Permitir que el navegador del frontend haga petición al backend de Django cruzando el origen de la aplicación React.',
    'Consumir el CRUD de exámenes de la API (Django REST Framework) desde React con Axios.',
    'Gestionar el estado de la petición: cargando, datos y error, con reintento.',
    'Registrar el entregable en el repositorio con las evidencias y el informe de entrega.',
]:
    p(text, 'List Bullet')
heading('Desarrollo del backend con CORS')
p('Se añadió la dependencia django-cors-headers==4.7.0 a requirements.txt. Se registró la aplicación corsheaders en INSTALLED_APPS y el middleware corsheaders.middleware.CorsMiddleware después de django.middleware.security.SecurityMiddleware. Se declararon los orígenes permitidos http://localhost:5173 y http://127.0.0.1:5173 en CORS_ALLOWED_ORIGINS. El middleware responde con Access-Control-Allow-Origin para el origen permitido, acepta el preflight de POST y rechaza orígenes no autorizados.')
code("INSTALLED_APPS = [\n    ...\n    \"corsheaders\",\n    ...\n]\n\nMIDDLEWARE = [\n    \"django.middleware.security.SecurityMiddleware\",\n    \"corsheaders.middleware.CorsMiddleware\",\n    ...\n]")
heading('Desarrollo del frontend con Axios')
p('Archivo principal: lab11-hooks/src/lib/api.js. El cliente Axios usa la base URL desde VITE_API_URL con valor por defecto http://127.0.0.1:8008 y añade el token del persona en Authorization: Token. Las operaciones del laboratorio 12 son GET /api/exams/, POST /api/exams/ y DELETE /api/exams/{id}.')
code("export const API_BASE_URL = import.meta.env.VITE_API_URL || \"http://127.0.0.1:8008\";\n\nexport async function fetchExams() {\n  const { data } = await client.get(\"/api/exams/\");\n  return Array.isArray(data) ? data : data.results ?? [];\n}")
code("export async function createExam(payload) {\n  const { data } = await client.post(\"/api/exams/\", payload);\n  return data;\n}\n\nexport async function deleteExam(id) {\n  await client.delete(`/api/exams/${id}`);\n}")
heading('Estados de la petición en el frontend')
p('Se implementó el hook useExams con los tres estados: loading (Esqueleto mientras carga), ready (exámenes listados) y error (ErrorBanner con Reintentar). El listado se delega en ExamsList, que muestra las filas con título, número de preguntas y fecha, y permite eliminar. El formulario ExamForm mantiene el título controlado, previene el envío por defecto, valida el título requerido y de máximo 120 caracteres, envía el POST y muestra el error que devuelve la API.')
p('La integración en App mantiene el inbox del laboratorio 11 y añade la sección de exámenes con su propio estado y sus propios flujos de creación y borrado.')
heading('Verificación')
p('Backend: python manage.py check -> sin problemas. Suite completa -> 100 tests OK. Frontend: npm test -> 72 tests OK. npm run build -> compilación correcta.')
p('Verificación en caliente del CORS: el backend responde Access-Control-Allow-Origin para http://localhost:5173, acepta el preflight de POST /api/exams/ y rechaza orígenes no permitidos.')
p('Verificación en caliente del CRUD: GET /api/exams/ con token -> 200 OK, POST /api/exams/ con token -> 201 Created, DELETE /api/exams/{id} con token -> 204 No Content, todos con Access-Control-Allow-Origin en http://localhost:5173.')
heading('Uso local')
p('Backend: python manage.py runserver 127.0.0.1:8008. Frontend: npm run dev en lab11-hooks (puerto 5173 por el proyecto). El token de la persona se guarda en localStorage con la clave dae-s11-token; el backend expone los tokens del seed en /api/docs/.')
heading('Conclusión')
p('Con el laboratorio 12 se completó la capa de servicios web del laboratorio: el backend autoriza el origen del frontend con django-cors-headers y el frontend consume la API real con Axios, cubriendo listado, creación y borrado con los tres estados de una petición para el rubricario de la entrega.')

OUT.mkdir(parents=True, exist_ok=True)
doc.save(OUT / 'Lab12_Diego_Magallanes_Linares.docx')

paths = [
    'LAB12.md',
    'config/settings.py',
    'requirements.txt',
    'quiz/',
    'lab11-hooks/src/App.jsx',
    'lab11-hooks/src/lib/api.js',
    'lab11-hooks/src/hooks/useExams.js',
    'lab11-hooks/src/hooks/usePlans.js',
    'lab11-hooks/src/components/ExamsList.jsx',
    'lab11-hooks/src/components/ExamsList.css',
    'lab11-hooks/src/components/ExamForm.jsx',
    'lab11-hooks/src/components/ExamForm.css',
    'lab11-hooks/src/components/ExamsSkeleton.jsx',
    'lab11-hooks/src/components/ErrorBanner.jsx',
    'lab11-hooks/src/test/App.test.jsx',
    'lab11-hooks/src/test/useExams.test.jsx',
    'lab11-hooks/src/test/ExamsList.test.jsx',
    'lab11-hooks/src/test/ExamForm.test.jsx',
]
with ZipFile(OUT / 'Lab12_codigo.zip', 'w', ZIP_DEFLATED) as z:
    for item in paths:
        source = ROOT / item
        if source.is_dir():
            for file in sorted(source.rglob('*')):
                if file.is_file() and '__pycache__' not in file.parts:
                    z.write(file, file.as_posix())
        elif source.exists():
            z.write(source, item)
print('Lab12 report and archive built.')
