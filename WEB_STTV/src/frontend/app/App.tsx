import { useEffect, useRef, useState } from 'react';
import config from '../../../config/frontend/interface.json';
import type { SttvLanguage } from '../localization/model';
import { SttvLocalizationProvider } from '../localization/context';
import { SttvMainWindow } from '../views/MainWindow';
import { SttvMenuPanel } from '../ui/layout/MenuPanel';
import { SttvButton } from '../ui/base/Button';
import { SttvLanguageSelector, SttvMenuToggle, SttvThemeToggle } from '../ui/composite/Settings';
import { SttvTechnologyField } from '../ui/layout/TechnologyField';
import { sttvUseDatabase } from './useDatabase';
import { sttvStatusMessage } from './status';
import { sttvDownloadReport } from './report';

export function SttvApp() {
  const [language, setLanguage] = useState(config.initialLanguage as SttvLanguage);
  const [theme, setTheme] = useState(config.initialTheme);
  const [expanded, setExpanded] = useState(config.initialMenuExpanded);
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [exportFailed, setExportFailed] = useState(false);
  const { opening, controller } = sttvUseDatabase();
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => { document.documentElement.lang = language; }, [language]);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  useEffect(() => { setSelected({}); setExportFailed(false); }, [opening.operationId]);
  const completed = ['ready', 'empty', 'error'].includes(opening.status);
  function save() {
    try { sttvDownloadReport(opening); setExportFailed(false); }
    catch { setExportFailed(true); }
  }
  const actions = <>
    {opening.status === 'loading'
      ? <SttvButton label={{ id: 'sttv_cancel' }} onClick={() => controller.cancel()} border="hover" />
      : <>
        {opening.status === 'error' && <SttvButton label={{ id: 'sttv_retry' }} onClick={() => controller.retry()} border="hover" />}
        <SttvButton label={{ id: 'sttv_open_database' }} onClick={() => input.current?.click()} border="hover" />
        {completed && <SttvButton label={{ id: 'sttv_save_report' }} onClick={save} border="hover" />}
      </>}
  </>;
  return <SttvLocalizationProvider language={language} data={opening.data}>
    <input type="file" multiple accept=".json,application/json" hidden ref={input} onChange={event => {
      const files = Array.from(event.currentTarget.files ?? []);
      event.currentTarget.value = '';
      if (files.length) controller.open(files);
    }} />
    <SttvMainWindow status={exportFailed ? { id: 'sttv_export_failed' } : sttvStatusMessage(opening, language)}
      menu={<SttvMenuPanel expanded={expanded} actions={actions}
        settings={<SttvLanguageSelector value={language} onChange={setLanguage} />}
        buttons={<>
          <SttvMenuToggle expanded={expanded} onToggle={() => setExpanded(value => !value)} />
          {expanded && <SttvThemeToggle theme={theme} onToggle={() => setTheme(value => value === 'night' ? 'day' : 'night')} />}
        </>} />}>
      {opening.status === 'ready' && opening.data && <SttvTechnologyField key={opening.operationId}
        data={opening.data} selected={selected} onSelect={(id, value) => setSelected(previous => ({ ...previous, [id]: value }))} />}
    </SttvMainWindow>
  </SttvLocalizationProvider>;
}
