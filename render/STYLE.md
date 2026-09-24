# Render style guide

The rules every SVG component follows, so that characters, places and props written at different times still look like one world. `story render` enforces the file layout and the rig declarations; the look is enforced at the preview checkpoint.

## Files

| What | Where | Exports |
|---|---|---|
| Character rig (series-wide) | `src/series/<series>/characters/<id>.tsx` | `rig: Rig` |
| Recurring location | `src/series/<series>/locations/<id>.tsx` | `location: Location` |
| Shared prop | `src/series/<series>/props/<id>.tsx` | `prop: Prop` |
| Episode-only location / prop | `src/episodes/<episode-id>/{locations,props}/<id>.tsx` | same as above |
| Shared close-up, insert or card | `src/common/{locations,props}/<id>.tsx` | same as above, plus `about` |
| Vendored open-source art | `src/vendor/<library>/` | components, with the library's LICENSE and a README |

The file name is the id from the manifest. The most specific component wins: episode, then series, then shared. Interfaces live in `src/kit/types.ts`. A shared component names no story or character, imports only from `kit/`, times itself from `words` (see `DIRECTING.md`), and declares its one-line description as `export const about = "...";`, which the ChatGPT briefs list as a ready-made shot.

## Rigs

- Drawn **facing right**, origin at the **feet on the ground line**, standing height roughly: Pip 260 px, Ben 380 px, Wren 150 px, humans about 470 px.
- People: build them with `makeHuman(spec)` from `kit/human.tsx` (proportions, IK arms and legs, planted-foot walk, a posture and gesture for every stance × mood). A spec is a mix-and-match wardrobe: hair style (`short`, `bun`, `braids` with a ribbon, `long`, a receding `fringe`), `mustache` (optionally curled), `beard`, `stubble`, `turban` (optionally jewelled), `hat`, `bindi`, `wrinkles`; top colour and `sleeves` (`rolled`, `long`, `none`); a lower garment via `skirt` (`hem` sets the length: dhoti about -95, long coat -120, sari or robe to the ankle) and a `robe.sash` over one shoulder (towel, pallu, sash); `buttons`, `apron`; build via `stout`, `stoop`, and children via `size` (~0.72) plus `headScale` (~1.2). Special stances draw their own tool: `aim` (a bow), `dig` (a shovel on a strike rhythm).
- Check every new character on a model sheet before it goes into an episode (`src/dev/CastSheet.tsx`: `CastSheet`, `PoseSheet`, `PropSheet`).
- Animals that walk: use `walkCycle` from `kit/walk.ts` so feet stay planted and stride follows speed. The renderer mirrors for `facing: left` and scales background characters to 0.6.
- Declare support as **one-line literal arrays**, which `story render` reads:
  ```ts
  stances: ['stand', 'walk', 'sit'],
  moods: ['neutral', 'happy', 'sad'],
  ```
- `anchors.hand` is where a held prop is drawn (the `hold` stance); `anchors.head` is the top of the head.
- Mouths: use `kit/face.tsx` (`Mouth`, `moodFace`) so the eight visemes and the eleven moods read the same on every character. Eyes blink through the `eye` prop (1 open → 0 closed).
- Keep idle life subtle: breathing about 1%, a small head tilt, a little extra movement while `speaking`.

## Locations

- Draw in the 1920×1080 scene space, **with margin beyond the frame** (about 200 px each side): the camera pans and zooms.
- `groundY` is where foreground characters stand (keep it about 850–880 so captions never cover feet); `backgroundGroundY` is for background characters.
- `propSlots` lists where free props stand, in the order props are assigned.
- Descriptions carry no time of day or weather: the renderer adds the sky, the light tint and the atmosphere. Interiors set `interior: true` and draw their own walls; windows may use `palette.skyMid` so they follow the time of day.
- Put slow SVG filters (`watercolor`) only on static background groups, never on characters or animated parts.

## Look

- **One ink outline**: `ink(width)` from `kit/style.tsx` (`#3b2a20`, round joins), about 3–3.5 px on characters, 2.5–3 on props and near scenery, lighter opacity on far scenery.
- **Palette**: muted greens and golden ochres, warm browns, soft creams; saturated colors only for small accents (Pip's scarf, Wren's berry, the lantern glow).
- **Depth**: far layers lighter, bluer and softly blurred (`farBlur`); near layers darker and crisper.
- Randomness only through `rand(i, salt)`: every frame must render identically on every run.

## Open-source assets

Characters are always our own rigs (no library offers rigged, lip-synced SVG people). Props and small
background objects may come from permissively licensed libraries, vendored under `src/vendor/<library>/`
with the licence file and a README naming the source: currently Microsoft Fluent Emoji Flat (MIT), with
our ink outline added and colours overridable (`recolor`). Prefer CC0 or MIT; CC BY needs a credit in the
video description. Draw the story's key objects ourselves; use vendored art for small or distant things.

