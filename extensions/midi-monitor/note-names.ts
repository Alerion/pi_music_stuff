/** BeatStep Pro octave naming: MIDI 0 = C-2, MIDI 48 = C2, MIDI 60 = C3. */
const OCTAVE_OFFSET = 2;
const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

export function noteName(midiNote: number): string {
	const octave = Math.floor(midiNote / 12) - OCTAVE_OFFSET;
	return `${NOTE_NAMES[midiNote % 12]}${octave}`;
}

/** Parse BeatStep Pro note names (including sharps/flats). Returns -1 if invalid. */
export function parseNoteToMidi(name: string): number {
	const NOTE_MAP: Record<string, number> = {
		"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "Fb": 4,
		"F": 5, "E#": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8,
		"A": 9, "A#": 10, "Bb": 10, "B": 11, "Cb": 11,
	};
	const m = name.trim().match(/^([A-Ga-g][#b]?)(\-?\d+)$/);
	if (!m) return -1;
	const pc = NOTE_MAP[m[1][0].toUpperCase() + m[1].slice(1)];
	if (pc === undefined) return -1;
	const octave = parseInt(m[2]);
	const midi = (octave + OCTAVE_OFFSET) * 12 + pc;
	return (midi >= 0 && midi <= 127) ? midi : -1;
}
