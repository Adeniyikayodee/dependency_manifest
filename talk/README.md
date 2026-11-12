# The Dependency Graph Your Tests Can't See

Talk for JS Monthly London #212, 12 Nov 2026, Red Dog Saloon Hoxton Square.

## Slides

- Online deck (Claude artifact, with speaker notes): https://claude.ai/artifact/GMg1K7jUkWekmRazjbVAU1
- PowerPoint with speaker notes: `The Dependency Graph Your Tests Can't See.pptx`
- Excalidraw source: `dependency-graph-talk.excalidraw` (open at excalidraw.com)
- Speaker notes as text: `dependency-graph-talk-notes.md`
- Slide images: `slides-png/`
- Charts and the QR code: `images/`

The online deck is the current version: 28 slides telling the GRMI Katcha
story, from floods and fieldwork to the river that sat on both sides of the
model. `artifact/` below mirrors it. The PowerPoint, PNGs and notes file are
from the first draft.

## To do before the talk

- Check the period on slide 2. The 44% figure covers 2000 to 2019.
- Check slide 3 against its source, which covers 1990 to 2022.
- Check that slide 15 matches how the flood input and label were built.

## Rebuilding

The scripts in `build/` made the deck.

- `slides.py` writes the Excalidraw file, using `excali.py` and the notes in `notes.py`.
- `charts.py`, `bmi.py`, `r2explain.py` and `term.py` make the images.
- `server.py` and `web/export.html` export each frame to PNG with Excalidraw's own renderer.
- `build_ppt.js` builds the PowerPoint from the PNGs and `slides.json`.
- `artifact/` holds the files behind the online deck.
