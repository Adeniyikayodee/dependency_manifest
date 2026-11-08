const pptxgen = require('pptxgenjs');
const fs = require('fs');
const [,, slidesJson, pngDir, out] = process.argv;
const slides = JSON.parse(fs.readFileSync(slidesJson));
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Kayode Adeniyi';
pres.title = "The Dependency Graph Your Tests Can't See";
pres.subject = 'JS Monthly London #212';
pres.defineSlideMaster({ title: 'IMAGE', background: { color: 'FFFFFF' }, objects: [] });
const sections = { 1: 'The story', 13: 'Reading the graph', 20: 'Looking after it', 28: 'Close' };
let current;
slides.forEach((s, i) => {
  const n = i + 1;
  if (sections[n]) { current = sections[n]; pres.addSection({ title: current }); }
  const slide = pres.addSlide({ masterName: 'IMAGE', sectionTitle: current });
  slide.addImage({ path: `${pngDir}/slide-${String(n).padStart(2, '0')}.png`, x: 0, y: 0, w: 10, h: 5.625,
                   altText: s.title, objectName: `Slide ${n}: ${s.title}` });
  slide.addNotes(s.notes);
});
pres.writeFile({ fileName: out }).then(f => console.log('wrote', f));
