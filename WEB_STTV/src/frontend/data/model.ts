export type SttvArea = 'physics' | 'society' | 'engineering';
export interface SttvNodeRef { database: string; document_id: string; pointer: string }
export interface SttvRepresentation {
  categories: string[]; iconAssetId: string | null; id: string; variantNumber?: number;
  area: SttvArea; nameId: string; descriptionId: string; sourceRef: SttvNodeRef;
}
export interface SttvCardTechnology {
  id: string; tier: number; levels: number | null; cost: number | null; weight: number | null;
  rare: boolean; dangerous: boolean; eventOnly: boolean; startTech: boolean; sourceRef: SttvNodeRef; representations: SttvRepresentation[];
}
export interface SttvCardCatalog {
  technologies: Record<string, SttvCardTechnology>;
  treeCombination: { parameters: { variants: Record<string, string> } };
  presentation: { research_icons: Record<string, string | null> };
}
