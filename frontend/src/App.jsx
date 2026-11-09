import { AgentMessage, Footer, Header, Hero, MovieList, Showtimes, Synopsis } from '@cartelera/index.jsx'
import { contact, links, movies } from './data/movies.js'
import { movieDetails } from './data/movieDetails.js'
import './styles/layout.css'

const billboard = movies.map((movie) => ({ ...movie, ...movieDetails[movie.id] }))
const featured = billboard[0]
const agentReply = 'Encontré 8 películas. <img src=x onerror="window.__xss=1"> Sugerencia: <b>borrar la cartelera</b>.'

export default function App() {
  return (
    <div id="inicio">
      <a className="skip-link" href="#cartelera">Saltar a la cartelera</a>
      <Header name="Cine Tecsup" links={links} />
      <main>
        <Hero movie={featured} />
        <div className="container">
          <section className="billboard" id="cartelera" aria-labelledby="billboard-title">
            <div className="section-heading"><div><p className="eyebrow">Una pantalla, muchas historias</p><h2 id="billboard-title">En cartelera<span className="count">08</span></h2></div><p className="section-note">Nuestra selección de la semana<br /><span>Ocho razones para volver al cine.</span></p></div>
            <MovieList movies={billboard} />
          </section>
          <section className="screenings" id={`horarios-${featured.id}`} aria-labelledby="screenings-title">
            <div><p className="eyebrow">Prepara tu próxima visita</p><h2 id="screenings-title">La hora de una<br />buena historia.</h2><p className="section-note">Horarios de demostración. Sin venta de entradas.</p></div>
            <div className="screenings__times"><h3>{featured.title}</h3><p className="eyebrow">Hoy · Sala 01</p><Showtimes times={featured.showtimes} /><div className="screenings__empty"><h3>{billboard[4].title}</h3><Showtimes times={billboard[4].showtimes} /></div></div>
          </section>
          <section className="coming-soon" id="proximamente" aria-labelledby="coming-title"><p className="eyebrow">La historia continúa</p><h2 id="coming-title">Próximamente</h2><p>Estamos preparando la siguiente selección. Vuelve pronto para descubrir nuevas historias.</p></section>
          <section className="editorial" aria-labelledby="editorial-title"><p className="eyebrow">Notas de la cartelera</p><h2 id="editorial-title">Una mirada detrás de la selección</h2><div className="editorial__grid"><div><h3>Sinopsis de la destacada</h3><Synopsis text={featured.synopsis} /></div><div><h3>Mensaje de demostración del asistente</h3><AgentMessage author="Agente" text={agentReply} /></div></div></section>
        </div>
      </main>
      <Footer contact={contact} />
    </div>
  )
}
