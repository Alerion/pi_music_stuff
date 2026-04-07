# pi-music-stuff

Pi coding agent extensions, skills, and themes for music production.

## Extensions

### midi-monitor

Real-time MIDI monitor for BeatStep Pro. Tracks incoming MIDI input, extracts step-sequencer patterns, and displays them in a TUI widget. Provides tools for the LLM to read and discuss patterns.

## Setup

Install as a local pi package in your music project's `.pi/settings.json`:

```json
{
  "packages": [
    "/path/to/pi_music_stuff"
  ]
}
```

Or try it for a single session:

```bash
pi -e /path/to/pi_music_stuff
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
