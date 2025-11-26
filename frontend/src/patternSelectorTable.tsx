import {Button} from "@/components/ui/button";
import {Card} from "@/components/ui/card";
import {Input} from "@/components/ui/input";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import type {ExerciseBoardRow, ExerciseBoardRowSetter} from "@/exerciseBoard";
import {cn} from "@/lib/utils";
import {getStripeColoring} from "@/table";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  useReactTable
} from "@tanstack/react-table";

import {PlusIcon} from "lucide-react";
import * as React from "react";
import {type ComponentProps, useState} from "react";

export type PatternTableRow = {
  note: string,
  octave: number,
  // A combination of mood (major|minor) and type (melodic|harmonic|none/natural)
  typeMood: "major" | "minor" | "natural minor" | "harmonic minor" | "melodic minor"
}
export const typeMoods: PatternTableRow["typeMood"][] = ["major", "minor", "natural minor", "harmonic minor", "melodic minor"]
export const patterns: PatternTableRow[] = []
// Range from C2 (C1 midi) to C6 (C5 midi) according to http://en.wikipedia.org/wiki/Vocal_range
const notes = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "FGb", "G", "G#/Ab", "A", "A#/Bb", "B",]

for (const octave of [2, 3, 4, 5]) {
  for (const note of notes) {
    for (const typeMood of typeMoods) {
      patterns.push({
        note,
        octave,
        typeMood,
      })
    }
  }
}
export type BooleanSetter = React.Dispatch<React.SetStateAction<boolean>>
export type StringSetter = React.Dispatch<React.SetStateAction<string>>

type Option = {
  value: string | number,
  selected: boolean
}

export const PatternSelectorTable = ({
                                       setExerciseBoardData,
                                       setReloadRequired,
                                       globalFilter, setGlobalFilter,
                                       ...props
                                     }: ComponentProps<typeof Card> & {
  setExerciseBoardData: ExerciseBoardRowSetter,
  setReloadRequired: BooleanSetter,
  globalFilter: string,
  setGlobalFilter: StringSetter,
}) => {

  const addRowToBoard = (row: PatternTableRow, setExerciseBoardData: ExerciseBoardRowSetter) => {
    // Plural in the case of e.g. "C#/Db"
    const notes = row.note.split("/").map((note) => `${note}${row.octave}`)
    // MIDI notes are numbered different from the American system. Middle C = C4 (american) = C3 (MIDI)
    const midiNotes = row.note.split("/").map((note) => `${note}${Number(row.octave) -1}`)
    const name = `${notes.join("/")} ${row.typeMood}`
    const key = `${midiNotes[0]}_${row.typeMood.split(" ").join("_")}`
    setExerciseBoardData(
      (exerciseBoardRows: ExerciseBoardRow[]) => [...exerciseBoardRows, {name, key}]
    )
  }

  const columnHelper = createColumnHelper<PatternTableRow>();
  const columns = [
    columnHelper.display({
      id: "actions",
      // header: () => <span>Add to Board</span>,
      cell: ({row, table}) => {
        const {setExerciseBoardData, setReloadRequired} = table.options.meta ?? {}
        if (!setExerciseBoardData || !setReloadRequired) throw Error
        return (<span className="flex justify-center">
            <Button type="button" variant="outline" size="icon-sm"
                    onClick={() => {
                      addRowToBoard(row.original, setExerciseBoardData)
                      setReloadRequired(true)
                    }}>
              <PlusIcon/>
            </Button>
          </span>
        )
      }
    }),
    columnHelper.accessor('note', {
      header: ({column}) => {
        return (<>
          <span>Note</span><br/>
        </>)
      },
      cell: ({getValue}) => <span>{getValue()}</span>,
      // TODO: Make custom filter to which an array of values is passed and returns True if the cell value is in the array
      filterFn: "auto", // contains,
    }),
    columnHelper.accessor('octave', {
      header: ({column}) => <span className="">Octave</span>,
      cell: ({getValue}) => <span>{getValue()}</span>,
      filterFn: "auto", // contains,
    }),
    columnHelper.accessor('typeMood', {
      header: ({column}) => <span>Type/Mood</span>,
      cell: ({getValue}) => <span>{getValue()}</span>,
      filterFn: "auto", // contains,
    }),

  ]
  const table = useReactTable<PatternTableRow>({
    data: patterns,
    columns,
    enableColumnResizing: false,
    enableGlobalFilter: true,
    defaultColumn: {
      size: 100,
    },
    state: {
      globalFilter,
    },
    globalFilterFn: 'auto',
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    meta: {setExerciseBoardData, setReloadRequired},
  });
  return (
    <Card {...props}>
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map(headerGroup => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  {/*{header.column.getCanFilter() ? (*/}
                  {/*  <div>*/}
                  {/*    <Filter column={header.column}/>*/}
                  {/*  </div>*/}
                  {/*) : null}*/}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row, rowIdx) => (
            <TableRow key={row.id} className={cn("border-0", getStripeColoring(rowIdx))}>
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  )
}