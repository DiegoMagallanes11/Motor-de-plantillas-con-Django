"""Build the solved Lab09 guide from the supplied text and retained course design."""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(r"C:\Users\Magal\Downloads\GLAB-S08-MMONTGOMERY-2026-02.docx")
OUT = ROOT / "deliverables/lab09"
EV = OUT / "evidence"
QA = ROOT / "deliverables/qa/lab09"
QA.mkdir(parents=True, exist_ok=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "e4b2cc283e57584ab8209d254ded62be332f3ff18493516ec662c58a1d803ceb"
browser = json.loads((EV / "browser-results.json").read_text(encoding="utf-8"))
document = Document(SOURCE)
original = list(document.paragraphs)
original[7].runs[0].text = "9"
original[9].runs[0].text = "Introducción a ReactJS"
for run in original[9].runs[1:]:
    run.text = ""
for paragraph in original[12:17]:
    paragraph._p.getparent().remove(paragraph._p)
original[18].paragraph_format.space_before = Pt(68)
for paragraph in original[28:]:
    paragraph._p.getparent().remove(paragraph._p)
for section in document.sections:
    for node in section.header._element.iter(qn("w:t")):
        if node.text:
            node.text = node.text.replace("Implementación de Servicios Web con Django.", "Introducción a ReactJS.")
document.core_properties.author = "Diego Magallanes Linares"
document.core_properties.title = "Laboratorio 09 Introducción a ReactJS Guía resuelta"


def p(text="", bold=False, size=11):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.06
    run = paragraph.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.bold = bold
    return paragraph


def heading(text, page=False):
    if page:
        document.add_page_break()
    paragraph = p(text, True, 13)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.space_before = Pt(7)


def code(text):
    paragraph = p(text.strip(), size=8.5)
    paragraph.paragraph_format.line_spacing = 1
    for run in paragraph.runs:
        run.font.name = "Consolas"
    return paragraph


def table(headers, rows, widths):
    result = document.add_table(rows=1, cols=len(headers))
    result.autofit = False
    for column, width in zip(result.columns, widths):
        column.width = Inches(width)
    for cell, text in zip(result.rows[0].cells, headers):
        cell.text = text
    for values in rows:
        for cell, text in zip(result.add_row().cells, values):
            cell.text = str(text)
    repeat = OxmlElement("w:tblHeader")
    result.rows[0]._tr.get_or_add_trPr().append(repeat)
    for index, row in enumerate(result.rows):
        no_split = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(no_split)
        for cell, width in zip(row.cells, widths):
            cell.width = Inches(width)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            props = cell._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for edge in ("top", "left", "bottom", "right"):
                line = OxmlElement("w:" + edge)
                for key, value in {"val": "single", "sz": "4", "color": "D9D9D9"}.items():
                    line.set(qn("w:" + key), value)
                borders.append(line)
            props.append(borders)
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "E6EEF2" if index == 0 else "FFFFFF")
            props.append(shade)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(5)
                paragraph.paragraph_format.space_before = Pt(3)
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(9)
                    run.bold = index == 0
    p("", size=3)


def picture(name, caption, max_height=3.8, crop=None):
    image_path = EV / name
    with Image.open(image_path) as opened:
        image = opened.copy()
    if crop:
        image = image.crop(crop)
        image_path = QA / (Path(name).stem + "-crop.png")
        image.save(image_path)
    width = min(6.5, max_height * image.width / image.height)
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run().add_picture(str(image_path), width=Inches(width))
    caption_paragraph = p(caption, size=9)
    caption_paragraph.runs[0].italic = True


heading("Guía de Laboratorio 09 resuelta")
p("Estudiante: Diego Magallanes Linares", True)
p("Equipo individual, 1 integrante. Revisión de entrega: 8 de noviembre de 2026.")
p("Tema: Introducción a ReactJS. Curso: Desarrollo de Aplicaciones Empresariales. Docente: Michael Montgomery Rosell. Sección: 4-C24-A.")
p("La cartelera Cine Tecsup funciona con ocho películas y ocho componentes funcionales sin estado ni hooks. Se verificaron 47 pruebas principales, 43 pruebas de la copia de IA corregida y 22 comprobaciones en navegador. Este documento reconstruye la guía a partir del texto proporcionado y conserva el diseño institucional de la entrega anterior; no se recibió un Word original de la semana 9.")
heading("I Capacidades")
for text in [
    "Crea un proyecto de React con Vite y lo levanta en el servidor de desarrollo.",
    "Escribe componentes funcionales con JSX y los compone para armar una interfaz completa.",
    "Pasa datos de un componente padre a sus hijos mediante props.",
]:
    p(text)
heading("II Seguridad")
p("Está prohibida la manipulación del hardware y de las conexiones eléctricas o de red, así como ingerir alimentos o bebidas en las estaciones. Mochilas y maletines deben ubicarse en el lugar destinado para ello, sin obstruir el paso ni las salidas. Al terminar, cerrar las sesiones de repositorios y servicios utilizados y dejar la estación y la silla limpias y ordenadas.")
heading("III Fundamento teórico")
p("Revisar la presentación y el cuestionario de refuerzo de la semana en el campus. La práctica aplica lo presentado en aula. El proyecto es acumulativo: se continúa desde el resultado de la semana anterior.")
heading("IV Normas empleadas")
p("Python según PEP 8 y la estructura Django, con una aplicación por responsabilidad y sin credenciales escritas en settings.py. En React, componentes en PascalCase y una carpeta por componente. Código, variables y comentarios en inglés; entregables y explicaciones en español. El repositorio extra aclara que el estado y los hooks corresponden a la semana 10, por lo que aquí no se usan.")
heading("V Recursos y VI Metodología", True)
p("Windows 10 o superior, Python 3.12 o superior, Node.js, Git, Visual Studio Code y acceso a internet. La guía menciona Node 20; las dependencias instaladas concretan las versiones compatibles: Node 20.19 o superior dentro de la rama 20, Node 22.12 o superior dentro de la rama 22, o Node 24 y posteriores. Se utilizó Node 24.15.0.")
p("El trabajo pertenece al repositorio único del curso, en la rama lab09-react. Diego Magallanes Linares es el único integrante. Se documentan nombre, título del desarrollo, capturas reales, código, explicación, casos de prueba y estructura en el editor.")
heading("VII Procedimiento y correspondencia de la solución")
steps = [
    ("1", "Comprobar Node; crear React con Vite; instalar dependencias y levantar el servidor.", "Desarrollo 1"),
    ("2 y 3", "Limpiar la plantilla y organizar componentes, datos y arquitectura de CSS.", "Desarrollo 2"),
    ("4", "Crear al menos ocho películas con título, imagen, sinopsis, clasificación, valoración y horarios.", "Desarrollo 3"),
    ("5 y 6", "Escribir Header con navegación y Footer con información de contacto.", "Desarrollo 4"),
    ("7 y 8", "Crear Hero y MovieCard, recibiendo la película por props.", "Desarrollo 5"),
    ("9", "Recorrer la cartelera con map y asignar una clave estable a cada película.", "Desarrollo 6"),
    ("10", "Componer en App.jsx y comprobar la cartelera completa en navegador.", "Desarrollo 7"),
    ("11", "Provocar class, dos nodos raíz y ausencia de key; registrar y corregir los mensajes.", "Desarrollo 8"),
    ("12", "Entregar repositorio y documento con capturas, código y recorte en componentes.", "Entrega y conclusiones"),
]
table(["Paso", "Requerimiento de la guía", "Desarrollo"], steps, [.65, 4.1, 1.75])
p("Se cubren también las cinco partes del README extra: lectura del verificador, ocho componentes, duelo con IA, corrección de la copia y tratamiento de datos de terceros.")

heading("VIII Desarrollo 1 Preparación y ejecución", True)
p("Se creó frontend/ con el generador oficial create-vite 9.3.4, plantilla react. El backend Django de las sesiones anteriores permanece en el mismo repositorio. La interfaz de esta semana usa datos locales; la guía no pide consumir la API REST.")
code("node --version\n# v24.15.0\nnpm --version\n# 11.12.1\nnpm create vite@latest frontend -- --template react --no-interactive\ncd frontend\nnpm install\nnpm run dev\n# VITE v8.3.6 ready — http://localhost:5173/")
p("Dependencias principales instaladas: React y React DOM 19.3.1, Vite 8.3.6, plugin-react 6.2.1, Vitest 4.1.12, Testing Library React 16.3.3 y jsdom 26.1.0. package.json declara dependencias y scripts; package-lock.json fija la instalación. Para repetir desde el repositorio se usa npm ci, sin volver a generar la plantilla.")
picture("desktop.png", "Figura 1. Cartelera real en el servidor de desarrollo de Vite.", 3.9)
p("Se empleó asistencia de Codex para integrar el material, completar componentes, ejecutar verificaciones y redactar el entregable. No se presenta este trabajo asistido como realizado sin ayuda.")

heading("Desarrollo 2 Estructura y arquitectura de CSS", True)
code("frontend/\n  index.html\n  src/\n    main.jsx\n    App.jsx\n    index.css\n    components/\n      Header/ Footer/ Hero/ MovieCard/\n      MovieList/ Showtimes/ Synopsis/ AgentMessage/\n    data/movies.js\n    data/movieDetails.js\n    styles/tokens.css\n    styles/base.css\n    styles/layout.css\n    duel/team/ ai/ fixed/ tests/\n  public/posters/\n  public/art/\n  lab-errors/\n  package.json  package-lock.json")
p("Cada carpeta de components/ contiene el archivo JSX y su CSS. tokens.css define colores y tipografía; base.css aplica reglas globales, foco y movimiento reducido; layout.css compone secciones y adaptaciones de tamaño. Se emplean nombres de clase por componente. La guía pegada no detalla otra arquitectura; el README extra traía un CSS global y se separó para cumplir la carpeta por responsabilidad.")
picture("editor.jpg", "Figura 2. Captura real de App.jsx y la estructura del proyecto en VS Code.", 3.6)
p("duel/team/ reexporta los componentes de components/ para mantener el contrato del verificador. ai/ conserva las respuestas originales. fixed/ contiene la copia corregida. La estructura de las carpetas de ejercicios se mantiene compatible con los scripts docentes.")

heading("Desarrollo 3 Datos de la cartelera", True)
table(["Película", "Clasificación", "Valoración", "Horarios"], [
    ["La Última Función", "+14", "4.5 / 5", "16:00, 19:30, 22:00"],
    ["Noche en el Altiplano", "ATP", "4.2 / 5", "15:30, 18:00"],
    ["Código Fantasma", "+14", "3.8 / 5", "17:00, 20:15, 22:45"],
    ["El Jardín de Vidrio", "ATP", "4.7 / 5", "14:00, 16:30"],
    ["Ruta 91", "+14", "3.5 / 5", "Sin funciones hoy"],
    ["Mares de Ceniza", "+14", "4.0 / 5", "19:00, 21:30"],
    ["Mi Vecino el Robot", "ATP", "4.9 / 5", "13:00, 15:15, 17:30"],
    ["Medianoche en Lima", "+14", "3.9 / 5", "20:00, 22:30"],
], [2.3, 1.15, .95, 2.1])
p("movies.js se conserva idéntico al del docente: incluye id, title, image, synopsis, rating y showtimes. Como su prueba exige exactamente esos campos, las clasificaciones y géneros ficticios se añaden en movieDetails.js y App los une sin modificar el origen.")
code("const billboard = movies.map((movie) => ({\n  ...movie,\n  ...movieDetails[movie.id],\n}))\nconst featured = billboard[0]")
p("Los ocho afiches y el banner son SVG originales generados localmente con scripts/create-art.mjs; no necesitan imágenes remotas. Las películas, valoraciones y contacto son de demostración, como señala el pie de página. Las clasificaciones añadidas son datos ficticios del ejercicio.")
heading("Observación sobre los datos de terceros")
p("La primera sinopsis contiene una etiqueta img con onerror. Se conserva porque forma parte del caso de prueba del docente; en la versión final se muestra literalmente como texto, sin convertirla en elementos HTML ni ejecutar el manejador.")

heading("Desarrollo 4 Header y Footer", True)
p("Header recibe únicamente name y links. Su h1 identifica al cine y nav tiene el nombre accesible Principal. Cada enlace del map usa href como key; sus destinos Cartelera, Próximamente y Contacto existen en la página.")
code('''export default function Header({ name, links }) {
  return (
    <header>
      <h1>{name}</h1>
      <nav aria-label="Principal">
        <ul>{links.map((link) => (
          <li key={link.href}><a href={link.href}>{link.label}</a></li>
        ))}</ul>
      </nav>
    </header>
  )
}''')
p("El fragmento anterior omite las clases y envoltorios visuales del archivo completo. No omite la lógica de props y listas.")
picture("desktop.png", "Figura 3. Header con nombre y tres enlaces de navegación.", 1.0, (110, 0, 1330, 94))
p("Footer recibe contact y construye sus enlaces con tel: y mailto:. Al cambiar el objeto del padre cambian dirección, teléfono y correo sin editar el componente.")
code('<a href={`tel:${contact.phone}`}>{contact.phone}</a>\n<a href={`mailto:${contact.email}`}>{contact.email}</a>')
picture("footer.png", "Figura 4. Footer con datos de contacto y nota académica.", 1.9)

heading("Desarrollo 5 Hero y MovieCard", True)
p("Hero recibe movie y muestra la destacada con su título, clasificación, género y valoración. El enlace se calcula con el id de esa misma película; no contiene un destino fijo del ejemplo.")
code('<section aria-label="Destacada" className="hero">\n  <h2>{movie.title}</h2>\n  <a href={`#horarios-${movie.id}`}>Ver horarios</a>\n</section>')
p("MovieCard recibe una película completa. La imagen usa alt={movie.title}; la valoración y los horarios provienen de props. details permite abrir y cerrar la sinopsis con el comportamiento nativo del navegador, sin añadir estado de React.")
code('<img src={movie.image} alt={movie.title} />\n<h3>{movie.title}</h3>\n<p>★ {movie.rating}</p>\n<details>\n  <summary>Sinopsis</summary>\n  <Synopsis text={movie.synopsis} />\n</details>\n<p>{movie.showtimes.length > 0\n  ? movie.showtimes.join(" · ")\n  : "Sin funciones hoy"}</p>')
picture("movie-list.png", "Figura 5. Primeras tarjetas con clasificación, valoración y horarios.", 2.7, (0, 150, 1170, 655))
p("Las tarjetas muestran los horarios en una línea. Showtimes reutiliza una lista semántica en la sección de funciones. Así se evita anidar listas de horarios en el ul de películas y se mantiene intacto el verificador original.")

heading("Desarrollo 6 Listas claves y componentes de texto", True)
code('''export default function MovieList({ movies }) {
  return (
    <ul className="movie-list">
      {movies.map((movie) => (
        <li key={movie.id}><MovieCard movie={movie} /></li>
      ))}
    </ul>
  )
}''')
p("La clave es el id de la película, no la posición. Las pruebas invierten la lista y eliminan el primer elemento; los nodos restantes conservan su identidad. key es un atributo reservado de React y no llega como una prop ordinaria al hijo.")
code('''export default function Showtimes({ times }) {
  if (times.length === 0) return <p>Sin funciones hoy</p>
  return <ul>{times.map((time) => <li key={time}>{time}</li>)}</ul>
}

export default function Synopsis({ text }) {
  return <p className="synopsis">{text}</p>
}

export default function AgentMessage({ author, text }) {
  return <p><strong>{author}:</strong> <span>{text}</span></p>
}''')
picture("showtimes.png", "Figura 6. Showtimes muestra horas y el caso de lista vacía de Ruta 91.", 2.0)
p("Se comprueba times.length === 0 antes del map. Usar times.length && (...) en la lista vacía puede dibujar un 0 suelto, porque React sí representa el número cero.")

heading("Desarrollo 7 Composición y flujo de props", True)
table(["Componente", "Props", "Responsabilidad"], [
    ["Header", "name, links", "Nombre del cine y navegación"],
    ["Footer", "contact", "Dirección, teléfono y correo"],
    ["Hero", "movie", "Película destacada y ancla a horarios"],
    ["MovieCard", "movie", "Imagen, título, valoración, sinopsis y horas"],
    ["MovieList", "movies", "map y claves estables para las tarjetas"],
    ["Showtimes", "times", "Horas o mensaje de lista vacía"],
    ["Synopsis", "text", "Sinopsis como texto literal"],
    ["AgentMessage", "author, text", "Mensaje con autor y contenido literal"],
], [1.2, 1.1, 4.2])
code('''App
├── Header(name, links)
├── Hero(movie=featured)
├── MovieList(movies=billboard)
│   └── MovieCard(movie) × 8
│       └── Synopsis(text=movie.synopsis)
├── Showtimes(times=featured.showtimes)
├── Showtimes(times=[])  — Ruta 91
├── Synopsis(text=featured.synopsis)
├── AgentMessage(author, text)
└── Footer(contact)''')
p("App importa los datos y decide qué enviar. Los componentes de presentación no importan movies.js ni hacen peticiones. Las pruebas cambian nombre, enlaces, contacto y película para comprobar que los hijos usan las props recibidas, en lugar de valores escritos directamente dentro de cada uno.")
p("La interfaz conserva los ocho registros completos. Se probaron ocho imágenes locales cargadas, ocho clasificaciones y ocho sinopsis disponibles. No se añadieron filtros, reservas ni una venta de entradas fuera del alcance de esta semana.")

heading("Desarrollo 8 Tres errores típicos de JSX", True)
p("Los ejemplos intencionales viven en frontend/lab-errors/ y se abren solo en desarrollo con ?case=class, ?case=key y ?case=roots. La entrada de producción no los importa. Sus fallos se registraron realmente en Edge y browser-results.json.")
table(["Caso", "Mensaje registrado y significado", "Corrección"], [
    ["class", "Invalid DOM property class. Did you mean className? Aviso de React; puede dibujar la página.", "Usar className en JSX."],
    ["Dos raíces", "Adjacent JSX elements must be wrapped in an enclosing tag. Error de transformación; Vite muestra el panel rojo.", "Envolver los nodos en <>...</> o en un elemento padre."],
    ["Sin key", 'Each child in a list should have a unique "key" prop. Aviso sobre identidad de los elementos.', "Asignar key={movie.id} al li devuelto por map."],
], [.9, 3.9, 1.7])
p("Los textos de los avisos se presentan con los argumentos de formato sustituidos. El JSON conserva el registro original de consola, incluidos sus marcadores %s. Las peticiones de los ejemplos aislados pueden registrar 404 o 500; la cartelera segura registra cero errores de consola.")
picture("error-roots.png", "Figura 7. Error real de Vite al devolver dos nodos raíz sin envolver.", 3.4)
code('return (<><h2>Primera raíz</h2><p>Segunda raíz</p></>)')

heading("Extensión del README Duelo y correcciones", True)
p("Referencia: https://github.com/Hellscythe25/dae-s09-react-ia, revisión 861176ca6b84f80446928c3fc2484aba2c1dceb0. Se conservaron sin cambios las pruebas docentes, movies.js y src/duel/ai/. Las respuestas de IA ya estaban incluidas en ese material; no se simula una conversación nueva con otro modelo.")
table(["Ejecución", "Resultado"], [
    ["Equipo inicial", "43 pruebas fallidas; ocho componentes pendientes"],
    ["IA original", "29 correctas, 14 fallidas; fallos en seis tareas"],
    ["Copia fixed inicial", "29 correctas, 14 fallidas"],
    ["Equipo terminado", "43 de 43 correctas"],
    ["Copia fixed corregida", "43 de 43 correctas"],
    ["Suite completa y repetición tras restaurar Synopsis", "47 de 47 correctas"],
    ["Compilación y análisis de código final", "npm run build y npm run lint terminan con código 0"],
], [3.25, 3.25])
table(["Tarea", "Fallo de la IA", "Cambio en fixed"], [
    ["T2 Footer", "Propiedad DOM class", "className"],
    ["T3 MovieCard", "Imagen sin alternativa", "alt={movie.title}"],
    ["T4 Showtimes", "Arreglo vacío verdadero y cero visible", "Condición explícita times.length === 0"],
    ["T5 MovieList", "key por índice; identidad inestable", "key={movie.id}"],
    ["T6 Synopsis", "HTML de terceros interpretado", "Interpolación {text}"],
    ["T7 Hero", "Espera film, recibe movie", "Desestructurar y usar movie"],
], [1.0, 2.9, 2.6])
p("T1 Header y T8 AgentMessage eran correctos en la IA original. fixed:init copió las respuestas antes de editarlas; nunca se corrigió ai/. El modo solutions queda reservado al docente y no se usó.")

heading("Datos de terceros y experimento controlado", True)
p("Se cambió temporalmente Synopsis para usar dangerouslySetInnerHTML con la misma sinopsis proporcionada. En el navegador se observó window.__xss === 1 y dos imágenes inyectadas en los lugares que reutilizan Synopsis. La carga solo establece esa bandera local del ejercicio.")
code('return <p dangerouslySetInnerHTML={{ __html: text }} />\n// Experimental version only; restored immediately after observation.')
p("El verificador de navegador restauró el archivo original dentro de finally. En una página nueva la versión segura no creó imágenes inyectadas y window.__xss quedó sin definir. La suite de 47 pruebas se repitió después de restaurarlo.")
table(["Estado", "Resultado observado"], [
    ["HTML inseguro temporal", "window.__xss = 1; 2 imágenes dentro de sinopsis"],
    ["Interpolación JSX restaurada", "window.__xss sin definir; 0 imágenes inyectadas"],
    ["Mensaje de agente en la versión final", "Etiquetas visibles como texto; no se convierten en órdenes"],
], [2.7, 3.8])
picture("untrusted-text.png", "Figura 8. Sinopsis y mensaje del agente representados literalmente en la versión final.", 2.1)
p("Mostrar texto literal conserva la información del tercero sin confiarle la estructura del documento. La autoría de un agente tampoco convierte el texto en HTML confiable. No se incluyó un servicio de IA ni se enviaron datos a un modelo externo.")

heading("Verificación de interfaz y adaptación de tamaño", True)
p(f"Se completaron {len(browser['checks'])} comprobaciones de navegador: HTTP 200, ocho tarjetas, clasificaciones y sinopsis, carga de imágenes, caso vacío, enlaces internos, ancla de horarios, texto hostil seguro, tres errores JSX y restauración del experimento. Se comprobó que no hay desbordamiento horizontal a 320, 390, 768, 1024 y 1440 píxeles.")
picture("mobile.png", "Figura 9. Vista móvil real de 390 píxeles; recorte superior de la captura completa.", 4.8, (0, 0, 390, 1000))
p("La cuadrícula usa cuatro columnas en pantallas amplias y dos en tamaños menores. La navegación se envuelve en móvil; los detalles de sinopsis conservan acceso con teclado. El documento no presenta estas comprobaciones como una auditoría integral de accesibilidad.")

heading("Entrega observaciones y rúbrica", True)
p("Repositorio: https://github.com/DiegoMagallanes11/Motor-de-plantillas-con-Django/tree/lab09-react")
p("El código React se ubica en frontend/. El documento y las evidencias están en deliverables/lab09/. LAB09.md explica instalación, scripts, estructura, correcciones y limitaciones. Las ramas anteriores permanecen disponibles.")
table(["Criterio de la rúbrica", "Evidencia aportada"], [
    ["Vite y servidor — 5 puntos", "Generador oficial, dependencias bloqueadas, servidor HTTP y captura real"],
    ["Componentes funcionales — 5 puntos", "Ocho responsabilidades, JSX, carpeta y estilos por componente"],
    ["Props padre e hijos — 5 puntos", "Matriz de props y pruebas con datos alternativos y listas reordenadas"],
    ["Repositorio y observaciones — 5 puntos", "Rama del curso, README, código, pruebas, resultados y esta guía"],
], [2.6, 3.9])
p("La rúbrica valora el trabajo por cuenta propia; esta entrega declara expresamente la asistencia recibida y no garantiza una calificación. Diego Magallanes Linares es el único integrante; no se inventa reparto entre compañeros.")
heading("Observaciones de reproducción")
code("git switch lab09-react\ncd frontend\nnpm ci\nnpm run dev\n# En otra terminal:\nnpm test\nnpm run duel:ai       # Falla de forma intencional\nnpm run duel:fixed    # Debe pasar\nnpm run build\nnpm run lint")
p("duel:ai permanece rojo como material de comparación. Los ejemplos lab-errors y ai/ están excluidos del análisis estático final por contener errores intencionales. Los componentes finales, fixed y las pruebas se revisan normalmente. La publicación en GitHub no equivale a un despliegue; la subida del Word al campus la realiza el estudiante.")

heading("Conclusiones", True)
for text in [
    "1. React y Vite permitieron crear y compilar la cartelera dentro del proyecto acumulativo. La instalación quedó reproducible mediante package.json y package-lock.json, y el servidor de desarrollo respondió correctamente por HTTP.",
    "2. Separar ocho componentes funcionales hizo visible la responsabilidad de cada uno. App compone la pantalla y entrega datos por props; los hijos de presentación no necesitan conocer el archivo de origen.",
    "3. Las listas con map necesitaron claves estables. Usar el id conservó la identidad de cada película al reordenar o eliminar elementos, mientras que el índice falló en esas comprobaciones.",
    "4. Los tres errores provocados mostraron dos niveles distintos: class y key generan avisos de React, mientras que dos raíces JSX sin envolver impiden transformar el archivo. Registrar el mensaje permitió aplicar una corrección concreta a cada caso.",
    "5. El duelo mostró que una respuesta de IA puede funcionar parcialmente y fallar en accesibilidad, listas, nombres de props o tratamiento de HTML. Las 14 pruebas fallidas de la copia se corrigieron sin modificar el verificador ni las respuestas originales.",
    "6. Interpolar las sinopsis y mensajes como texto evitó ejecutar HTML de terceros. El experimento temporal activó la bandera local esperada y la restauración devolvió el comportamiento seguro; las 47 pruebas principales y las 22 comprobaciones de navegador sustentan el resultado entregado.",
]:
    p(text)
heading("Referencias")
for text in [
    "Guía de Laboratorio 09 proporcionada como texto por el estudiante; copia en guia-referencia.txt.",
    "Repositorio extra del docente: https://github.com/Hellscythe25/dae-s09-react-ia",
    "Vite: https://vite.dev/guide/",
    "JSX: https://react.dev/learn/writing-markup-with-jsx",
    "Listas y claves: https://react.dev/learn/rendering-lists",
    "Props: https://react.dev/learn/passing-props-to-a-component",
]:
    p(text, size=9)

target = OUT / "Lab09_Diego_Magallanes_Linares.docx"
document.save(target)
with ZipFile(SOURCE) as source_zip, ZipFile(target) as target_zip:
    for name in source_zip.namelist():
        if name.startswith("word/media/"):
            assert source_zip.read(name) == target_zip.read(name)
print(target)
