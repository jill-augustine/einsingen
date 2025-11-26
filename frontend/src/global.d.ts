import type {ExerciseBoardRowSetter} from "@/exerciseBoard";
import type {BooleanSetter} from "@/patternSelectorTable";
import type {RowData} from "@tanstack/react-table";

declare global {
  interface Window {
    MIDIjs: {
      play: (arg: string) => (void);
      stop: () => (void);
      player_callback: (event) => (event);
    }
  }
}
declare module '@tanstack/react-table' {
  interface TableMeta<TData extends RowData> {
    setExerciseBoardData: ExerciseBoardRowSetter,
    setReloadRequired: BooleanSetter,
  }
}

export {};
