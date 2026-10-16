"""Proposed exercise statements and independent, fixed-data answer keys."""
QUESTIONS = [
    {
        "number": 1,
        "text": "Artículos publicados desde el 05/10/2026 a las 00:00 en Lima, incluido el límite; ordenar por id.",
        "expected": [2, 4, 5, 6, 7, 8, 9, 10, 11],
        "budget": 1,
    },
    {
        "number": 2,
        "text": "Artículos publicados de autores cuyo perfil indica Lima y cuya categoría es Tecnología; ordenar por id.",
        "expected": [1, 2, 7, 10], "budget": 1,
    },
    {
        "number": 3,
        "text": "Artículos publicados que pertenecen a Tecnología o no tienen categoría; ordenar por id.",
        "expected": [1, 2, 3, 7, 9, 10], "budget": 1,
    },
    {
        "number": 4,
        "text": "Autores con al menos un artículo publicado etiquetado django, sin repetir autores; ordenar por id.",
        "expected": [1, 3], "budget": 1,
    },
    {
        "number": 5,
        "text": "Todos los artículos con n_comments y n_tags, incluidos comentarios no aprobados; ordenar por id.",
        "expected": [
            [1, 4, 2], [2, 2, 2], [3, 0, 1], [4, 2, 1],
            [5, 3, 2], [6, 1, 2], [7, 0, 2], [8, 2, 1],
            [9, 1, 0], [10, 0, 2], [11, 0, 1], [12, 0, 1],
        ],
        "budget": 1,
    },
    {
        "number": 6,
        "text": "Autores que no tienen ningún comentario aprobado en ninguno de sus artículos, incluidos autores sin artículos; ordenar por id.",
        "expected": [2, 5, 6, 7], "budget": 1,
    },
    {
        "number": 7,
        "text": "Categorías con al menos dos artículos publicados y su n_articles publicado; ordenar por id.",
        "expected": [[1, 4], [2, 3], [3, 2]], "budget": 1,
    },
    {
        "number": 8,
        "text": "Los once artículos publicados más recientes, ordenados por fecha descendente e id descendente en empates; renderizar autor y etiquetas con máximo dos consultas.",
        "expected": [11, 10, 9, 8, 7, 6, 5, 4, 2, 3, 1], "budget": 2,
    },
]
