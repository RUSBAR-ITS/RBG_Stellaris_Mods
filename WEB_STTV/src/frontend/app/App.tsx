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
import { TreeTooltipContext } from './tooltipCache';
import { technologyLink, technologyRoute } from './technologyRoute';
import { SttvTechnologyPage } from '../views/TechnologyPage';

type View = 'tree' | 'system' | 'game';
type GameTab = 'dlc' | 'empire';
const pages: View[] = ['tree', 'system', 'game'];
const switchStyle = { '--sttv-switch-width': controls.switchWidth + 'px', '--sttv-switch-height': controls.switchHeight + 'px',
  '--sttv-switch-inset': controls.switchInset + 'px' } as CSSProperties;

export function SttvApp() {
  const [route, setRoute] = useState(() => technologyRoute(location.hash));
  const [language, setLanguage] = useState<SttvLanguage>(route?.language ?? config.initialLanguage as SttvLanguage);
  const [theme, setTheme] = useState(config.initialTheme);
  const [expanded, setExpanded] = useState(config.initialMenuExpanded);
  const [zoom, setZoom] = useState(sttvZoomSettings.initialPercent);
  const [view, setView] = useState<View>('tree');
  const [tab, setTab] = useState<GameTab>('dlc');
  const [systemTab, setSystemTab] = useState<'database' | 'tree'>('database');
  const [referenceMode, setReferenceMode] = useState(true);
  const reference = useReferenceTree(route?.enabled);
  const showTree = view === 'tree' && !route;
  useEffect(() => {
    function changed() {
      const next = technologyRoute(location.hash);
      setRoute(next);
      if (next?.language) setLanguage(next.language);
      if (!next && location.hash === '#/tree') setView('tree');
    }
    window.addEventListener('hashchange', changed);
    return () => window.removeEventListener('hashchange', changed);
  }, []);
  useEffect(() => {
    if (!route && location.hash === '#/tree' && referenceMode) void reference.open();
  }, [route]);
  function changeLanguage(value: SttvLanguage) {
    setLanguage(value);
    if (route) history.replaceState(null, '', technologyLink(route.id, value, route.enabled));
  }

  useEffect(() => { document.documentElement.lang = language; }, [language]);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  function navigate(page: View) {
    if (route) { history.pushState(null, '', page === 'tree' ? '#/tree' : location.pathname + location.search); setRoute(null); }
    setView(page);
    if (page === 'tree' && referenceMode) void reference.open();
    if (page === 'game' && tab === 'dlc') void reference.loadDlcs();
  }
  function selectGameTab(next: GameTab) {
    setTab(next);
    if (next === 'dlc') void reference.loadDlcs();
  }
  return <SttvLocalizationProvider language={language} data={reference.tree}>
    <SttvMainWindow status={route ? { id: 'sttv_technology_page' } : view === 'game' && tab === 'dlc' && reference.catalogError ? reference.catalogError
      : !referenceMode && view === 'tree' ? { id: 'sttv_empire_mode' } : reference.status ?? { id: 'sttv_ref_idle' }}
      menu={<SttvMenuPanel expanded={expanded}
        actions={pages.map(page => <SttvButton key={page} label={{ id: `sttv_nav_${page}` }} current={!route && view === page}
          onClick={() => navigate(page)} border="never" />)}
        settings={<><SttvLanguageSelector value={language} onChange={changeLanguage} />
          {showTree && <SttvZoomSelector value={zoom} onChange={setZoom} />}</>}
        buttons={<><SttvMenuToggle expanded={expanded} onToggle={() => setExpanded(!expanded)} />
          {expanded && <SttvThemeToggle theme={theme} onToggle={() => setTheme(theme === 'night' ? 'day' : 'night')} />}</>} />}>
      <div className="sttv-view-slot" data-active={showTree} aria-hidden={!showTree} inert={!showTree}>
        <TreeTooltipContext.Provider value={{ enabled: reference.tree?.enabled, active: showTree,
          cache: reference.tooltipCache }}>
          {referenceMode ? reference.tree && <ReferenceField key={reference.tree.id + language} tree={reference.tree}
            language={language} scale={zoom / 100} /> : <p><SttvText text={{ id: 'sttv_empire_placeholder' }} /></p>}
        </TreeTooltipContext.Provider>
      </div>
      {route && <TreeTooltipContext.Provider value={{ cache: reference.tooltipCache, active: true }}>
        <SttvTechnologyPage key={route.id} id={route.id} enabled={route.enabled} />
      </TreeTooltipContext.Provider>}
      {!route && view === 'system' && <SttvTabs<'database' | 'tree'> label="sttv_nav_system" selected={systemTab} onSelect={setSystemTab}
        tabs={[{ id: 'database', label: 'sttv_tab_database', content:
          <div className="sttv-reset-actions">{(['trees', 'progress', 'tooltips', 'all'] as const).map(scope => <SttvButton key={scope}
            label={{ id: scope === 'trees' ? 'sttv_ref_clear' : 'sttv_reset_' + scope }} disabled={reference.busy}
            onClick={() => reference.clear(scope)} />)}</div> },
          { id: 'tree', label: 'sttv_tab_tree_settings', content: <div style={switchStyle}>
            {(['mixed_trees', 'hide_event_technologies'] as const).map(key => <div className="sttv-empire-mode" key={key}>
              <SttvText text={{ id: 'sttv_' + key }} />
              <SttvSwitch label={{ id: 'sttv_' + key }} checked={reference.modes[key]} disabled={reference.busy}
                onChange={() => reference.toggleMode(key)} />
            </div>)}
          </div> }]} />}
      {!route && view === 'game' && <div className="sttv-view-slot" style={switchStyle}>
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
