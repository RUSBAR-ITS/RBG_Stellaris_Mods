import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import config from '../../../config/frontend/interface.json';
import type { SttvLanguage } from '../localization/model';
import { SttvLocalizationProvider } from '../localization/context';
import { SttvMainWindow } from '../views/MainWindow';
import { SttvMenuPanel } from '../ui/layout/MenuPanel';
import { SttvButton } from '../ui/base/Button';
import { SttvLanguageSelector, SttvMenuToggle, SttvThemeToggle } from '../ui/composite/Settings';
import { SttvZoomSelector, sttvZoomSettings } from '../ui/composite/ZoomSelector';
import { SttvTechnologyField } from '../ui/layout/TechnologyField';
import { sttvUseDatabase } from './useDatabase';
import { sttvStatusMessage } from './status';
import { sttvDownloadReport } from './report';
import { sttvPrepareField } from './field';
import { SttvCardMeasurement } from '../ui/composite/CardMeasurement';
import { SttvImageProvider } from '../ui/base/ResourceImage';
import type { SttvCatalog } from '../data/model';
import { sttvDiagnostic, type SttvDiagnostic } from '../workers/diagnostics';
import { sttvUseDlc } from './useDlc';
import { SttvDlcSettings } from '../views/DlcSettings';
import navigation from '../../../config/frontend/dlc.json';

export function SttvApp() {
  const [language, setLanguage] = useState(config.initialLanguage as SttvLanguage);
  const [theme, setTheme] = useState(config.initialTheme);
  const [expanded, setExpanded] = useState(config.initialMenuExpanded);
  const [zoom, setZoom] = useState(sttvZoomSettings.initialPercent);
  const [exportFailed, setExportFailed] = useState(false);
  const [view, setView] = useState('tree');
  const { opening: loaded, controller } = sttvUseDatabase();
  const dlc = sttvUseDlc(loaded, controller, view);
  const [imageIssues, setImageIssues] = useState<{ operation: number; items: SttvDiagnostic[] }>({ operation: 0, items: [] });
  const imageUnavailable = useCallback((id: string, reason: string) => setImageIssues(previous => ({
    operation: loaded.operationId, items: [...(previous.operation === loaded.operationId ? previous.items : []),
      sttvDiagnostic('image_unavailable', 'preparing', { id, reason })],
  })), [loaded.operationId]);
  const [measurement, setMeasurement] = useState<{ data: SttvCatalog | null; language: string; height: number } | null>(null);
  const measured = measurement?.data === loaded.data && measurement?.language === language;
  const onMeasure = useCallback((height: number) => setMeasurement({ data: loaded.data, language, height }), [loaded.data, language]);
  const { opening, layout } = useMemo(() => measured ? sttvPrepareField(loaded, language, measurement!.height)
    : { opening: loaded, layout: null }, [loaded, language, measured, measurement]);
  const previousField = useRef<{ operation: number; data: SttvCatalog; layout: NonNullable<typeof layout> } | null>(null);
  if (layout && opening.data) previousField.current = { operation: opening.operationId, data: opening.data, layout };
  const field = previousField.current?.operation === opening.operationId && opening.status === 'ready' ? previousField.current : null;
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => { document.documentElement.lang = language; }, [language]);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  useEffect(() => { setExportFailed(false); }, [opening.operationId]);
  const completed = ['ready', 'empty', 'error'].includes(opening.status);
  function save() {
    try { sttvDownloadReport({ ...opening, diagnostics: [...opening.diagnostics,
      ...(imageIssues.operation === opening.operationId ? imageIssues.items : [])] }, layout?.report); setExportFailed(false); }
    catch { setExportFailed(true); }
  }
  const actions = <>
    {navigation.navigation.map(id => <SttvButton key={id} label={{ id: `sttv_nav_${id}` }}
      current={view === id} onClick={() => setView(id)} border="never" />)}
    {opening.status === 'loading'
      ? <SttvButton label={{ id: 'sttv_cancel' }} onClick={() => controller.cancel()} border="hover" />
      : <>
        {opening.status === 'error' && <SttvButton label={{ id: 'sttv_retry' }} onClick={() => controller.open(opening.files)} border="hover" />}
        <SttvButton label={{ id: 'sttv_open_database' }} onClick={() => {
          if (input.current && 'webkitdirectory' in input.current) input.current.click();
          else controller.unsupportedDirectory();
        }} border="hover" />
        {completed && <SttvButton label={{ id: 'sttv_save_report' }} onClick={save} border="hover" />}
      </>}
  </>;
  return <SttvLocalizationProvider language={language} data={opening.data}>
    <SttvImageProvider key={opening.operationId} images={opening.data?.images} onUnavailable={imageUnavailable}>
    {opening.status === 'ready' && opening.data && !measured && <SttvCardMeasurement data={opening.data} onMeasure={onMeasure} />}
    <input type="file" {...{ webkitdirectory: '' }} hidden ref={input} onChange={event => {
      const files = Array.from(event.currentTarget.files ?? []);
      event.currentTarget.value = '';
      if (files.length) controller.open(files);
    }} />
    <SttvMainWindow status={exportFailed ? { id: 'sttv_export_failed' } : dlc.status ?? sttvStatusMessage(opening, language)}
      menu={<SttvMenuPanel expanded={expanded} actions={actions}
        settings={<><SttvLanguageSelector value={language} onChange={setLanguage} />
          {view === 'tree' && <SttvZoomSelector value={zoom} onChange={setZoom} />}</>}
        buttons={<>
          <SttvMenuToggle expanded={expanded} onToggle={() => setExpanded(value => !value)} />
          {expanded && <SttvThemeToggle theme={theme} onToggle={() => setTheme(value => value === 'night' ? 'day' : 'night')} />}
        </>} />}>
      <div className="sttv-view-slot" data-active={view === 'tree'} aria-hidden={view !== 'tree'} inert={view !== 'tree'}>
        {field && <SttvTechnologyField key={opening.operationId} data={field.data} layout={field.layout} scale={zoom / 100} />}
      </div>
      <div className="sttv-view-slot" data-active={view === 'dlc'} aria-hidden={view !== 'dlc'} inert={view !== 'dlc'}>
        <SttvDlcSettings key={opening.operationId} data={opening.data} state={dlc} />
      </div>
    </SttvMainWindow>
    </SttvImageProvider>
  </SttvLocalizationProvider>;
}
