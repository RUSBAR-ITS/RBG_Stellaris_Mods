import { useState } from 'react';

export function sttvAssetUrl(path: string) {
  const base = (import.meta.env.VITE_STTV_ASSETS_URL ?? '/game-assets').replace(/\/$/, '');
  return base + '/' + path.split('/').map(encodeURIComponent).join('/');
}

export function SttvResourceImage({ id, label = '', className = '', measuring = false }:
  { id: string | null; label?: string; className?: string; measuring?: boolean }) {
  const [failed, setFailed] = useState<string | null>(null);
  const url = id && sttvAssetUrl(id);
  return <span className={`sttv-resource-image ${className}`}>
    {url && failed !== url && !measuring ? <img src={url} alt={label} onError={() => setFailed(url)} />
      : <span className="sttv-image-placeholder" role={label ? 'img' : undefined} aria-label={label || undefined} aria-hidden={!label}>◇</span>}
  </span>;
}
