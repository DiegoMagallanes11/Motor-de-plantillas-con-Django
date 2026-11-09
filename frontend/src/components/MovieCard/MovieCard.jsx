import Synopsis from '../Synopsis/Synopsis.jsx'
import './MovieCard.css'

export default function MovieCard({ movie }) {
  return (
    <article className="movie-card" id={`pelicula-${movie.id}`}>
      <div className="movie-card__poster"><img src={movie.image} alt={movie.title} loading="lazy" width="480" height="600" />{movie.classification && <span className="movie-card__classification">{movie.classification}</span>}</div>
      <div className="movie-card__heading"><h3>{movie.title}</h3><p className="movie-card__rating">★ {movie.rating}</p></div>
      {movie.genre && <p className="movie-card__genre">{movie.genre}</p>}
      <details className="movie-card__details"><summary>Sinopsis</summary><Synopsis text={movie.synopsis} /></details>
      <p className="movie-card__times-label">Funciones de hoy</p>
      <p className={`movie-card__times${movie.showtimes.length === 0 ? ' movie-card__times--empty' : ''}`}>{movie.showtimes.length > 0 ? movie.showtimes.join(' · ') : 'Sin funciones hoy'}</p>
    </article>
  )
}
