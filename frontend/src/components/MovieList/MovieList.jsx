import MovieCard from '../MovieCard/MovieCard.jsx'
import './MovieList.css'

export default function MovieList({ movies }) {
  return <ul className="movie-list">{movies.map((movie) => <li key={movie.id}><MovieCard movie={movie} /></li>)}</ul>
}
