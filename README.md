# pi-music-stuff

Pi coding agent extensions, skills, and themes for music production.

## Extensions

### midi-monitor

Real-time MIDI monitor for BeatStep Pro. Tracks incoming MIDI input, extracts step-sequencer patterns, and displays them in a TUI widget. Provides tools for the LLM to read and discuss patterns.

## Setup

### 1. Install dependencies

You need Pi, Node.js (a version supported by your Pi installation), and npm.
From the root of this checkout, install the runtime dependencies:

```bash
cd /path/to/pi_music_stuff
npm ci --omit=peer
```

`--omit=peer` skips installing the Pi packages supplied by the host. The MIDI
library, `@julusian/midi`, is a native Node.js addon, so allow npm's install
scripts to run (do not use `--ignore-scripts`).

If a prebuilt MIDI binary is unavailable for your platform or Node.js version,
building it requires Python 3 and a C/C++ toolchain. On Linux, install the ALSA
development headers as well:

```bash
# Fedora
sudo dnf install gcc-c++ make python3 alsa-lib-devel

# Debian / Ubuntu
sudo apt install build-essential python3 libasound2-dev
```

On macOS, install the Xcode Command Line Tools (`xcode-select --install`) and
ensure Python 3 is available. On Windows, a source build requires Python 3 and
Visual Studio Build Tools with the Desktop development with C++ workload.

### 2. Load the package in Pi

From your music project, register this checkout as a project-local package:

```bash
cd /path/to/music-project
pi install --local /path/to/pi_music_stuff
```

Alternatively, add it to your music project's `.pi/settings.json` (preserving
any existing settings):

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

Local package paths are loaded in place; Pi does **not** install their npm
dependencies. Complete step 1 even when using `pi install` or `pi -e`.
Restart Pi after installation, or run `/reload` in an existing session.

### Troubleshooting

**`Cannot find module '@julusian/midi'`** means the MIDI dependency is not
available in this checkout. Run `npm ci --omit=peer` in the `pi_music_stuff`
root, not in your music project or the `extensions/midi-monitor` directory,
and then reload Pi.

If installation fails with `node-gyp` or missing ALSA header errors, install the
build prerequisites above and rerun the command. If the native addon fails to
load after changing Node.js versions, rerun it to reinstall dependencies for
the current Node.js version.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
