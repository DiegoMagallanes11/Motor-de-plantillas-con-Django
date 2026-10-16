# Pulso — Laboratorio 06 de Django

Portal académico de noticias para demostrar herencia de plantillas, fragmentos
reutilizables, variables, etiquetas, filtros y gestión desde Django Admin.

**Estudiante:** Diego Magallanes Linares. Desarrollo realizado con asistencia de
Codex. Las noticias y la redacción del portal son ficticias. Las ilustraciones
geométricas se generan localmente con Pillow y no requieren imágenes externas.

## Instalación en Windows

Requisitos: Python 3.12 o superior y Git. Implementación verificada con Python
3.14.5, Django 6.0.9 y Pillow 12.3.0.

```powershell
git clone https://github.com/DiegoMagallanes11/Motor-de-plantillas-con-Django.git
cd Motor-de-plantillas-con-Django
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/setup_local.py
.\.venv\Scripts\python.exe manage.py runserver
```

Si la creación del entorno falla al instalar pip, se puede completar con:

```powershell
python -m pip --python .\.venv\Scripts\python.exe install -r requirements.txt
```

Abrir http://127.0.0.1:8000/ y http://127.0.0.1:8000/admin/.
El usuario local es `diego`. La contraseña aleatoria se guarda únicamente en
`.private/admin-access.txt`, excluido del repositorio. El script preserva un
usuario existente y no reemplaza su contraseña. Si se necesita recuperarla:

```powershell
.\.venv\Scripts\python.exe manage.py changepassword diego
```

`setup_local.py` crea una clave aleatoria en `.env`, aplica las migraciones y
carga seis noticias en tres categorías. No sobrescribe noticias ya existentes.
El comando de carga también puede ejecutarse por separado:

```powershell
.\.venv\Scripts\python.exe manage.py seed_news
```

El archivo `.env.example` documenta las variables. Si se configura manualmente
`.env`, reemplazar la clave de ejemplo por una clave aleatoria. Los valores ya
exportados en el entorno tienen prioridad. La configuración incluida es para
desarrollo local; publicar el repositorio no despliega una aplicación web.

## Estructura

```text
config/                  Configuración y rutas principales
news/
  models.py              Article, Category y Author
  admin.py               Listados, filtros y búsquedas
  views.py               Consulta de noticias publicadas
  urls.py                Rutas con namespace news
  context_processors.py  Categorías de navegación
  migrations/            Esquema versionado
  management/commands/seed_news.py
  tests.py               Diez pruebas funcionales
templates/
  base.html              Estructura común y bloques
  news/
    _article_card.html   Tarjeta compartida
    home.html            Portada
    detail.html          Detalle y escapado
    category.html        Listado por categoría
static/news/css/styles.css
scripts/setup_local.py   Preparación local reproducible
deliverables/            Guía Word y evidencias
```

La base de datos, medios generados, entorno virtual y credenciales no se suben
a Git. Una instalación nueva los reconstruye con las migraciones y la carga.

## Rutas

| Nombre | Ruta | Función |
|---|---|---|
| `news:home` | `/` | Noticias publicadas |
| `news:detail` | `/noticias/<slug>/` | Detalle de noticia |
| `news:category` | `/categorias/<slug>/` | Noticias de una categoría |
| `admin:index` | `/admin/` | Administración |

## Decisiones y observaciones

- `Article.author` utiliza `ForeignKey` con `PROTECT`; no se elimina un autor
  que todavía tiene noticias. `Article.categories` es una relación muchos a
  muchos. La imagen es opcional y tiene un estado visual alternativo.
- Las vistas solo publican noticias habilitadas cuya fecha no sea futura.
  `select_related` y `prefetch_related` recuperan las relaciones del listado.
- Las tres páginas heredan de `base.html`. Portada y categoría incluyen
  `_article_card.html` con `only` para compartir un fragmento con contexto claro.
- Los enlaces internos utilizan `{% url %}`; el CSS utiliza `{% load static %}`.
  Las imágenes cargadas se obtienen desde `featured_image.url`.
- Se usan `for`, `empty`, `if`, `date`, `truncatewords` y `length`. Las consultas
  y decisiones de publicación permanecen en Python.
- El detalle mantiene el escapado automático. `linebreaksbr` conserva saltos de
  línea y escapa el texto de entrada; no se emplea `safe`. En la noticia
  «Diseñar herramientas que todos puedan usar» aparece literalmente
  `<strong>Texto de prueba</strong>` en lugar de aplicar negrita.
- Los filtros, búsquedas, edición y publicación se gestionan desde el panel.
  Para comprobar cambios, editar una noticia, guardar y recargar su detalle.

## Verificación

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test --verbosity 2
```

Las diez pruebas cubren herencia y recorte, escapado y relaciones, filtrado por
categoría, listas vacías, 404 y visibilidad, edición desde el administrador,
búsqueda y filtros, acceso autenticado y protección de autores.

Para comprobar manualmente `{% empty %}`, puede crearse temporalmente una
categoría sin noticias. Al terminar, elimínala para conservar las tres categorías
de la carga inicial. Las pruebas automáticas usan una base temporal independiente.

`scripts/browser_evidence.cjs` es una herramienta auxiliar de captura que depende
del runtime de automatización del entorno donde se preparó la entrega; no es
necesaria para instalar ni usar el portal. Su resultado registra por separado las
comprobaciones visuales realmente ejecutadas.

## Entrega

La guía Word describe los trece pasos, incluye las evidencias obtenidas, las
pruebas, observaciones y conclusiones. El archivo debe subirse manualmente al
campus virtual. La publicación en GitHub y la entrega en el campus son acciones
distintas.
