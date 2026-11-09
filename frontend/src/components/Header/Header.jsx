import './Header.css'

export default function Header({ name, links }) {
  return (
    <header className="header"><div className="container header__inner">
      <a className="header__brand" href="#inicio"><span className="header__mark" aria-hidden="true">c.</span><h1>{name}</h1></a>
      <nav aria-label="Principal"><ul className="header__links">
        {links.map((link) => <li key={link.href}><a href={link.href}>{link.label}</a></li>)}
      </ul></nav>
      <span className="header__location">Santa Anita, Lima ↗</span>
    </div></header>
  )
}
