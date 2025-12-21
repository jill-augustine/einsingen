// The type containing information about a musical pattern
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { BooleanSetter } from "@/patternSelectorTable";
import { getStripeColoring } from "@/table";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
  type Table as TanStackTable,
} from "@tanstack/react-table";
import { MoveDownIcon, MoveUpIcon, Trash2Icon } from "lucide-react";
import * as React from "react";
import { type ComponentProps } from "react";
import { cn } from "@/lib/utils"


export type ExerciseBoardRow = {
  name: string,
  key: string,
}

export type ExerciseBoardRowSetter = React.Dispatch<React.SetStateAction<ExerciseBoardRow[]>>

const OptionalTableHeader = ({ table }: ComponentProps<typeof TableHeader> & {
  table: TanStackTable<ExerciseBoardRow>
}) => {
  return <TableHeader>
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
          </TableHead>
        ))}
      </TableRow>
    ))}
  </TableHeader>
}

export const ExerciseBoard = ({
  exerciseBoardData,
  setExerciseBoardData,
  className,
  setReloadRequired,
  ...props
}: ComponentProps<typeof Card> & {
  exerciseBoardData: ExerciseBoardRow[],
  setExerciseBoardData: ExerciseBoardRowSetter,
  setReloadRequired: BooleanSetter,
}) => {

  const removeRowFromBoard = (idx: number, setExerciseBoardData: ExerciseBoardRowSetter) => {
    setExerciseBoardData(
      (exerciseBoardRows: ExerciseBoardRow[]) => exerciseBoardRows.filter((row, i) => i != idx)
    )
    setReloadRequired(true)
  }
  const moveRowUp = (idx: number, setExerciseBoardData: ExerciseBoardRowSetter) => {
    setExerciseBoardData(
      (exerciseBoardRows: ExerciseBoardRow[]) => {
        if (idx <= 0 || idx >= exerciseBoardRows.length) return exerciseBoardRows;
        const [prev, n] = exerciseBoardRows.slice(idx - 1, idx + 1)
        const newRows = [...exerciseBoardRows]
        newRows.splice(idx - 1, 2, n, prev)
        return newRows
      }
    )
  }
  const moveRowDown = (idx: number, setExerciseBoardData: ExerciseBoardRowSetter) => {
    setExerciseBoardData(
      (exerciseBoardRows: ExerciseBoardRow[]) => {
        if (idx <= 0 || idx >= exerciseBoardRows.length - 1) return exerciseBoardRows;
        const [n, next] = exerciseBoardRows.slice(idx, idx + 2)
        const newRows = [...exerciseBoardRows]
        newRows.splice(idx, 2, next, n)
        return newRows
      }
    )
  }


  const columnHelper = createColumnHelper<ExerciseBoardRow>();
  const columns = [
    columnHelper.accessor('name', {
      header: () => {
        return (<>
          <span>Pattern</span>
        </>)
      },
      cell: ({ getValue }) => <span>{getValue()}</span>,
    }),
    columnHelper.display({
      id: 'actions',
      cell: ({ row, table }) => {
        const { setExerciseBoardData } = table.options.meta ?? {}
        if (!setExerciseBoardData) throw Error
        return (<span className="flex justify-center gap-x-2">
          <Button size="icon-sm" onClick={() => moveRowUp(row.index, setExerciseBoardData)}>
            <MoveUpIcon />
          </Button>
          <Button size="icon-sm" onClick={() => moveRowDown(row.index, setExerciseBoardData)}>
            <MoveDownIcon />
          </Button>
          <Button size="icon-sm"
            onClick={() => removeRowFromBoard(row.index, setExerciseBoardData)}>
            <Trash2Icon />
          </Button>
        </span>
        )
      }
    })
  ]

  const table = useReactTable<ExerciseBoardRow>({
    data: exerciseBoardData,
    columns,
    enableColumnFilters: true,
    state: {},
    getCoreRowModel: getCoreRowModel(),
    meta: { setExerciseBoardData, setReloadRequired },
  });

  const includeHeader = false
  return (
    <Card className={className} {...props}>
      <Table>
        {includeHeader ? <OptionalTableHeader table={table} /> : null}
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