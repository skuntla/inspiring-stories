# inspiring-stories

Stories become narrated, animated 16:9 videos, drawn entirely as SVG from code. The Python `story`
CLI (`.venv/bin/story`) validates the manifest, voices it (Kokoro), builds the timeline and music, and
renders through Remotion in `render/`. Changes are planned with OpenSpec (`openspec/`).

Before building or changing an episode, read:

- `render/DIRECTING.md`: workflow, pacing, shot grammar, acting, walking, timing to the voice, review checklist
- `render/STYLE.md`: how components are drawn and where they live

Reuse before drawing: `render/src/kit/` (rigs, faces, walk cycle, scenery, captions) and
`render/src/common/` (ready-made close-ups and cards) serve every series. New lessons go into
`DIRECTING.md`, not only into one episode.
