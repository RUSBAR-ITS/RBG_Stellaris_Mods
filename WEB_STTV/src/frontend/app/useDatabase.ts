import { useEffect, useRef, useState } from 'react';
import { SttvOpeningController, sttvIdle } from '../workers/controller';

export function sttvUseDatabase() {
  const [opening, setOpening] = useState(sttvIdle);
  const controller = useRef<SttvOpeningController | null>(null);
  if (!controller.current) controller.current = new SttvOpeningController(setOpening,
    () => new Worker(new URL('../workers/database.worker.ts', import.meta.url), { type: 'module' }));
  useEffect(() => () => controller.current?.dispose(), []);
  return { opening, controller: controller.current };
}
