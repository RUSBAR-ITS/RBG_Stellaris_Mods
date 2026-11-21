import { useCallback, useMemo, useState } from 'react';
import type { SttvLanguage } from '../localization/model';
import { SttvText } from '../ui/base/Text';
import { SttvCardMeasurement } from '../ui/composite/CardMeasurement';
import { SttvTechnologyField } from '../ui/layout/TechnologyField';
import { fetchReference, referenceLayout } from '../app/reference';

export function ReferenceField({ tree, language, scale }: {
  tree: Awaited<ReturnType<typeof fetchReference>>; language: SttvLanguage; scale: number;
}) {
  const [measurement, setMeasurement] = useState<{ tree: typeof tree; height: number } | null>(null);
  const height = measurement?.tree === tree ? measurement.height : 0;
  const measure = useCallback((height: number) => setMeasurement({ tree, height }), [tree]);
  const result = useMemo(() => {
    if (!height) return null;
    try { return { layout: referenceLayout(tree.nodes, tree.hidden, language, height) }; }
    catch (error) { return { error: String(error) }; }
  }, [height, tree, language]);
  return <>
    {!height && <SttvCardMeasurement data={tree.data} onMeasure={measure} />}
    {result?.layout && <SttvTechnologyField data={tree.data} layout={result.layout} scale={scale} />}
    {result?.error && <p role="alert"><SttvText text={{ id: 'sttv_ref_error', params: { reason: result.error } }} /></p>}
  </>;
}
