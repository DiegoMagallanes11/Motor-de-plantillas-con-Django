import { createRoot } from 'react-dom/client'

function InvalidClass() {
  return <footer class="footer">Ejemplo intencional de class en JSX.</footer>
}

function MissingKey() {
  return <ul>{['Película A', 'Película B'].map((title) => <li>{title}</li>)}</ul>
}

const example = new URLSearchParams(window.location.search).get('case')
if (example === 'roots') {
  const { default: TwoRoots } = await import('./TwoRoots.jsx')
  createRoot(document.getElementById('root')).render(<TwoRoots />)
} else {
  createRoot(document.getElementById('root')).render(example === 'class' ? <InvalidClass /> : <MissingKey />)
}
