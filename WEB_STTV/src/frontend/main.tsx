import { createRoot } from 'react-dom/client';
import { SttvApp } from './app/App';
import config from '../../config/frontend/interface.json';
import connections from '../../config/frontend/connections.json';
import card from '../../config/frontend/card.json';
import './styles/dictionary.css';
import './styles/elements.css';
import './styles/global.css';

for (const [name, value] of Object.entries(config)) {
  if (typeof value === 'number') document.documentElement.style.setProperty(
    `--sttv-${name.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`)}`, `${value}px`);
}
document.documentElement.style.setProperty('--sttv-connection-stroke-width', `${connections.strokeWidth}px`);
for (const [name, value] of Object.entries(card)) document.documentElement.style.setProperty(
  `--sttv-card-${name.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`)}`, `${value}px`);
createRoot(document.getElementById('root')!).render(<SttvApp />);
