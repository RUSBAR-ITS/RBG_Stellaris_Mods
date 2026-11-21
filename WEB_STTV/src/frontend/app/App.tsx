import { useEffect, useState, type CSSProperties } from 'react';
import config from '../../../config/frontend/interface.json';
import controls from '../../../config/frontend/dlc.json';
import type { SttvLanguage } from '../localization/model';
import { SttvLocalizationProvider } from '../localization/context';
import { SttvMainWindow } from '../views/MainWindow';
import { SttvMenuPanel } from '../ui/layout/MenuPanel';
import { SttvButton } from '../ui/base/Button';
import { SttvSwitch } from '../ui/base/Switch';
import { SttvText } from '../ui/base/Text';
import { SttvLanguageSelector, SttvMenuToggle, SttvThemeToggle } from '../ui/composite/Settings';
import { SttvZoomSelector, sttvZoomSettings } from '../ui/composite/ZoomSelector';
import { SttvTabs } from '../ui/composite/Tabs';
import { DlcSettings } from '../views/DlcSettings';
import { ReferenceField } from '../views/ReferenceField';
import { useReferenceTree } from './useReferenceTree';

type View = 'tree' | 'system' | 'game';
type GameTab = 'dlc' | 'empire';
const pages: View[] = ['tree', 'system', 'game'];
const switchStyle = { '--sttv-switch-width': controls.switchWidth + 'px', '--sttv-switch-height': controls.switchHeight + 'px',
  '--sttv-switch-inset': controls.switchInset + 'px' } as CSSProperties;

export function SttvApp() {
  const [language, setLanguage] = useState(config.initialLanguage as SttvLanguage);
  const [theme, setTheme] = useState(config.initialTheme);
  const [expanded, setExpanded] = useState(config.initialMenuExpanded);
  const [zoom, setZoom] = useState(sttvZoomSettings.initialPercent);
  const [view, setView] = useState<View>('tree');
  const [tab, setTab] = useState<GameTab>('dlc');
  const [referenceMode, setReferenceMode] = useState(true);
  const reference = useReferenceTree();

  useEffect(() => { document.documentElement.lang = language; }, [language]);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  function navigate(page: View) {
    setView(page);
    if (page === 'tree' && referenceMode) void reference.open();
    if (page === 'game' && tab === 'dlc') void reference.loadDlcs();
  }
  function selectGameTab(next: GameTab) {
    setTab(next);
    if (next === 'dlc') void reference.loadDlcs();
  }
  return <SttvLocalizationProvider language={language} data={reference.tree}>
    <SttvMainWindow status={view === 'game' && tab === 'dlc' && reference.catalogError ? reference.catalogError
      : !referenceMode && view === 'tree' ? { id: 'sttv_empire_mode' } : reference.status ?? { id: 'sttv_ref_idle' }}
      menu={<SttvMenuPanel expanded={expanded}
        actions={pages.map(page => <SttvButton key={page} label={{ id: `sttv_nav_${page}` }} current={view === page}
          onClick={() => navigate(page)} border="never" />)}
        settings={<><SttvLanguageSelector value={language} onChange={setLanguage} />
          {view === 'tree' && <SttvZoomSelector value={zoom} onChange={setZoom} />}</>}
        buttons={<><SttvMenuToggle expanded={expanded} onToggle={() => setExpanded(!expanded)} />
          {expanded && <SttvThemeToggle theme={theme} onToggle={() => setTheme(theme === 'night' ? 'day' : 'night')} />}</>} />}>
      <div className="sttv-view-slot" data-active={view === 'tree'} aria-hidden={view !== 'tree'} inert={view !== 'tree'}>
        {referenceMode ? reference.tree && <ReferenceField key={reference.tree.id + language} tree={reference.tree}
          language={language} scale={zoom / 100} /> : <p><SttvText text={{ id: 'sttv_empire_placeholder' }} /></p>}
      </div>
      {view === 'system' && <SttvTabs label="sttv_nav_system" selected="database" onSelect={() => {}}
        tabs={[{ id: 'database', label: 'sttv_tab_database', content:
          <SttvButton label={{ id: 'sttv_ref_clear' }} disabled={reference.busy} onClick={reference.clear} /> }]} />}
      {view === 'game' && <div className="sttv-view-slot" style={switchStyle}>
        <SttvTabs<GameTab> label="sttv_nav_game" selected={tab} onSelect={selectGameTab} tabs={[
          { id: 'dlc', label: 'sttv_tab_dlc', content: <DlcSettings state={reference} referenceMode={referenceMode} /> },
          { id: 'empire', label: 'sttv_tab_empire', content: <>
            <div className="sttv-empire-mode"><SttvText text={{ id: 'sttv_reference_mode' }} />
              <SttvSwitch label={{ id: 'sttv_reference_mode' }} checked={referenceMode} onChange={() => setReferenceMode(!referenceMode)} /></div>
            <fieldset className="sttv-empire-inputs" disabled={referenceMode} />
          </> },
        ]} />
      </div>}
    </SttvMainWindow>
  </SttvLocalizationProvider>;
}
