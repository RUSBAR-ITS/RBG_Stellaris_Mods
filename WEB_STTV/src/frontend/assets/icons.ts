export const sttvIcons = {
  collapse: 'm14 6-6 6 6 6',
  expand: 'm10 6 6 6-6 6',
  sun: 'M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  moon: 'M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z',
  check: 'm5 12 4 4L19 6',
  down: 'm6 9 6 6 6-6',
} as const;
export type SttvIconName = keyof typeof sttvIcons;
