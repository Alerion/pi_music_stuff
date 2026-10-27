import assert from "node:assert/strict";
import test from "node:test";
import { noteName, parseNoteToMidi } from "../extensions/midi-monitor/note-names.ts";
import { renderDrumLines, renderPatternLine, renderPatternText } from "../extensions/midi-monitor/renderer.ts";

const referenceNotes = [
	[0, "C-2"],
	[12, "C-1"],
	[24, "C0"],
	[36, "C1"],
	[37, "C#1"],
	[38, "D1"],
	[48, "C2"],
	[60, "C3"],
	[127, "G8"],
];

test("note names match BeatStep Pro octave numbering", () => {
	for (const [midi, name] of referenceNotes) {
		assert.equal(noteName(midi), name);
		assert.equal(parseNoteToMidi(name), midi);
	}
});

test("all 128 MIDI notes round-trip without transposition", () => {
	for (let midi = 0; midi <= 127; midi++) {
		assert.equal(parseNoteToMidi(noteName(midi)), midi);
	}
});

test("parser accepts flats, lowercase and whitespace", () => {
	assert.equal(parseNoteToMidi("Db2"), 49);
	assert.equal(parseNoteToMidi(" f#2 "), 54);
	assert.equal(parseNoteToMidi("bb1"), 46);
});

test("parser rejects invalid names and out-of-range notes", () => {
	for (const name of ["", "C", "H2", "C2.5", "C-3", "G#8", "C9"]) {
		assert.equal(parseNoteToMidi(name), -1, name);
	}
});

function makePattern(midiNotes, channel) {
	return {
		channel,
		pattern_length: 16,
		loop_count: 1,
		has_notes: true,
		steps: Array.from({ length: 16 }, (_, i) => ({
			step: i + 1,
			notes: i === 2 ? midiNotes.map((note) => ({
				note,
				note_name: noteName(note),
				velocity: 100,
				gate_pct: 17,
			})) : [],
		})),
	};
}

test("bass widget and tool text show MIDI 48 as C2", () => {
	const pattern = makePattern([48], 1);
	const config = { channel: 1, name: "Bass", type: "bass" };
	assert.match(renderPatternLine(pattern, config, 120), /C2/);
	assert.match(renderPatternText(pattern, config), /3 \| C2\s+\| 100 \|\s+17%/);
	assert.equal(pattern.steps[2].notes[0].note, 48);
});

test("drum labels keep their MIDI assignments with the new note names", () => {
	const pattern = makePattern([36, 38], 10);
	const config = { channel: 10, name: "Drums", type: "drums" };
	const lines = renderDrumLines(pattern, config, 120).join("\n");
	assert.match(lines, /Kick \(36\)/);
	assert.match(lines, /Closed HH \(38\)/);
	const text = renderPatternText(pattern, config);
	assert.match(text, /C1/);
	assert.match(text, /D1/);
});
