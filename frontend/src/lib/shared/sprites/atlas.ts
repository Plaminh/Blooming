export type AtlasCell = {
  col: number;
  row: number;
};

export function atlasCellOffset(cell: AtlasCell, cellWidth: number, cellHeight: number): { x: number; y: number } {
  return {
    x: cell.col * cellWidth,
    y: cell.row * cellHeight,
  };
}

export function atlasSheetTransform(cell: AtlasCell, cellWidth: number, cellHeight: number, scale: number): string {
  const { x, y } = atlasCellOffset(cell, cellWidth, cellHeight);
  return `scale(${scale}) translate(${-x}px, ${-y}px)`;
}
