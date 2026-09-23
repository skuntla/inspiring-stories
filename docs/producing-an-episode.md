# Producing an episode

The workflow from a story idea to approved images. Narration and rendering come in a later
change.

Run the commands from the repository root, with the virtual environment active
(`source .venv/bin/activate`) or as `.venv/bin/story …`.

## Once per series

### 1. Install the ChatGPT instructions

```bash
pbcopy < series/willow-meadow/chatgpt-project-instructions.md
```

Paste the result into the ChatGPT Project's **Instructions** field. Optionally upload
`series/willow-meadow/chatgpt-reference.md` to the Project's files. Re-paste the instructions
whenever the series changes. `story brief willow-meadow --out series/willow-meadow/chatgpt-project-instructions.md`
regenerates them.

### 2. Generate the reference images

```bash
story prompts series/willow-meadow
```

Open `series/willow-meadow/build/prompts/index.md` and work through it in order. For each
prompt file: attach the listed images, paste the prompt into Gemini, and save the result at
the "Save as" path. The style reference comes first, then each character's front view, and
the other views of each character attach that front view.

```bash
story images series/willow-meadow        # checks every reference; writes build/contact-sheet.png
story approve series/willow-meadow references
git add series/willow-meadow && git commit -m "Approve Willow Meadow references"
```

To regenerate one image, replace its file and rerun `story images`. The approval turns
**stale** and names the changed file; approve again once it looks right.

## Every episode

### 3. Write and lock the story in ChatGPT

Brainstorm in the Project. When the storyboard is right, say **"Lock this story"**.

```bash
story new willow-meadow "Pip and the Foggy Path" --date 2026-09-22
# paste ChatGPT's YAML into episodes/2026-09-22-pip-and-the-foggy-path/episode.yaml
story validate episodes/2026-09-22-pip-and-the-foggy-path
```

If validation reports errors, paste the report back into ChatGPT and ask for the fixed,
complete YAML.

### 4. Generate the images

```bash
story prompts episodes/2026-09-22-pip-and-the-foggy-path
```

Work through `build/prompts/index.md` in the episode folder, in order:

1. **Location anchors** (`location-*.md`): one per place used by several shots. They are
   attached to every shot set there, so generate them first.
2. **Shots** (`s01.md`, `s02.md`, …).
3. **Thumbnail** (`thumbnail.md`). It's required. Draw no text: the title is added later.

### 5. Check, review and approve

```bash
story images episodes/2026-09-22-pip-and-the-foggy-path
```

Fix every error (missing, duplicate, not 16:9, too small). Size warnings below 1920×1080
are acceptable. Open `build/contact-sheet.png` in the episode folder and check characters,
places and continuity. Regenerate any shot that's off, then run `story images` again.

```bash
story approve episodes/2026-09-22-pip-and-the-foggy-path images
git add episodes/2026-09-22-pip-and-the-foggy-path && git commit -m "Approve Foggy Path images"
```

Approved images are committed: Gemini can't reproduce them. If the story is relocked, an
image replaced, or a series reference regenerated, `story images` shows the approval as
**stale** and lists what changed.
