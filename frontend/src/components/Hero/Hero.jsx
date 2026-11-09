import './Hero.css'

export default function Hero({ movie }) {
  return (
    <section aria-label="Destacada" className="hero"><div className="container hero__inner">
      <p className="eyebrow hero__eyebrow"><span aria-hidden="true">●</span> Esta semana en pantalla</p>
      <h2>{movie.title}</h2>
      <p className="hero__tagline">Hay historias que se quedan<br />cuando se encienden las luces.</p>
      <div className="hero__facts"><span>{movie.classification ?? 'Clasificación pendiente'}</span><span>{movie.genre ?? 'Cine'}</span><span>★ {movie.rating} / 5</span></div>
      <a className="button" href={`#horarios-${movie.id}`}>Ver horarios <span aria-hidden="true">↗</span></a>
      <p className="hero__caption">Una selección para mirar de otra manera.</p>
    </div><span className="hero__edition" aria-hidden="true">SELECCIÓN<br />09 / 26</span></section>
  )
}
