# nerd-dictation on Fedora 43 + GNOME Wayland

Setup notes from April 2026. This document captures what we installed, where
it lives, and — importantly — *why* each choice was made, so future-you can
revisit the setup without re-doing the research.

## TL;DR

- **Tool:** [nerd-dictation](https://github.com/ideasman42/nerd-dictation) — offline speech-to-text that types into the focused window.
- **Speech engine:** VOSK, small English model (~130 MB unpacked), fully local.
- **Input injection:** `ydotool` (via user-mode systemd service).
- **Python:** dedicated 3.12 venv (Fedora 43's system Python 3.14 lacks vosk wheels).
- **Install root:** `~/opt/nerd-dictation` (git clone + venv).
- **Command on PATH:** `nerd-dictation` (wrapper at `~/.local/bin/nerd-dictation`).

Launch example:
```sh
nerd-dictation begin --simulate-input-tool=YDOTOOL --timeout=3
```

---

## Environment at time of install

- Fedora 43, GNOME 49, Wayland session (`XDG_SESSION_TYPE=wayland`)
- PipeWire for audio (with `parec` available as the Pulse-compatible capture tool)
- System Python: 3.14.3
- User: `geoff`, shell: bash

## What nerd-dictation does (one-paragraph recap)

You run `nerd-dictation begin`; it captures audio from your microphone,
streams it through a local VOSK speech model, and types the transcribed text
into whatever window currently has keyboard focus. You run `nerd-dictation end`
(or let `--timeout` fire) to stop. No internet, no cloud.

The "type into the focused window" step is the hard part on modern Linux
desktops, and most of the decisions below are about that.

---

## Decision log

### 1. Keep GNOME Wayland, don't switch desktop

**Alternatives considered:**
- Switch to a different Wayland compositor like Sway/Hyprland (these expose
  the virtual-keyboard protocol that `wtype` needs).
- Switch to Cinnamon on X11 (X11 makes input injection trivial via `xdotool`).
- Drop back to GNOME-on-X11 — **not viable**, Fedora has removed the GNOME
  X11 session.

**Chose GNOME Wayland because:** user is otherwise happy with GNOME, and the
ydotool plumbing is a one-time setup cost. Switching desktops is a much bigger
UX change for a single feature.

### 2. Input simulation tool: ydotool (not wtype, not dotool, not xdotool)

The goal is to simulate keystrokes so that dictated text is typed into the
focused window. The options on Wayland:

| Tool     | Works on GNOME Wayland? | Packaged in Fedora? | Notes |
| -------- | ----------------------- | ------------------- | ----- |
| xdotool  | No (X11 only)           | yes                 | Dead end — we're on Wayland. |
| wtype    | **No** — needs virtual-keyboard protocol that GNOME/Mutter doesn't implement | yes | Only works on wlroots-based compositors (Sway, Hyprland). |
| ydotool  | Yes (uinput)            | **yes** (v1.0.4)    | Older, more users, explicit nerd-dictation support doc. |
| dotool   | Yes (uinput)            | **no** — build from sourcehut | Better keyboard-layout handling; smaller community. |
| kdotool  | Yes (but KDE-specific)  | yes                 | Not relevant — we're on GNOME. |

**Chose ydotool because:**
- One `dnf install` away — no manual compile.
- nerd-dictation has a dedicated `readme-ydotool.rst` setup doc.
- The layout limitation (doesn't auto-detect keyboard layouts) doesn't matter
  for US English dictation on a US QWERTY layout.

**Revisit dotool if:** you start typing in non-US layouts or multiple languages,
or if ydotool bitrots (last release was Jan 2023).

**About uinput:** Both ydotool and dotool use `/dev/uinput`, a kernel
facility that lets a privileged userspace process create a virtual input
device. The kernel treats events from this device as real keyboard input, so
the compositor accepts them no matter how strict its security model is. This
is why ydotool needs special permissions that `wtype` doesn't.

### 3. ydotool daemon: user-mode service, not Fedora's system service

Fedora's `ydotool` package ships a system service
(`/usr/lib/systemd/system/ydotool.service`) that runs the daemon as root with
no socket-permission configuration. In that default state the daemon socket
is `root:root` mode 0600 — unreachable from a regular user, so the `ydotool`
client would need `sudo`.

**Chose user-mode service** (`~/.config/systemd/user/ydotoold.service`)
**because:**
- Runs as your user, not root — smaller blast radius.
- Socket lives in your user's runtime dir with default permissions you own.
- Lifecycle is tied to your login session — stops cleanly on logout.

**Cost:** you have to give your *user* permission to open `/dev/uinput` via
the `input` group + a udev rule. This is a one-time setup.

### 4. Python 3.12 venv, not system Python 3.14

Fedora 43 ships Python 3.14 as the system Python. As of install time, `vosk`
on PyPI had no wheels for Python 3.14 — attempting `pip install vosk` on 3.14
would either fail or try to build from source (which needs Kaldi build deps,
a whole-afternoon detour).

**Chose:** `sudo dnf install python3.12`, then a venv using that interpreter.
Self-contained, doesn't touch system Python, doesn't interfere with anything
else.

**Revisit when:** vosk publishes Python 3.14+ wheels — at that point you can
drop the `python3.12` dependency and use system Python.

### 5. VOSK model: small English (vosk-model-small-en-us-0.15)

| Model   | Size | Accuracy | Latency |
| ------- | ---- | -------- | ------- |
| small   | ~130 MB unpacked | Good for dictation | Low |
| large   | ~1.8 GB          | Better             | Higher RAM + slower |

**Chose small** as default — good enough for general English dictation,
loads fast, low memory footprint. Upgrade to the large model later if
accuracy becomes the bottleneck.

Model list: https://alphacephei.com/vosk/models

### 6. Keyboard shortcut: Pause key

**Alternatives considered:**
- `Ctrl+Alt+D` — free in GNOME, mnemonic for "Dictate". Good choice, but uses a
  three-finger chord every time you dictate.
- `Super+D` — ergonomic, but **taken** (Show Desktop in GNOME).
- `Ctrl+D` — **very bad** — hijacks a critical key used by terminals (EOF),
  many editors (delete line / multi-cursor), and browser bookmark dialogs.
- `F12` — free at GNOME level, but browsers and editors grab it for devtools.
  A global binding would steal it from those apps.

**Chose the `Pause` key** because it's a dedicated dead key on modern
keyboards — almost never used by any application — so there's no risk of
stealing it from an app, and it's a single keystroke rather than a chord.

Downside: not all keyboards have a Pause key (notably most laptops lack one
or bury it behind Fn). If that changes, fall back to `Ctrl+Alt+D`.

### 7. Install location: `~/opt/nerd-dictation`

**Alternatives:** `/opt/nerd-dictation` (system-wide, needs sudo to update),
`~/.local/share/nerd-dictation` (XDG-standard), pip/pipx install.

**Chose `~/opt/`** because:
- Single-user, no sudo needed to `git pull` updates.
- Repo contains a venv (`./.venv`) — treating it as a self-contained app
  dir is cleaner than scattering across XDG dirs.
- Matches the author's installation pattern (not a Python package, just a
  runnable script in a repo).

---

## Setup steps (what we actually ran)

### Packages
```sh
sudo dnf install -y ydotool python3.12
```

### uinput permissions (so ydotoold can run as user)

Write the udev rule:
```sh
sudo tee /etc/udev/rules.d/80-uinput.rules <<'EOF'
KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"
EOF
```

Add yourself to the `input` group:
```sh
sudo usermod -aG input "$USER"
```

Apply without rebooting:
```sh
sudo udevadm control --reload-rules
sudo udevadm trigger /dev/uinput
```

**Group membership requires a fresh login session to take effect in the
graphical environment** — log out and back in. (Running apps and shells
can't pick up the new group without restarting.)

Verify:
```sh
ls -la /dev/uinput               # should be: crw-rw---- root input ...
grep '^input:' /etc/group         # should list your username
id -nG | tr ' ' '\n' | grep -x input  # (after re-login) should print "input"
```

### ydotoold user service

File: `~/.config/systemd/user/ydotoold.service`
```ini
[Unit]
Description=ydotoold daemon (virtual input device for ydotool)

[Service]
ExecStart=/usr/bin/ydotoold
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

Enable (starts on every login):
```sh
systemctl --user enable ydotoold.service
```

After re-login, verify:
```sh
systemctl --user is-active ydotoold   # should print: active
```

### nerd-dictation install

```sh
mkdir -p ~/opt
cd ~/opt
git clone https://github.com/ideasman42/nerd-dictation.git
cd nerd-dictation
python3.12 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install vosk
```

### VOSK model

```sh
mkdir -p ~/.config/nerd-dictation
cd /tmp
wget https://alphacephei.com/kaldi/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 ~/.config/nerd-dictation/model
rm vosk-model-small-en-us-0.15.zip
```

nerd-dictation looks for the model at `~/.config/nerd-dictation/model` by
default — no flag needed once it's there.

### Launcher wrapper

File: `~/.local/bin/nerd-dictation`
```sh
#!/bin/sh
# Wrapper around the cloned nerd-dictation script that uses its dedicated
# Python 3.12 venv (where vosk is installed).
exec /home/geoff/opt/nerd-dictation/.venv/bin/python \
    /home/geoff/opt/nerd-dictation/nerd-dictation "$@"
```

```sh
chmod +x ~/.local/bin/nerd-dictation
```

`~/.local/bin` is already in `$PATH` on Fedora.

---

## File inventory (where everything lives)

| Path | What it is |
| ---- | ---------- |
| `/usr/bin/ydotool`, `/usr/bin/ydotoold` | Fedora-packaged binaries |
| `/etc/udev/rules.d/80-uinput.rules` | Grants `input` group access to `/dev/uinput` |
| `~/.config/systemd/user/ydotoold.service` | User-mode service unit |
| `~/.config/systemd/user/default.target.wants/ydotoold.service` | Symlink created by `systemctl --user enable` |
| `~/opt/nerd-dictation/` | Cloned git repo |
| `~/opt/nerd-dictation/.venv/` | Python 3.12 venv with vosk |
| `~/opt/nerd-dictation/nerd-dictation` | The actual script (called by the wrapper) |
| `~/.config/nerd-dictation/model/` | VOSK speech model |
| `~/.config/nerd-dictation/nerd-dictation.py` | **(optional, not yet created)** User config for word substitutions, etc. |
| `~/.local/bin/nerd-dictation` | Wrapper on PATH |

---

## Usage

### One-shot dictation with auto-stop on silence
```sh
nerd-dictation begin --simulate-input-tool=YDOTOOL --timeout=3
```
Focus your target window, speak. Three seconds of silence ends the session
and commits the typed output.

### Manual begin/end (for longer dictation)
Terminal A:
```sh
nerd-dictation begin --simulate-input-tool=YDOTOOL
```
Focus the target window, dictate as long as you want.

Terminal B (when done):
```sh
nerd-dictation end
```

### Test without typing (prints to stdout)
Useful when debugging the speech engine, separate from the input-injection path:
```sh
nerd-dictation begin --output=STDOUT --timeout=3
```

### Keyboard shortcut (`Pause` key)

Set up as a GNOME custom shortcut, binding the `Pause` key to:
```
nerd-dictation begin --simulate-input-tool=YDOTOOL --timeout=3 --full-sentence
```

Press **Pause**, click into any text field, speak, stay silent for 3
seconds — text appears.

**To change the key** (CLI):
```sh
gsettings set \
  org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd-dictation/ \
  binding '<Ctrl><Alt>d'    # or any other accelerator string
```

**To change via GUI:** Settings → Keyboard → View and Customize Shortcuts →
Custom Shortcuts → "Dictate".

**To remove entirely:**
```sh
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "[]"
dconf reset -f /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd-dictation/
```

### Other useful `begin` flags
- `--full-sentence` — capitalize first word, auto-add comma/period between
  utterances.
- `--numbers-as-digits` — transcribe "twenty three" as "23".
- `--punctuate-from-previous-timeout=2` — re-add punctuation after silence.
- `--continuous` — better for long sessions (doesn't re-process entire
  transcript each update).

---

## Known gotchas

1. **First run is slow.** VOSK loads the model (tens of MB) into memory on
   each `begin`. Expect a 1–3 second warmup. For responsive push-to-talk,
   consider running `begin --suspend-on-start` and toggling with
   `suspend`/`resume` instead.

2. **`--timeout=N` is silence-timeout, not total-timeout.** It stops after N
   seconds of *no speech*. As long as you keep talking, it keeps going.

3. **Keyboard layout mismatches.** ydotool doesn't auto-detect your keyboard
   layout. On a non-US layout, some characters (especially punctuation) will
   come out wrong. Switch to `dotool` if this bites you.

4. **Group membership only applies to new logins.** After the initial
   `usermod -aG input`, running apps, open terminals, and your desktop
   session itself all need a fresh login to see the new group. This caught
   us once — if the ydotoold service fails with permission errors on
   `/dev/uinput`, the session predates the group change.

5. **Mic selection.** PipeWire may route to the wrong input source. Check
   GNOME Settings → Sound → Input. Or enumerate devices with
   `pactl list sources` and pass `--pulse-device-name=<identifier>` to
   `begin`.

6. **No mic activity indicator.** nerd-dictation doesn't chirp or flash
   anything when it starts listening. Easy to think it's hung when it's
   just waiting for speech.

---

## Future enhancements

### Toggle on/off instead of silence-timeout

Current setup: press Pause, dictate, wait for silence. You can't "cancel"
mid-stream without waiting, and you can't pause-to-think without ending the
session.

**Option A — process-check toggle (simple).** Replace the shortcut command
with a wrapper script that checks whether nerd-dictation is running and
either starts `begin` or sends `end`:

```sh
#!/bin/sh
# ~/.local/bin/nerd-dictation-toggle
if pgrep -u "$USER" -f 'nerd-dictation/nerd-dictation begin' > /dev/null; then
    exec /home/geoff/.local/bin/nerd-dictation end
else
    exec /home/geoff/.local/bin/nerd-dictation begin \
        --simulate-input-tool=YDOTOOL --full-sentence
fi
```

Then repoint the shortcut:
```sh
gsettings set \
  org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd-dictation/ \
  command '/home/geoff/.local/bin/nerd-dictation-toggle'
```

Pro: simple, no RAM cost when idle.
Con: each dictation session pays the 1–3 s model load time.

**Option B — persistent daemon with suspend/resume (fast).** Run
`nerd-dictation begin --suspend-on-start` as a systemd user service (same
pattern as `ydotoold.service`). Shortcut toggles between `suspend` and
`resume`. Model stays hot in RAM (~200 MB idle), so toggling is
near-instant.

Pro: instant on/off.
Con: permanent ~200 MB RAM overhead; slightly more moving parts (a second
service + a toggle script that calls suspend/resume instead of begin/end).

### Larger VOSK model (better accuracy)

The small model (~130 MB) is fast and good enough for everyday dictation.
If you hit accuracy limits (missed words, wrong homophones), swap to the
large model. Models are listed at <https://alphacephei.com/vosk/models>.

As of writing, the recommended large English model is
`vosk-model-en-us-0.22` (~1.8 GB unpacked). Swap steps:

```sh
# Back up current (small) model
mv ~/.config/nerd-dictation/model ~/.config/nerd-dictation/model.small

# Download, unpack, install
cd /tmp
wget https://alphacephei.com/kaldi/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
mv vosk-model-en-us-0.22 ~/.config/nerd-dictation/model
rm vosk-model-en-us-0.22.zip

# Test
nerd-dictation begin --output=STDOUT --timeout=3
```

To revert: `rm -rf ~/.config/nerd-dictation/model &&
mv ~/.config/nerd-dictation/model.small ~/.config/nerd-dictation/model`.

Trade-offs: longer first-load (~3–5 s), higher RAM (~1 GB during dictation),
better accuracy.

### Other ideas

- **User config for word replacements.** Create
  `~/.config/nerd-dictation/nerd-dictation.py` to map dictated phrases to
  output (e.g., "new line" → `\n`, "comma" → `,`, or code-specific
  substitutions). See upstream `readme.rst` → "Configuration" section.
- **Drop Python 3.12 dependency** once vosk ships 3.14 wheels — rebuild
  the venv with system Python.

---

## Uninstall

```sh
# Remove the keyboard shortcut
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "[]"
dconf reset -f /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd-dictation/

# Stop and disable the daemon
systemctl --user disable --now ydotoold.service
rm ~/.config/systemd/user/ydotoold.service

# Remove the install
rm -rf ~/opt/nerd-dictation
rm -rf ~/.config/nerd-dictation
rm ~/.local/bin/nerd-dictation

# Remove system packages (optional — safe to leave installed)
sudo dnf remove ydotool python3.12

# Revert uinput permissions (optional)
sudo rm /etc/udev/rules.d/80-uinput.rules
sudo gpasswd -d "$USER" input
sudo udevadm control --reload-rules
sudo udevadm trigger /dev/uinput
```

---

## References

- nerd-dictation: https://github.com/ideasman42/nerd-dictation
- nerd-dictation ydotool guide: https://github.com/ideasman42/nerd-dictation/blob/master/readme-ydotool.rst
- ydotool: https://github.com/ReimuNotMoe/ydotool
- dotool: https://git.sr.ht/~geb/dotool
- VOSK models: https://alphacephei.com/vosk/models
