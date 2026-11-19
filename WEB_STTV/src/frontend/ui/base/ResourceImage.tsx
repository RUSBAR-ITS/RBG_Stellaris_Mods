import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react';

const SttvImages = createContext<Record<string, string>>({});

export function SttvImageProvider({ images, children, onUnavailable }: { images?: Record<string, Blob | null>;
  children: ReactNode; onUnavailable: (id: string, reason: string) => void }) {
  const [loaded, setLoaded] = useState<{ source: typeof images; urls: Record<string, string> }>({ source: undefined, urls: {} });
  const cache = useRef(new Map<string, { url: string; image: HTMLImageElement; reported: boolean;
    ready: Promise<{ url: string | null; reason?: string }> }>());
  useEffect(() => () => {
    for (const entry of cache.current.values()) URL.revokeObjectURL(entry.url);
    cache.current.clear();
  }, []);
  useEffect(() => {
    let active = true;
    const pending = Object.entries(images ?? {}).filter((entry): entry is [string, Blob] => entry[1] !== null)
      .map(async ([id, blob]) => {
        if (!cache.current.has(id)) {
          const url = URL.createObjectURL(blob), image = new Image();
          image.src = url;
          cache.current.set(id, { url, image, reported: false,
            ready: image.decode().then(() => ({ url }), error => ({ url: null, reason: String(error) })) });
        }
        const entry = cache.current.get(id)!, result = await entry.ready;
        if (active && result.reason && !entry.reported) {
          entry.reported = true;
          onUnavailable(id, result.reason);
        }
        return [id, result.url] as const;
      });
    void Promise.all(pending).then(entries => {
      if (active) setLoaded({ source: images, urls: Object.fromEntries(entries.filter((entry): entry is readonly [string, string] => entry[1] !== null)) });
    });
    return () => { active = false; };
  }, [images, onUnavailable]);
  return <SttvImages.Provider value={loaded.source === images ? loaded.urls : {}}>{children}</SttvImages.Provider>;
}

export function SttvResourceImage({ id, label = '', className = '', measuring = false }:
  { id: string | null; label?: string; className?: string; measuring?: boolean }) {
  const urls = useContext(SttvImages), [failed, setFailed] = useState<string | null>(null);
  const url = id ? urls[id] : undefined;
  return <span className={`sttv-resource-image ${className}`}>
    {url && failed !== url && !measuring ? <img src={url} alt={label} onError={() => setFailed(url)} />
      : <span className="sttv-image-placeholder" role={label ? 'img' : undefined} aria-label={label || undefined} aria-hidden={!label}>◇</span>}
  </span>;
}
