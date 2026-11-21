import { SttvTechnologyDetails } from '../ui/composite/TechnologyTooltipDetails';
import { SttvText } from '../ui/base/Text';

export function SttvTechnologyPage({ id, enabled }: { id: string; enabled?: string[] }) {
  return <article className="sttv-technology-page">
    <a href="#/tree"><SttvText text={{ id: 'sttv_nav_tree' }} /></a>
    <SttvTechnologyDetails id={id} enabled={enabled} page />
  </article>;
}
