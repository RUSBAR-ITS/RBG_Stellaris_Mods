import type { SttvPlacement } from './model';
import { sttvTreeError } from './contract';

export function sttvPlaceTrees(roots: string[], nodes: Map<string, { column: number; children: string[] }>,
  compare: (parent: string) => (a: string, b: string) => number) {
  const occupied = new Set<string>(), visited = new Set<string>(), cards: SttvPlacement[] = [];
  type Frame = { id: string; row: number; bottom: number; children: string[]; next: number };
  function enter(id: string, minimum: number): Frame {
    if (visited.has(id)) sttvTreeError('tree_layout_failed', 'Technology visited twice.', { technologyId: id });
    visited.add(id);
    const node = nodes.get(id)!;
    let row = minimum;
    while (occupied.has(`${node.column}:${row}`)) row++;
    occupied.add(`${node.column}:${row}`);
    cards.push({ id, column: node.column, row });
    return { id, row, bottom: row, children: [...node.children].sort(compare(id)), next: 0 };
  }
  let bottom = -1;
  for (const root of roots) {
    const stack = [enter(root, bottom + 1)];
    while (stack.length) {
      const frame = stack.at(-1)!;
      if (frame.next < frame.children.length) {
        const child = frame.children[frame.next];
        const minimum = frame.next++ === 0
          ? frame.row + Number(nodes.get(child)!.column === nodes.get(frame.id)!.column) : frame.bottom + 1;
        stack.push(enter(child, minimum));
      } else {
        stack.pop();
        if (stack.length) stack.at(-1)!.bottom = Math.max(stack.at(-1)!.bottom, frame.bottom);
        else bottom = frame.bottom;
      }
    }
  }
  return { cards, rowCount: bottom + 1 };
}
