# Speaker notes: The Dependency Graph Your Tests Can't See

JS Monthly London #212, 12 November 2026, 8:00 to 8:45 PM.

## 01 Title

[0:00 · 30 sec]
[Walk on. Smile. Let the title sit for a second.]

SAY:
Hi everyone, Kayode here.
Tonight we're talking about a bug that no test will ever catch.
Nothing crashes. Nothing goes red. The numbers look amazing.
And by the end, you'll be able to spot it in about ten seconds.

No Python knowledge needed. If you've used npm, you already know most of this.

NEXT: start with something every JS dev has seen.

## 02 Seen this?

[0:30 · 1.5 min]
[ASK] Hands up if you've seen this warning.
[Wait. Most hands go up. Laugh with them.]

SAY:
a.js imports b.js. b.js imports a.js. A loop.
And our bundler catches it for us. We don't go looking.
The tooling knows what depends on what, so it can warn us.

Hold on to that idea: tools can only warn us about loops
when somebody has written the dependencies down.

NEXT: now something from outside code.

## 03 BMI

[2:00 · 1.5 min]
SAY:
Something we've all seen at the doctor or on a fitness app. BMI.
BMI is made from two numbers. Weight and height. That's it.

Imagine someone trains a model.
Input: weight and height. Output: BMI.
It scores 0.998. Nearly perfect.

[ASK] Who's impressed?
[Pause. Nobody is.]

Exactly. We all know the formula.
The model didn't learn anything. It rediscovered a sum we gave it.

NEXT: quick pause, what does 0.998 even mean?

## 04 What R² means

[3:30 · 1 min]
[Quick. This slide is a key, not a lecture.]

SAY:
Quick one, because this number matters for the rest of the talk.
R squared tells us how close the model's guesses are to the real answers.

Left: 1.0. Every dot on the line. Every guess spot on.
Middle: about 0.5. A rough idea.
Right: zero. No idea at all.

In real life, with messy data, 0.5 is often a good result.
0.998 is almost unheard of.

NEXT: so back to BMI, but now let's hide the formula.

## 05 Now hide the formula

[4:30 · 1 min]
SAY:
Now imagine the formula is on page 80 of a PDF,
written by a different organisation.
The two columns arrive in a CSV. No recipe attached.
Same model. Same 0.998.

[ASK] Would you spot it?
[Pause.]

Honestly, most of us wouldn't. We'd celebrate.
This is what a lot of public data looks like.

NEXT: and this is exactly what happened to us.

## 06 Then it happened to us

[5:30 · 1 min]
[EDIT THIS SLIDE: say the lab name and the project in one line.]

SAY:
In our lab we build models on free public data.
CDC, FEMA, the US Census.
It's good data, and anyone can check our work. That's why we use it.

We were building a model. We ran it.

NEXT: here's the score we got.

## 07 Our score

[6:30 · 1 min]
[Let the chart land. Don't talk for 3 seconds.]

SAY:
This is real. CDC's Social Vulnerability Index.
9,041 neighbourhoods in California. Proper cross-validation.
Every dot is one neighbourhood. They all sit on the line.

R squared 0.998.

[ASK] Who would ship this?
[A few hands. Good.]

NEXT: put it next to something we just saw.

## 08 Look familiar?

[7:30 · 1 min]
[Point left, then right.]

SAY:
Left: BMI from weight and height.
Right: our model on CDC data.
Same line. Same score. 0.998 on both.

On the left, we knew the formula.
On the right, the formula was hidden from us.

Our CDC model had found its own BMI.

NEXT: so what was the hidden formula?

## 09 The loop

[8:30 · 1.5 min]
[Trace the top path with your hand, then the bottom path.]

SAY:
CDC builds a score called Theme 1 from exactly five columns.
Poverty, unemployment, housing cost, no diploma, no insurance.
That's the top path.

We gave our model the same five columns.
That's the bottom path.

So the answer went in, and the answer came out.
The model relearned CDC's formula.
It told us nothing new about the world.

This is called target leakage. Our inputs already contained the answer.

NEXT: so what does a real result look like?

## 10 Leak vs signal

[10:00 · 1.5 min]
SAY:
Left: the leak. A thin, perfect line.

Right: one column called internet access.
CDC ships it in the same file, but it's not part of the score.
It still relates to vulnerability. It scores 0.384.

That messy cloud is what a real relationship looks like.
Real life is noisy.

TAKEAWAY: when a score looks too clean, get suspicious.

NEXT: and here's the worst part.

## 11 Every check passed

[11:30 · 1 min]
SAY:
Tests passed. Lint passed. Cross-validation was done right.
The score was great.

Nothing in our pipeline asked the one question that mattered:
what was this data made from?

Our bundler would have caught a loop in our imports.
Nothing caught this one.

NEXT: and before you think this is only a data science problem...

## 12 It's in your code too

[12:30 · 2 min]
[Point at each card. This is the slide that makes it about THEM.]

SAY:
This isn't only a data science thing. You've probably got it at work.

Snapshot tests. Our code writes the snapshot,
then the test checks our code against it.
Expected equals actual, by construction. It can never fail.

AI evals. If the test questions leaked into the training data,
the model scores 95%. It isn't smart. It saw the answers.

Product metrics. Click rate is made from clicks.
Use click rate to predict clicks, and we get a beautiful, useless model.

Same loop every time. The answer sneaks in as an input.

[ASK] Anyone recognise one of these from their own codebase?
[Let a hand or two go up. Nod.]

NEXT: so how do JS tools stop loops? They write the graph down.

## 13 You already use one

[14:30 · 1.5 min]
SAY:
Every JS dev here trusts a dependency graph every day.
debug feeds body-parser. Both feed express. express feeds our app.
And package-lock.json writes all of that down.
That's why npm can warn us about loops and conflicts.

Now look at public data. The ACS survey feeds a Census estimate,
which feeds a FEMA risk score.
Is that written down anywhere a computer can read it?
No. There's no lock file for data.

One note: in all these drawings, sources sit at the top and flow down,
like a river. Upstream is where things come from.

NEXT: two questions worth asking about any column.

## 14 Two questions

[16:00 · 1 min]
SAY:
Two questions we can ask about any column.

Question one: where did this file come from?
Which website, which download.
Data catalogues record this really well.

Question two: what was this number made from?
Almost nobody records that.

And the leak always lives in question two.

NEXT: let's answer question two for a real dataset.

## 15 A real chain (1)

[17:00 · 30 sec]
SAY:
Here's FEMA's National Risk Index. The risk score for every US county.
Used for real decisions about real money.

[ASK] What do you think it's made from?
[Let one or two people guess.]

Let's walk upstream.

[CLICK]

## 16 A real chain (2)

[17:30 · 1 min]
SAY:
Route one, in blue.
The unemployment rate from the ACS survey
feeds a Census statistical model.
That becomes FEMA's social vulnerability,
which goes into the risk score.

So unemployment is already inside the risk score.

[CLICK] But that's not the only way in.

## 17 A real chain (3)

[18:30 · 1 min]
SAY:
Route two, in red. Pure arithmetic this time.
The same unemployment column feeds an index called BRIC,
which becomes community resilience, which also goes into the risk score.

One column. Two routes into the target.
Three different agencies along the way.
Nobody owns the whole picture.

If we predict the risk score using unemployment,
we're feeding it its own ingredient. Twice.

This all comes from FEMA's own published documentation.
It's there. It's just in a PDF.

NEXT: how to read any graph like this.

## 18 How to read a graph

[19:30 · 1 min]
SAY:
Boxes are datasets or columns. Arrows mean "used to make".

Find the target. That's our yellow box.
Everything above it is upstream. It was made from those.
Everything below it is downstream. Those were made from it.

The grey boxes off to the side have no path to the target.
Those are the safe inputs.

NEXT: there are only three shapes to look for.

## 19 Three shapes

[20:30 · 1.5 min]
SAY:
Shape one: the input sits upstream of the target.
The target was made from it. Stop.

Shape two: the input sits downstream.
The input was made from the target. Also stop.
That's the true circular case. Predicting the parent from its child.

Shape three: two inputs share a parent.
They're related to each other. Sometimes fine. Always worth a look.

That's all. Three shapes.

NEXT: now we write the graph down.

## 20 Step 1. Write it down

[22:00 · 1.5 min]
SAY:
Step one: write it down.
Think of it as a lock file for data.

One entry per dataset: what was it made from?
This entry says FEMA's social vulnerability is the Census estimate,
republished under a new name.

Two small extras make it honest.
Each box says what kind of number it is:
counted, predicted by a model, or plain arithmetic.
Each arrow says how sure we are:
certain, documented in the agency's method, or just inferred.

Plain YAML. In the repo. Reviewed in pull requests like any other code.

NEXT: quick game.

## 21 Spot the leak

[23:30 · 1.5 min]
[ENERGY UP. This is the audience moment.]

SAY:
Your turn.
We want to predict the FEMA risk score.
Here are three inputs. Which one is safe to use?

A: poverty rate. B: unemployment rate. C: rainfall.

[ASK] Shout it out. A, B or C?
[Let them shout. Repeat what you hear.]

Hold that thought. Let's walk the graph and see.

[CLICK]

## 22 Step 2. Walk it

[25:00 · 1 min]
SAY:
Step two: walk it.
Start at the target. Follow every arrow upstream.
Poverty: upstream. Out.
Unemployment: upstream, twice. Out.
Rainfall: no path at all. Safe.

[Point at whoever shouted C.] You were right.

A computer does this walk in milliseconds.
And it finds every route, not only the shortest.

NEXT: the walk gives us one of four answers.

## 23 Step 3. Four answers

[26:00 · 1 min]
SAY:
Step three. Four possible answers.

FAIL: an input sits on the target's path.
REVIEW: two inputs share a parent. A human should look.
PASS: we traced the target, and the inputs are clear of it.
UNTRACED: nobody has written down this target's lineage yet.

That last one matters. An empty graph tells us nothing.
So it never gets to count as a pass.

NEXT: and then we automate it.

## 24 Step 4. Run it on every push

[27:00 · 1 min]
SAY:
Step four: put it in CI, right next to the tests.
Every push, the lineage check runs.
It takes about a tenth of a second. No network.

Leak found: build goes red.
Broken manifest: build goes red too.
And a typo in a column name? Also red.
A name the tool doesn't know can never be cleared.

NEXT: let's watch it go red for real.

## 25 Demo

[28:00 · 2 min]
[LIVE DEMO. Terminal open, font large, already in the repo folder.]

TYPE:
python3 lint_lineage.py --target FEMA_NRI.risk_score --covariates ACS.EP_POV150 ACS.EP_UNEMP

SAY while it prints:
FAIL. Two errors. Poverty: one route. Unemployment: two routes.
The same two routes we drew by hand.

TYPE: echo $?
SAY: Exit code 1. In CI, that's a red build.

BONUS: rerun with a typo, EP_UNEMPP. Still FAIL. Typos can't sneak through.

[IF THE DEMO BREAKS] Stay calm: "This is exactly what it prints." Point at the screenshot.

NEXT: time to admit where we got it wrong.

## 26 Where we got it wrong

[30:00 · 1.5 min]
SAY:
We got this wrong ourselves.

The CDC file has a handful of extra columns that aren't in the score.
We marked 8 of them as safe.

Turns out 7 of them add up, exactly, to one of the score's own inputs.
The chart on the right: every dot on the line. Zero difference.
So they were inside the score all along, just one step removed.

Our own tool would have cleared them. Now it doesn't.

LESSON: read the method, then check it in the data.

NEXT: the graph only helps if we keep it right.

## 27 Looking after the graph

[31:30 · 1 min]
SAY:
Five habits.
One: keep it in the repo and review it in PRs.
Two: every arrow says how sure we are.
Three: log every fix. Our first check of our own file found six mistakes.
Four: unknown names fail the build.
Five: when a dataset ships a new version, check it again.

Treat it like code. Because it is.

NEXT: back to where we started.

## 28 Next time

[32:30 · 1 min]
SAY:
Back to BMI.
Next time a score looks too good, ask one question:
is this BMI?

And if you want more, three questions for any input column:
What was it made from?
Does it share a parent with our target?
Who published both?

If we can't answer them, that column is untraced.
That's fine. Now we know what we don't know.

NEXT: thank you.

## 29 Thank you

[33:30 · then Q&A]
SAY:
Thank you.
If this was useful, scan the code and say hello on LinkedIn.
Happy to chat about your own data afterwards.

[ASK] Questions?

BACKUP ANSWERS:
"Is this only a Python thing?" No. Any project with a dependency graph and a CI job can do it.
"Doesn't cross-validation catch it?" No. The leak is inside every fold.
"Who should write these graphs?" Ideally the agencies themselves. Until then, any team can start one for its own project.

