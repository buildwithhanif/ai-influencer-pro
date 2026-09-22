# Audio

- **Embedded audio needs `volume: 1.0`** on a Video layer; omitted means silent. Gain is linear
  and static (trap 7): duck by splitting.
- **SFX are Audio layers**: `Edit.sfx(asset, at, length_ms, vol)`. Place the file so its loudest
  point lands on the event (`at = event - peak_offset`). The Audio layer's source range must not
  run past the file: take the length from `assets.json`.
- **Levels**: a swoosh at 0.22 sits about -20 dBFS pre-normalisation, under the voices. If you can
  name the sound on a first watch it is too loud.
- **Proving a sound is in the mix**: `verify.py sfx` exports with every Video layer muted and reads
  the peak at each time. With voices on top, RMS proves nothing.
- **Loudness**: `deliver.sh` to -14 LUFS, true peak -1.5, 48 kHz.
