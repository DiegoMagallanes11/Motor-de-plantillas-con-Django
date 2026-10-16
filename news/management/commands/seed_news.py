"""Create reproducible fictional articles and original geometric illustrations."""
from datetime import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw

from news.models import Article, Author, Category

CATEGORIES = [
    ("Tecnología", "tecnologia", "Herramientas e ideas que transforman nuestra forma de crear."),
    ("Cultura", "cultura", "Espacios, personas y expresiones que nos acercan."),
    ("Ciencia", "ciencia", "Preguntas que abren nuevas formas de entender el mundo."),
]
ARTICLES = [
    ("Un laboratorio de ideas para aprender a programar", "laboratorio-de-ideas", 0,
     "Un grupo de estudiantes convierte sus primeras líneas de código en un portal colaborativo. El proyecto reúne diseño, programación y una nueva forma de aprender en comunidad.",
     "En este escenario de ejemplo, un equipo organiza sesiones de programación para construir herramientas útiles para su comunidad. Cada encuentro comienza con una pregunta concreta y termina con una pequeña mejora verificable.\n\nEl portal separa los datos de su presentación. Los autores redactan desde el administrador y las plantillas muestran el resultado con una estructura compartida.\n\nLa primera lección es sencilla: avanzar en pasos pequeños permite entender mejor cada decisión y corregir errores a tiempo."),
    ("Bibliotecas que abren espacio a nuevas historias", "bibliotecas-nuevas-historias", 1,
     "Lectura, conversación y creación se encuentran en una biblioteca imaginaria que invita a compartir historias. Sus actividades acercan a vecinos de distintas generaciones en un mismo espacio.",
     "La biblioteca de esta noticia ficticia propone un taller semanal para compartir relatos. Las personas participantes llevan recuerdos, fotografías y preguntas que sirven como punto de partida.\n\nEl objetivo no es competir por una historia perfecta, sino escuchar experiencias diferentes. Una mesa común se convierte en un lugar de encuentro y aprendizaje."),
    ("Mirar el cielo también es hacer preguntas", "mirar-el-cielo", 2,
     "Un encuentro de observación invita a reconocer patrones en el cielo y registrar preguntas. La actividad de ejemplo propone aprender a observar antes de buscar respuestas definitivas.",
     "En una jornada ficticia de observación, estudiantes registran lo que ven y comparan sus notas. Los dibujos permiten reconocer cambios y formular preguntas para una próxima sesión.\n\nLa actividad muestra que observar con cuidado y conservar registros son hábitos valiosos para aprender ciencia. No se presentan descubrimientos ni datos de una investigación real."),
    ("Diseñar herramientas que todos puedan usar", "herramientas-accesibles", 0,
     "Un prototipo académico explora enlaces claros, navegación con teclado y pantallas adaptables. Las decisiones de diseño buscan que más personas puedan recorrer el contenido con comodidad.",
     "El prototipo de ejemplo incorpora una estructura de encabezados, enlaces descriptivos y un acceso directo al contenido principal. También adapta las tarjetas al ancho de pantalla.\n\nLas pruebas incluyen recorrer los enlaces con el teclado y comprobar que las imágenes no bloquean la comprensión del texto.\n\nPrueba de escapado automático:\n<strong>Texto de prueba</strong>\nLa etiqueta anterior se almacena en el cuerpo para verificar cómo la plantilla la presenta."),
    ("El barrio se cuenta a través de sus colores", "colores-del-barrio", 1,
     "Un taller de ilustración imaginario transforma recuerdos cotidianos en composiciones de color. Las piezas reúnen miradas distintas sobre las calles, los encuentros y la vida del barrio.",
     "Las personas participantes del taller ficticio eligen una escena cotidiana y la representan con formas simples. Algunas dibujan una plaza; otras, una ventana o un trayecto habitual.\n\nAl reunir las piezas, el grupo reconoce que un mismo lugar puede contarse desde experiencias muy distintas. El proceso creativo se documenta para una exposición de ejemplo."),
    ("Pequeños jardines para observar grandes cambios", "pequenos-jardines", 2,
     "Un jardín de práctica permite registrar cambios en hojas, tallos y condiciones de luz. El ejercicio invita a comparar observaciones y aprender a llevar un registro ordenado.",
     "En este ejercicio ficticio se prepara un registro de observación de plantas. Cada entrada describe la fecha, las condiciones y los cambios visibles, sin atribuir efectos que no se hayan comprobado.\n\nEl valor de la actividad está en mantener notas consistentes y distinguir lo observado de las posibles explicaciones. El jardín funciona como un recurso didáctico, no como un experimento publicado."),
]


def illustration(index):
    palettes = [
        ("#dce8cc", "#254e41", "#afcc63"),
        ("#eedbc9", "#a75a40", "#d8b26e"),
        ("#d4dfeb", "#293e64", "#8fabc9"),
        ("#e5dfef", "#615378", "#b6a2cf"),
        ("#f1d8ca", "#b45e49", "#db9f55"),
        ("#d5e3d5", "#3e6b50", "#9aba75"),
    ]
    background, dark, accent = palettes[index]
    image = Image.new("RGB", (1200, 700), background)
    draw = ImageDraw.Draw(image)
    if index in (0, 3):
        draw.rounded_rectangle((220, 130, 950, 540), 22, fill=dark)
        draw.rounded_rectangle((250, 165, 920, 495), 12, fill=background)
        for row, width in enumerate((240, 380, 180, 310)):
            draw.rounded_rectangle((310, 225 + row * 52, 310 + width, 241 + row * 52), 7, fill=accent)
        draw.polygon([(170, 555), (1000, 555), (1080, 600), (110, 600)], fill=dark)
        draw.ellipse((825, 70, 1050, 295), fill=accent)
    elif index in (1, 4):
        for column in range(6):
            x = 230 + column * 120
            top = 140 + (column % 3) * 42
            color = dark if column % 2 else accent
            draw.rounded_rectangle((x, top, x + 90, 550), 8, fill=color)
            draw.line((x + 20, top + 40, x + 70, top + 40), fill=background, width=6)
        draw.rectangle((160, 552, 1040, 575), fill=dark)
    elif index == 2:
        draw.ellipse((370, 110, 825, 565), fill=dark)
        draw.ellipse((470, 110, 825, 465), fill=accent)
        for x, y in ((170, 160), (1000, 200), (260, 490), (960, 540), (880, 90)):
            draw.line((x - 18, y, x + 18, y), fill=dark, width=4)
            draw.line((x, y - 18, x, y + 18), fill=dark, width=4)
        draw.arc((220, 240, 1000, 480), 0, 330, fill=dark, width=7)
    else:
        for x, height in ((330, 260), (600, 160), (870, 230)):
            draw.line((x, 490, x, height), fill=dark, width=12)
            draw.ellipse((x - 100, height, x, height + 100), fill=dark)
            draw.ellipse((x, height + 65, x + 100, height + 165), fill=accent)
            draw.polygon([(x - 80, 490), (x + 80, 490), (x + 55, 595), (x - 55, 595)], fill=dark)
    output = BytesIO()
    image.save(output, format="JPEG", quality=90)
    return output.getvalue()


class Command(BaseCommand):
    help = "Load six fictional articles in three categories without duplicating them."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = []
        for name, slug, description in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": name, "description": description}
            )
            categories.append(category)
        author, _ = Author.objects.get_or_create(
            name="Redacción Pulso",
            defaults={"bio": "Equipo editorial ficticio del portal académico Pulso."},
        )
        for index, (title, slug, category_index, summary, body) in enumerate(ARTICLES):
            article, created = Article.objects.get_or_create(slug=slug, defaults={
                "title": title, "summary": summary, "body": body, "author": author,
                "published_at": datetime(2026, 10, 15 - index, 9, tzinfo=ZoneInfo("America/Lima")),
            })
            if created:
                article.categories.set([categories[category_index]])
            if not article.featured_image:
                article.featured_image.save(
                    f"{slug}.jpg", ContentFile(illustration(index)), save=True
                )
        self.stdout.write(self.style.SUCCESS("Six sample articles and three categories are available."))
