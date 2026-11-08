# The Dependency Graph Your Tests Can't See

Talk for JS Monthly London #212, 12 Nov 2026, Red Dog Saloon Hoxton Square.

## Slides

- Online deck (Claude artifact, with speaker notes): https://claude.ai/artifact/GMg1K7jUkWekmRazjbVAU1
- PowerPoint with speaker notes: `The Dependency Graph Your Tests Can't See.pptx`
- Excalidraw source: `dependency-graph-talk.excalidraw` (open at excalidraw.com)
- Speaker notes as text: `dependency-graph-talk-notes.md`
- Slide images: `slides-png/`
- Charts and the QR code: `images/`

## To do before the talk

- Add the lab line on slide 6.
- Rehearse the live demo on slide 25.

## Rebuilding

The scripts in `build/` made the deck.

- `slides.py` writes the Excalidraw file, using `excali.py` and the notes in `notes.py`.
- `charts.py`, `bmi.py`, `r2explain.py` and `term.py` make the images.
- `server.py` and `web/export.html` export each frame to PNG with Excalidraw's own renderer.
- `build_ppt.js` builds the PowerPoint from the PNGs and `slides.json`.
- `artifact/` holds the files behind the online deck.
