import './Footer.css'

export default function Footer({ contact }) {
  return (
    <footer className="footer" id="contacto"><div className="container footer__grid">
      <div><p className="footer__wordmark">Nos vemos<br />en el cine.</p><p>Historias que merecen una pantalla grande.</p></div>
      <div><h2>Encuéntranos</h2><p>{contact.address}</p><a href={`tel:${contact.phone}`}>{contact.phone}</a><a href={`mailto:${contact.email}`}>{contact.email}</a></div>
      <div><h2>Sobre esta cartelera</h2><p>Proyecto académico de React.<br />Películas, valoraciones y contacto de demostración.</p><a href="#inicio">Volver al inicio ↑</a></div>
    </div><div className="container footer__bottom"><span>Cine Tecsup · Laboratorio 09</span><span>Diego Magallanes Linares · Equipo individual</span></div></footer>
  )
}
