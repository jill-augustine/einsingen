// ----------------------------------------------------------------------------
import {getBackendURL} from "@/url";
import axios, {type AxiosResponse} from "axios";

axios.defaults.withCredentials = true; // include cookies on requests

import type {ExerciseBoardRow} from "@/exerciseBoard";
import * as React from "react";

export type MidiJSEvent = {
  time: number,
  status: string, // 'playing' | 'finished'
}
export type PlayerEventStatusSetter = React.Dispatch<React.SetStateAction<MidiJSEvent>>


export const playMidi = (
  midiBase64: string, setPlayerEventStatus: PlayerEventStatusSetter
): void => {
  const playerCallback = (event: MidiJSEvent) => (setPlayerEventStatus(event))
  // Convert from URL-safe to regular base64 encoded.
  const generalizedBase64 = midiBase64.replace(/-/g, '+').replace(/_/g, '/');
  const url = `data:audio/midi;charset=utf-8;base64,${generalizedBase64}`;
  window.MIDIjs.player_callback = playerCallback
  window.MIDIjs.play(url)
}
export type SetMidiBase64 = React.Dispatch<React.SetStateAction<string>>

// Matches equivalent class in backend
type MelodyResponse = {
  rhythm: string,
  pitch: string,
  melody: string  // base64-encoded bytes
}
// Return byte string
export const getExercise = async (
  exercise: ExerciseBoardRow[], setMidiBase64: SetMidiBase64
): Promise<void> => {
  const url = getBackendURL()
  // Body must have the key `exercises`
  const body = {exercises: exercise.map(e => ({name: e.key, arp: false}))}
  const jsonResponse: AxiosResponse<string> = await axios.post(
    `${url}/api/exercises`,
    body,
    {headers: {"Content-Type": "application/json"}, withCredentials: true}
  );
  const response: MelodyResponse = JSON.parse(jsonResponse.data)
  setMidiBase64(response.melody)
}