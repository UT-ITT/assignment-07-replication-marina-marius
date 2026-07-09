# Possible Papers for an ITT / Interaction Techniques Recreation Project

The point here is not to reproduce the papers perfectly one-to-one, but to find good references where the core idea is manageable and could be turned into a fun own version within roughly 1.5 weeks.

I grouped the papers by theme so it is easier to see which ones lean more toward webcam input, voice, AR, or humor/interface design.

## 1. Picture, Color, and Object Trigger Systems

### Lu et al. (2024) – Color Singer: Composing Music via the Construction of LEGO Blocks with Various Colors

**Short summary**  
This paper presents a playful system where differently colored LEGO blocks or drawn color areas are translated into musical notes. The really useful part here is not the LEGO hardware itself, but the general idea of mapping simple visual properties to a surprising and creative output.

**Interaction/Technique**  
Color detection or brightness regions are mapped to notes. Users build or draw something, the system reads the visual differences, and music is generated from that input.

**Requirements**  
Webcam or phone camera, colored cards / printed color patches / drawn color fields, laptop. The original uses LEGO Mindstorms, but for a recreation it would make much more sense to reduce it to pure camera-based input.

**Effort estimate**  
Very doable within 1.5 weeks if it is reframed as something like "hold color cards in front of the camera -> trigger sound / events / game mechanics." Much more realistic than trying to rebuild the original hardware setup.

**Ideas for recreations (that could be funny)**  
- A color-spell system where red, blue, and green cards cast ridiculous spells.
- A "bad conductor" version where wrong color combinations trigger chaotic music on purpose.
- Doodles or color patches generate not only tones, but weird character voices or silly NPC reactions.

### Kim et al. (2023) – Bubbleu: Exploring Augmented Reality Game Design with Uncertain AI-based Interaction

**Short summary**  
Bubbleu is an AR pet game on a smartphone where real objects are recognized through the camera and the virtual pet reacts to them. What makes it especially interesting is not just the object recognition, but also how the game design handles uncertainty and recognition errors in a playful way.

**Interaction/Technique**  
Camera-based object recognition plus AR feedback. Real objects like fruit, a bottle, or a hand are detected and trigger different reactions from a virtual pet.

**Requirements**  
Smartphone or webcam, household objects, and ideally a simplified recognition setup using only a few objects or markers. For a student project, a small 2D or pseudo-AR prototype would probably be smarter than trying to build a full AR game.

**Effort estimate**  
Medium to rather high. If the goal is full AR and robust object recognition, it can get too big quickly. If it is reduced to 4-5 clearly distinguishable objects or markers, it becomes much more realistic.

**Ideas for recreations (that could be funny)**  
- A virtual pet that completely misinterprets real objects and turns that into comedy.
- A dramatic pet that reacts to a banana as if it were a legendary artifact.
- Object-feeding with exaggerated effects, e.g. coffee makes the pet hyperactive, a donut makes it philosophical.

## 2. Voice, Audio, and Multisensory Games

### Hagerer et al. (2017) – VoicePlay: An affective sports game operated by speech emotion recognition

**Short summary**  
This paper describes a sports game controlled through detected emotions in the voice. Instead of only using volume or keywords, it tries to use affective vocal states as actual gameplay input.

**Interaction/Technique**  
Speech emotion recognition as input for a game mechanic. So not just "loud = jump," but more like "angry / happy / sad" influences what happens in the game.

**Requirements**  
Laptop with microphone, audio processing, and ideally an existing library or pretrained model. Without existing tools, this would be risky for the time frame.

**Effort estimate**  
Only partly realistic within 1.5 weeks. If the goal is real emotion classification, this is probably too risky. A simplified version based on loudness, pitch, and speaking speed as substitutes would be much safer.

**Ideas for recreations (that could be funny)**  
- A "Drama Olympics" game where players have to speak in an absurdly theatrical way.
- A mini sports game where exaggerated motivation or fake suffering earns points.
- Instead of real emotion recognition: a "coach" that constantly misreads the player's voice and overreacts to everything.

### Wu & Rank (2015) – Spatial Audio Feedback for Hand Gestures in Games

**Short summary**  
This paper looks at gesture interaction in games and how spatial, diegetic audio feedback can support hand gestures. What is especially interesting is that audio is not only the result of the gesture, but also helps structure the interaction before, during, and after the gesture.

**Interaction/Technique**  
Hand gestures plus responsive audio feedback. The audio signals what might happen next, accompanies the gesture while it is being performed, and confirms or comments on the outcome.

**Requirements**  
The original uses more specialized gesture hardware; for a recreation, it would make much more sense to replace that with a webcam and a simple hand-tracking library. Also needed: laptop, speakers or headphones.

**Effort estimate**  
Manageable in a simplified version. The safest approach would be not to copy the whole audio-only setup, but to build 2-3 clear gestures with funny spatial or narrative sound feedback.

**Ideas for recreations (that could be funny)**  
- Magic gestures where the game already "guesses" what the player is trying to do through sound.
- A very silly wizard-school prototype where failed gestures trigger embarrassing sounds or dumb comments.
- An invisible-object-throwing game with exaggerated 3D sound and overly dramatic hit feedback.

### Kim et al. (2021) – Harmonionz, Rescue The Planet: A Voice Visualizing Game that Match Pitch with Color

**Short summary**  
This is a cooperative game where voice is not just an extra input feature, but part of the story, the world, and the game mechanics themselves. Pitch is mapped to colors, and players have to produce matching notes to activate targets.

**Interaction/Technique**  
Pitch detection via microphone, visual feedback via color, combined with game objectives and role distribution. Voice is the core input, but not the only source of fun.

**Requirements**  
Laptop with microphone, pitch detection, and ideally a simple 2D game environment instead of a full 3D game. Two players are optional; it could also be simplified into a solo prototype.

**Effort estimate**  
Doable if the scope stays small. A reduced version with a 2D view, 3-5 pitch targets, and only a few gameplay elements would still fit into 1.5 weeks. The full cooperative game would probably be too much.

**Ideas for recreations (that could be funny)**  
- A weird boss-fight game where enemies are defeated by singing at them.
- Color-pitch spells where wrong notes create absurd side effects.
- A game where players have to hit embarrassingly precise notes while the system comments on mistakes like a talent-show jury.

## 3. Humor and Performance Interfaces

### Huang et al. (2026) – Not Human, Funnier: How Machine Identity Shapes Humor Perception in Online AI Stand-up Comedy

**Short summary**  
This paper examines how an AI comedian can seem funnier through machine-like self-presentation, timing, and live audience feedback than a more generic baseline chatbot. The interesting part here is really the combination of stage framing, joke rhythm, pauses, and reactions.

**Interaction/Technique**  
Humor interface with live-performance logic: short jokes, rhythmic delivery, audience feedback, and adaptation. The main contribution is more interaction dramaturgy than sensing hardware.

**Requirements**  
Laptop, a web or desktop UI, maybe TTS, buttons for laughter/applause, and optionally webcam or mic input as an extra trigger. No special hardware needed.

**Effort estimate**  
Very realistic within 1.5 weeks if treated as a compact performance prototype instead of trying to solve "AI comedy" in general. The interaction side is relatively manageable.

**Ideas for recreations (that could be funny)**  
- An "AI talent show" that reacts to your pose or objects in front of the webcam and turns them into dumb live commentary.
- A robot host that announces everything way too seriously and then drifts into absurd self-jokes.
- A version where harmless user actions are turned into a completely overdramatic stand-up routine.

### Weinberg et al. (2025) – Why So Serious? Exploring Timely Humorous Comments in AAC Through AI-Powered Interfaces

**Short summary**  
This paper comes from the AAC context, but it is very interesting because it explores how interfaces can help users insert well-timed humorous comments into ongoing conversations. The focus is on different UI variants that balance user control and automation.

**Interaction/Technique**  
Humor interface with context analysis, suggestions, keywords, bubble selection, and different degrees of user control. So this is more of an interaction design paper than a sensing paper.

**Requirements**  
Laptop, microphone for transcription or alternatively text input, and a simple web interface. For a recreation, the AI side could be simplified heavily with fixed templates or a small number of LLM prompts.

**Effort estimate**  
Doable if the project focuses on one or two interface ideas instead of trying to rebuild every variant. The UI logic is more realistic than many vision-heavy projects.

**Ideas for recreations (that could be funny)**  
- A "joke assist" for everyday situations that suggests absurd remarks based on keywords.
- A party or interview mode where users get context-based silly comments at the press of a button.
- A webcam version where recognized objects or facial expressions are turned into extra keywords for joke suggestions.

## 4. Material and Simulation Interaction

### Lejemble et al. (2015) – Interactive procedural simulation of paper tearing with sound

**Short summary**  
This paper focuses on interactive paper-tearing simulation including sound. What makes it interesting is the tight coupling between material behavior, visual response, and audio feedback.

**Interaction/Technique**  
Physics or material simulation plus sound synthesis or sound coupling to user interaction. The main goal is a convincing, responsive material feel.

**Requirements**  
Laptop, mouse, or touch input. No special hardware needed, but it does require more programming effort in simulation and audio than the other papers.

**Effort estimate**  
Medium to high. An exact recreation would probably be too ambitious for 1.5 weeks. A heavily simplified playful version could still be possible.

**Ideas for recreations (that could be funny)**  
- A "virtual office meltdown" where users tear digital papers and the system overreacts dramatically.
- A paper monster that can only be defeated by tearing, folding, or crumpling virtual sheets.
- A game where badly torn paper shapes are judged and mocked by a fake arts-and-crafts jury.

## Rough suitability overview

If the goal is really **something that can be built within 1.5 weeks**, these would probably be the rough priorities:

- **Very suitable:** Huang et al. (2026), Weinberg et al. (2025), Lu et al. (2024)
- **Good if the scope is reduced:** Wu & Rank (2015), Kim et al. (2021)
- **Only really sensible with strong simplification:** Kim et al. (2023), Hagerer et al. (2017), Lejemble et al. (2015)

The safest sweet spot is probably one of these:
- color / image -> surprising output,
- webcam gesture -> funny feedback,
- or humor / performance interface combined with a little bit of vision or text input.

## Ranking table

Scale for both rankings: **1 = lowest value**, **8 = highest value** within this set.  
For **complexity**, a higher number means harder to implement.  
For **fun/creativity**, a higher number means more potential for a funny or original recreation.

| Paper | Category | Complexity (1-8) | Fun/Creativity (1-8) | Short comment |
|---|---|---:|---:|---|
| Lu et al. (2024) – Color Singer | Picture / color triggers | 1 | 6 | Probably the most implementation-friendly, but it needs a strong funny twist on top. |
| Huang et al. (2026) – Not Human, Funnier | Humor / performance interface | 2 | 7 | Very strong option if the focus is on interface, timing, and show effect instead of heavy sensing. |
| Weinberg et al. (2025) – Why So Serious? | Humor / assistive interface | 3 | 5 | Good UI concept, slightly less playful at first glance, but easy to extend in a fun direction. |
| Wu & Rank (2015) – Spatial Audio Feedback for Hand Gestures in Games | Gestures + audio | 4 | 8 | Could become extremely funny if gestures and sound are designed in a deliberately silly way. |
| Kim et al. (2021) – Harmonionz | Voice + color + game | 5 | 6 | Nice mapping idea, but needs a bit more technical setup and balancing. |
| Lejemble et al. (2015) – Paper Tearing | Material simulation | 6 | 4 | Original, but less directly funny unless a strong extra concept is added. |
| Kim et al. (2023) – Bubbleu | AR + object recognition | 7 | 7 | Very charming direction, but easy to let it grow out of scope. |
| Hagerer et al. (2017) – VoicePlay | Voice emotion input | 8 | 5 | Interesting, but probably the riskiest one to make robust in a short time. |