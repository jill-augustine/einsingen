// -@ts-nocheck
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { getExercise, type MidiJSEvent, playMidi } from "@/midi";
// import {Input} from "@/components/ui/input.tsx";
import { PatternSelectorTable, } from "@/patternSelectorTable";
import { ExerciseBoard, type ExerciseBoardRow } from "@/exerciseBoard"
import type { FilterFn } from "@tanstack/react-table";
import { useState } from "react";
import * as React from "react";


const contains: FilterFn<unknown> = (row, columnId: string, filterValue: unknown[]) => {
  if (filterValue.length == 0) return true
  return filterValue.includes(row.getValue(columnId))
}

const Component = () => {
  const [globalFilter, setGlobalFilter] = useState("")
  const [exerciseBoardData, setExerciseBoardData] = useState<ExerciseBoardRow[]>([])
  const [midiBase64, setMidiBase64] = useState<string>("")
  // Also valid for inital load
  const [reloadRequired, setReloadRequired] = useState<boolean>(false)
  const midiJSEventPlaceholder = { status: "", time: 0 }
  const [playerEventStatus, setPlayerEventStatus] = useState<MidiJSEvent>({ status: "", time: 0 })
  const emptyBoard = exerciseBoardData.length == 0
  return (
    <div className="flex flex-col md:gap-y-4 items-center w-full">
      <Card className="flex flex-col md:gap-y-4 items-center w-full border-0 shadow-none p-4">
        <CardContent className="flex flex-col gap-y-3 items-center min-w-sm md:min-w-md">
          <CardTitle>
            Exercise Board
          </CardTitle>
          {/*Pad ExerciseBoard if list is empty*/}
          <ExerciseBoard exerciseBoardData={exerciseBoardData} setExerciseBoardData={setExerciseBoardData}
            setReloadRequired={setReloadRequired} className={
              emptyBoard ?
                "flex w-full justify-center px-1 pt-1 pb-11" :
                "flex w-full justify-center px-1 py-1"} />
          <div className="flex gap-x-3 gap-y-2 self-center-safe">
            {emptyBoard ?
              <Button disabled variant="outline">Clear Board</Button> :
              <Button className="text-red-500" variant="outline" onClick={() => setExerciseBoardData([])}>Clear
                Board</Button>}
            {emptyBoard ?
              <Button disabled variant="outline">Load Exercise</Button> :
              <Button className="" variant="outline"
                onClick={async () => {
                  await getExercise(exerciseBoardData, setMidiBase64)
                  setReloadRequired(false)
                }}>Load Exercise</Button>}
            {/*Disable the play button if there is no MIDI track or reload is required
            (because new items were added to the exercise board) */}
            {midiBase64 === "" || reloadRequired ?
              <Button disabled variant="outline">Play Exercise</Button> : (
                playerEventStatus.status == "playing" ?
                  <Button className="text-blue-500" variant="outline"
                    onClick={() => {
                      window.MIDIjs.stop()
                      setPlayerEventStatus(midiJSEventPlaceholder)
                    }}>Stop
                    Exercise</Button> :
                  <Button className="text-blue-500" variant="outline"
                    onClick={() => playMidi(midiBase64, setPlayerEventStatus)}>Play
                    Exercise</Button>
              )}
          </div>
          <span id="spacer" className="h-3" />
          <span className="self-start font-semibold">Available Patterns</span>
          <Input type="text"
            placeholder="Search all patterns..."
            className=""
            value={globalFilter ?? ""}
            onChange={(e) => setGlobalFilter(e.target.value)} />

          <PatternSelectorTable setExerciseBoardData={setExerciseBoardData} setReloadRequired={setReloadRequired}
            globalFilter={globalFilter} setGlobalFilter={setGlobalFilter}
            className="flex w-full justify-center px-1 py-1" />
        </CardContent>
      </Card>
    </div>
  )

}

export const route = {
  path: "/home",
  Component,
}
