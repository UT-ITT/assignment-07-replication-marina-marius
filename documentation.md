# Documentation

<Text about the project scope / MVP>

## 1. Paper Selection
For the Paper selection we looked for papers that have the following attributes:
-   doable in two weeks
-   an interesting interaction technique
-   a sufficient technique (not to easy and not to hard)
-   possibility to make a creative/funny replication for our beloved tutors (>ᴗ•)

With these categories we selected 10 Papers and discussed their advantages and disadvantages. The winner is ...... not one but two papers??? (O.O)

- Harmonionz: Rescue The Planet - A Voice Visualizing Game that Match Pitch with Color (pitch–to–color mapping in a collaborative voice game)
- Color Singer: Composing Music via the Construction of LEGO Blocks with Various Colors (color–to–pitch mapping using LEGO and a light sensor)

> A shoutout goes to the "interactive paper tearing" paper (Ljemble et al. 2015) because it is so funny and hilarious. Unforunately not posible in the “two weeks” since *whisper* dont tell anyone, but we also have multiple other courses *whisper* (Now you need to *gasp*).

But why now two Papers? Lets give you some Background first of the other papers that got killed one by one during our conquest process...

### The unloved unchoosen Papers
From our initial pool, we quickly realized that many papers failed our “two weeks, one laptop, zero lab hardware and not being able to recycling much of old ITT assignments” test:
- Some systems relied on special hardware setups, like multi-touch tables or custom sensors that we didn't build in the ITT course.
- Others were complex full games / systems with multiple scenes, narrative structures, custom audio pipelines, or machine learning components that would be hard to replicate in 1–2 weeks.
- A few were “this is super cool, but probably a whole project course on its own” in terms of implementation detail.

**For Example:**
The paper tearing simulation with sound models realistic tear geometry and procedural tearing sounds based on hand motion and cone-shaped deformations of paper.
- Super cool, super funny, but too much (╥﹏╥)
- So the judges ruled and the verdict was: “Love you, but you belong in my private side‑projects folder, not in the 2‑week ITT graveyard.”

Now my fellow readers, we reached the storytime of: "the Prophecy of the two choosen Papers"

### The choosen Paper(s)
Once upon a time, in the far‑away kingdom of ITT,<br>
two humble students set out on a quest:<br>

>_Find a paper that is doable in two weeks and still impresses the local tutor‑wizards_<br>

They searched the lands of CHI, PLAY, and mysterious PDF scrolls,<br>
fought off dragons named “required hardware” and “way too many user studies”,<br>
and finally discovered two magical artifacts:<br>
- The Harmonionz scroll, which whispered the secret of turning voice pitch into color and making players sing to save a planet.
- The Color Singer relic, forged from LEGO blocks and light sensors, which could turn rainbow‑colored bricks into actual music.<br>

The prophecy spoke of a rare alignment:
> “When pitch meets color and color meets pitch,
> two papers shall stand where one assignment is required.”

So the brave students proposed a daring spell:
- Take the Harmonionz magic and build a pitch => color prototype
- Extend it with a color => pitch ritual, inspired by Color Singer, to show that the same cross‑modal magic can be cast in both directions

But alas, in this land no hero may choose their own destiny.<br>
For above them sits the Council of Tutors, wise wizards of replication,<br>
who hold the ultimate power to proclaim:<br>

- “Yes, this is a noble replication + extension!”
=> and Harmonionz becomes the Chosen One.

- Or: “Nay, thou hast strayed too far from the original scroll!”
=> and Color Singer is crowned as the official quest paper, with a pure color‑to‑pitch implementation and fewer side‑quests.

And so, our heroes have carefully explained both paths, placed their candidate scrolls on the altar of the Discoed Chat, now patiently awaiting the judgment of the tutor‑wizards.

_To be continued..._



(https://www.etymonline.com/search?q=unfortunately)
(https://thehistoryofengland.co.uk/resource/glossary-of-medieval-terms/)

# 2. Implementation
How did we implement all of that? 
## Audio and Color Mapping
**Audio**: We used the microphone to capture the audio input from the user. The audio is then processed to extract the pitch and frequency information, which is used to determine the corresponding color or musical note.

**Color Mapping**: We implemented a mapping between pitch and color, allowing users to see visual representations of the audio input. The mapping is based on the frequency of the audio signal, with different frequencies corresponding to different colors. It follows the implementation of the Harmonionz paper, where specific frequency ranges are associated with specific colors. Durint the coding, it was very hard to actually hold a pitch (and therefor color), so we decided to reduce the time to holt the pitch to 0.5 seconds, which is a lot easier to achieve for the user.

## Gesture Recognition
We used mediapipe to implement gesture recognition as in previous assigments. For the game it was not exact enough, so we patched it: instead of feeding the raw pinch signal straight into the game logic, we turn a detected pinch into an actual OS-level mouse click (press on pinch, release on release), with the cursor position smoothed via an EMA to stop the visible shaking from noisy per-frame landmarks. This also meant we could reuse pyglet's existing on_mouse_press/on_mouse_drag/on_mouse_release handlers, so the gems and gates don't care whether they got clicked by a real mouse or a pinch — same code path either way.

The trickiest part was that a single pinch-distance threshold made the pinch check flicker true/false whenever fingers jittered near the line, which fired press/release/press/release instead of one clean "held" click. We fixed it with two thresholds instead of one: entering a pinch requires the fingers to get closer together, while leaving it tolerates them drifting a bit further apart before letting go. That little bit of hysteresis was enough to make dragging feel stable (>ᴗ•)

## Sounds
As for every good game, we needed sounds. Not only because I didnt want to learn for my other exams, but for the feedback for the user. We play a click sound when the fingers connect and disconnect, so the user "feels" the pinch gesture.
Additionally, a sound is played when the user hits the crystal correctly. Adding sound was rather easy

Background music was created by me and was purely because Machine Learning is hard and music is not.