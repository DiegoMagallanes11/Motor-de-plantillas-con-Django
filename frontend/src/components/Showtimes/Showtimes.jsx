import './Showtimes.css'

export default function Showtimes({ times }) {
  if (times.length === 0) return <p className="showtimes__empty">Sin funciones hoy</p>
  return <ul className="showtimes">{times.map((time) => <li key={time}><time>{time}</time></li>)}</ul>
}
