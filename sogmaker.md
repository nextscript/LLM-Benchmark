# sogmaker.md — Songwriting Benchmark Test Prompts

## Ziel

Diese Datei definiert fertige Test-Prompts für einen Songwriting-Benchmark. Damit soll geprüft werden, ob ein LLM wirklich gut im Songwriting ist oder nur generische Liedtexte erzeugt.

Bewertet werden unter anderem:

- Hook-Stärke
- Refrain-Qualität
- Vers-/Story-Aufbau
- Reime
- Metrik und Singbarkeit
- emotionale Klarheit
- Genre-Treue
- natürliche Sprache
- Suno-/AI-Music-Format
- Originalität
- Rewrite-/Verbesserungsfähigkeit
- Mehrsprachigkeit

---

## Allgemeine Bewertungslogik

Jeder Songwriting-Test sollte folgende Felder speichern:

```python
{
    "prompt_key": "songwriting_hook_pop_chorus",
    "category": "songwriting",
    "sub_category": "hook",
    "language": "english",
    "genre": "pop",
    "difficulty": "medium",
    "text": "...",
    "checks": ["hook", "simple_language", "singable", "repetition"]
}
```

---

## Score-Badges

Empfohlene Badge-Kategorien:

```text
Hook: Kann gut / Kann mittel / Kann schlecht
Reime: Kann gut / Kann mittel / Kann schlecht
Metrik: Kann gut / Kann mittel / Kann schlecht
Story: Kann gut / Kann mittel / Kann schlecht
Emotion: Kann gut / Kann mittel / Kann schlecht
Genre: Kann gut / Kann mittel / Kann schlecht
Suno: Kann gut / Kann mittel / Kann schlecht
Originalität: Kann gut / Kann mittel / Kann schlecht
Deutsch: Kann gut / Kann mittel / Kann schlecht
Englisch: Kann gut / Kann mittel / Kann schlecht
Griechisch: Kann gut / Kann mittel / Kann schlecht
```

Farben:

```text
Grün = Kann gut
Orange = Kann mittel
Rot = Kann schlecht
```

Schwellenwerte:

```python
if score >= 75:
    rating = "good"
    label = "Kann gut"
elif score >= 45:
    rating = "medium"
    label = "Kann mittel"
else:
    rating = "bad"
    label = "Kann schlecht"
```

---

# 1. Hook Tests

## `songwriting_hook_pop_chorus`

**Kategorie:** Hook  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Write a radio-ready pop chorus about missing someone you still love.

Requirements:
- 4 to 6 short lines
- clear emotional hook
- simple everyday language
- strong final line
- easy to sing
- repeat the main emotional phrase at least once
- no abstract poetry
- no explanations
```

Checks:

```python
["hook", "chorus", "simple_language", "singable", "repetition", "strong_final_line"]
```

---

## `songwriting_hook_greek_pop_chorus`

**Kategorie:** Hook  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Medium

```text
Write a modern Greek pop chorus about a missed chance in love.

Requirements:
- Greek lyrics only
- 4 to 6 short lines
- native-sounding Greek
- simple emotional words
- clean end rhymes
- strong repeated hook phrase
- no translation notes
- no explanations
```

Checks:

```python
["greek", "hook", "chorus", "rhyme", "native_sound", "simple_language"]
```

---

## `songwriting_hook_german_schlager`

**Kategorie:** Hook  
**Sprache:** Deutsch  
**Genre:** Schlager / Pop-Schlager  
**Schwierigkeit:** Medium

```text
Schreibe einen eingängigen deutschen Schlager-Refrain über eine Liebe, die nie ganz vorbei war.

Anforderungen:
- nur deutscher Liedtext
- 4 bis 6 kurze Zeilen
- klare Hook
- einfache Alltagssprache
- Mitsing-Gefühl
- keine kitschigen Floskeln
- keine Erklärung
```

Checks:

```python
["german", "hook", "schlager", "chorus", "singable", "no_cheesy_phrases"]
```

---

# 2. Refrain Tests

## `songwriting_chorus_emotional_release`

**Kategorie:** Chorus  
**Sprache:** Englisch  
**Genre:** Pop Ballad  
**Schwierigkeit:** Medium

```text
Write a chorus that feels bigger and more emotional than the verse.

Theme: A person regrets never saying "I love you".

Requirements:
- 6 lines maximum
- the chorus must feel like an emotional release
- include one memorable repeated phrase
- no complex metaphors
- no filler lines
- lyrics only
```

Checks:

```python
["chorus", "emotional_release", "repetition", "no_filler", "memorable_phrase"]
```

---

## `songwriting_chorus_final_line`

**Kategorie:** Chorus  
**Sprache:** Englisch  
**Genre:** Mainstream Pop  
**Schwierigkeit:** Hard

```text
Write three different chorus versions for the same song idea.

Song idea: Someone cannot forget the voice of the person they lost.

Requirements:
- each chorus must have 4 lines
- each chorus needs a different final line
- final line must be the strongest line
- simple language
- no explanations
```

Checks:

```python
["multiple_versions", "chorus", "final_line", "simple_language", "hook_variation"]
```

---

# 3. Verse Tests

## `songwriting_verse_story_setup`

**Kategorie:** Verse  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Write Verse 1 for a pop song.

Story:
A man sees an old photo and remembers the woman he never confessed his feelings to.

Requirements:
- 8 lines maximum
- set up the story clearly
- no chorus lines
- no overused phrases
- natural spoken language
- lyrics only
```

Checks:

```python
["verse", "story_setup", "natural_language", "no_cliche", "clear_scene"]
```

---

## `songwriting_verse_greek_story`

**Kategorie:** Verse  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Medium

```text
Γράψε την πρώτη στροφή για ένα ελληνικό pop τραγούδι.

Ιστορία:
Κάποιος βλέπει ένα παλιό μήνυμα και θυμάται τη γυναίκα που δεν τόλμησε ποτέ να κρατήσει.

Απαιτήσεις:
- μόνο ελληνικοί στίχοι
- μέχρι 8 γραμμές
- φυσική καθημερινή γλώσσα
- να βγάζει νόημα
- χωρίς μετάφραση
- χωρίς εξηγήσεις
```

Checks:

```python
["greek", "verse", "story_setup", "natural_language", "meaningful", "no_translation"]
```

---

# 4. Pre-Chorus Tests

## `songwriting_prechorus_tension_build`

**Kategorie:** Pre-Chorus  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Write a pre-chorus that builds tension before a big chorus.

Theme: The singer is about to admit they still love someone.

Requirements:
- 4 lines
- emotional build-up
- last line must lead naturally into a chorus
- no direct chorus repetition
- lyrics only
```

Checks:

```python
["pre_chorus", "tension", "build_up", "chorus_lead_in", "emotion"]
```

---

## `songwriting_prechorus_greek_build`

**Kategorie:** Pre-Chorus  
**Sprache:** Griechisch  
**Genre:** Greek Pop / Laiko-Pop  
**Schwierigkeit:** Medium

```text
Γράψε ένα pre-chorus για ελληνικό pop/laiko τραγούδι.

Θέμα:
Ο τραγουδιστής κρατάει μέσα του λόγια που δεν είπε ποτέ.

Απαιτήσεις:
- μόνο ελληνικά
- 4 γραμμές
- να ανεβάζει ένταση πριν το ρεφρέν
- φυσική γλώσσα
- τελευταία γραμμή να οδηγεί καθαρά στο ρεφρέν
- χωρίς εξηγήσεις
```

Checks:

```python
["greek", "pre_chorus", "build_up", "natural_language", "chorus_lead_in"]
```

---

# 5. Bridge Tests

## `songwriting_bridge_emotional_turn`

**Kategorie:** Bridge  
**Sprache:** Englisch  
**Genre:** Pop Ballad  
**Schwierigkeit:** Hard

```text
Write a bridge for a pop ballad.

Story:
The singer finally admits that the real mistake was not losing the person, but staying silent when it mattered.

Requirements:
- 4 to 6 lines
- add a new emotional perspective
- do not repeat the chorus
- make the final chorus feel stronger afterward
- lyrics only
```

Checks:

```python
["bridge", "emotional_turn", "new_perspective", "no_chorus_repeat", "final_chorus_setup"]
```

---

## `songwriting_bridge_german_regret`

**Kategorie:** Bridge  
**Sprache:** Deutsch  
**Genre:** Pop-Ballade  
**Schwierigkeit:** Medium

```text
Schreibe eine Bridge für eine deutsche Pop-Ballade.

Thema:
Der Sänger versteht erst spät, dass sein Schweigen alles zerstört hat.

Anforderungen:
- nur deutscher Liedtext
- 4 bis 6 Zeilen
- neue emotionale Wendung
- kein Refrain-Recycling
- natürlich singbar
- keine Erklärung
```

Checks:

```python
["german", "bridge", "emotional_turn", "no_recycling", "singable"]
```

---

# 6. Full Song Structure Tests

## `songwriting_full_pop_structure`

**Kategorie:** Full Song  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Hard

```text
Write a complete radio-ready pop song.

Theme:
Someone lost the love of their life because they were too afraid to speak.

Structure:
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Pre-Chorus]
[Chorus]
[Bridge]
[Final Chorus]
[Outro]

Requirements:
- chorus must be the strongest part
- verses must move the story forward
- bridge must add a new emotional angle
- simple singable language
- no explanations
- no translation
```

Checks:

```python
["full_song", "structure", "chorus", "verse_progression", "bridge", "singable"]
```

---

## `songwriting_full_greek_pop_suno`

**Kategorie:** Full Song  
**Sprache:** Griechisch  
**Genre:** Greek Pop / Laiko-Pop  
**Schwierigkeit:** Hard

```text
Write a complete Suno-ready Greek pop/laiko song.

Theme:
A man missed his chance with the woman he loved and still wonders if she ever felt the same.

Requirements:
- Greek lyrics only
- use section tags
- radio-ready structure
- strong chorus
- natural Greek wording
- clean rhymes where possible
- no explanations
- no translations

Structure:
[Instrumental Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Pre-Chorus]
[Chorus]
[Bridge]
[Final Chorus]
[Outro]
```

Checks:

```python
["greek", "suno", "full_song", "structure", "hook", "rhyme", "natural_language"]
```

---

## `songwriting_full_german_pop_rap`

**Kategorie:** Full Song  
**Sprache:** Deutsch  
**Genre:** Pop-Rap  
**Schwierigkeit:** Hard

```text
Schreibe einen kompletten deutschen Pop-Rap-Song.

Thema:
Jemand kommt nach einer Trennung nicht los, will aber stark wirken.

Struktur:
[Intro]
[Part 1]
[Pre-Hook]
[Hook]
[Part 2]
[Pre-Hook]
[Hook]
[Bridge]
[Final Hook]

Anforderungen:
- nur deutscher Text
- moderne Alltagssprache
- Hook muss eingängig sein
- Parts sollen eine Geschichte erzählen
- keine überladenen Reime
- keine Erklärung
```

Checks:

```python
["german", "pop_rap", "full_song", "hook", "story", "modern_language"]
```

---

# 7. Rhyme Tests

## `songwriting_rhyme_clean_end_rhymes`

**Kategorie:** Rhyme  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Write a 6-line pop chorus with clean end rhymes.

Theme: I still hear your name in every song.

Requirements:
- lines 2, 4, and 6 must rhyme
- no forced word order
- simple emotional language
- easy to sing
- lyrics only
```

Checks:

```python
["rhyme", "end_rhyme", "natural_word_order", "simple_language", "singable"]
```

---

## `songwriting_rhyme_greek_natural`

**Kategorie:** Rhyme  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Hard

```text
Γράψε ένα ελληνικό ρεφρέν με φυσικές ρίμες.

Θέμα:
Κάθε βράδυ σκέφτομαι ακόμα το όνομά σου.

Απαιτήσεις:
- μόνο ελληνικοί στίχοι
- 6 γραμμές
- οι γραμμές 2, 4 και 6 να κάνουν ρίμα
- όχι αναγκαστική σύνταξη
- φυσική γλώσσα
- χωρίς εξηγήσεις
```

Checks:

```python
["greek", "rhyme", "end_rhyme", "natural_syntax", "chorus"]
```

---

## `songwriting_rhyme_repair`

**Kategorie:** Rhyme Rewrite  
**Sprache:** Deutsch  
**Genre:** Pop  
**Schwierigkeit:** Hard

```text
Verbessere diesen Refrain, damit die Reime natürlicher und stärker werden.

Original:
Ich denke jede Nacht an dich
Und alles ist so schwer für mich
Ich wollte dir so vieles sagen
Jetzt muss ich diese Schmerzen tragen

Anforderungen:
- Bedeutung behalten
- bessere Reime
- natürlichere Sprache
- stärkerer Hook
- keine Erklärung
- nur den verbesserten Refrain ausgeben
```

Checks:

```python
["rewrite", "rhyme", "german", "meaning_preserved", "stronger_hook"]
```

---

# 8. Meter and Singability Tests

## `songwriting_meter_128bpm_dance_pop`

**Kategorie:** Meter  
**Sprache:** Englisch  
**Genre:** Dance Pop  
**Schwierigkeit:** Hard

```text
Write a verse and chorus for a 128 BPM dance-pop song.

Theme: Running back to someone you cannot forget.

Requirements:
- short rhythmic lines
- easy to sing
- chorus must be repetitive
- avoid lines longer than 9 syllables if possible
- include [Verse] and [Chorus] labels
- lyrics only
```

Checks:

```python
["meter", "128bpm", "short_lines", "singable", "repetition", "dance_pop"]
```

---

## `songwriting_meter_greek_singable`

**Kategorie:** Meter  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Hard

```text
Γράψε μια στροφή και ένα ρεφρέν για ελληνικό pop τραγούδι.

Θέμα:
Μια αγάπη που χάθηκε αλλά δεν έσβησε.

Απαιτήσεις:
- μόνο ελληνικά
- μικρές γραμμές
- φυσικός ρυθμός
- να τραγουδιέται εύκολα
- όχι μεγάλες προτάσεις
- βάλε [Verse] και [Chorus]
- χωρίς εξηγήσεις
```

Checks:

```python
["greek", "meter", "singable", "short_lines", "natural_rhythm", "section_tags"]
```

---

# 9. Storytelling Tests

## `songwriting_story_progression`

**Kategorie:** Storytelling  
**Sprache:** Englisch  
**Genre:** Pop Ballad  
**Schwierigkeit:** Hard

```text
Write a song where each section moves the story forward.

Story:
A man lost the woman he loved because he never told her the truth. Years later, he still wonders if she felt the same.

Structure:
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Bridge]
[Final Chorus]

Requirements:
- Verse 1 sets the situation
- Verse 2 adds new information
- Bridge reveals the deepest regret
- Chorus stays memorable
- no repeated empty phrases
- lyrics only
```

Checks:

```python
["storytelling", "progression", "verse2_new_info", "bridge_reveal", "chorus"]
```

---

## `songwriting_story_greek_lost_chance`

**Kategorie:** Storytelling  
**Sprache:** Griechisch  
**Genre:** Greek Ballad  
**Schwierigkeit:** Hard

```text
Γράψε ένα ελληνικό τραγούδι όπου κάθε μέρος προχωράει την ιστορία.

Ιστορία:
Ένας άντρας έχασε τη γυναίκα που αγαπούσε επειδή δεν της είπε ποτέ την αλήθεια. Μετά από χρόνια αναρωτιέται αν ένιωσε κι εκείνη το ίδιο.

Δομή:
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Bridge]
[Final Chorus]

Απαιτήσεις:
- μόνο ελληνικοί στίχοι
- κάθε μέρος να έχει λόγο ύπαρξης
- όχι άδειες επαναλήψεις
- το ρεφρέν να είναι δυνατό
- η bridge να φέρνει συναισθηματική αποκάλυψη
- χωρίς εξηγήσεις
```

Checks:

```python
["greek", "storytelling", "progression", "bridge_reveal", "strong_chorus", "no_empty_repetition"]
```

---

# 10. Emotion Tests

## `songwriting_emotion_regret_only`

**Kategorie:** Emotion  
**Sprache:** Englisch  
**Genre:** Ballad  
**Schwierigkeit:** Medium

```text
Write a song section where the only main emotion is regret.

Theme:
I had the chance to love her, but I stayed silent.

Requirements:
- 8 lines maximum
- do not mix in anger or revenge
- clear emotional focus
- simple language
- lyrics only
```

Checks:

```python
["emotion", "regret", "focus", "simple_language", "no_anger", "no_revenge"]
```

---

## `songwriting_emotion_euphoric_edm`

**Kategorie:** Emotion  
**Sprache:** Englisch  
**Genre:** EDM  
**Schwierigkeit:** Medium

```text
Write an EDM chorus and drop chant about finally feeling alive again.

Requirements:
- euphoric emotion only
- short repeatable lines
- include [Chorus] and [Drop]
- strong crowd-singalong feeling
- no sad lyrics
- lyrics only
```

Checks:

```python
["emotion", "euphoria", "edm", "drop", "repetition", "singalong"]
```

---

# 11. Genre Tests

## `songwriting_genre_greek_laiko`

**Kategorie:** Genre  
**Sprache:** Griechisch  
**Genre:** Laiko / Laiko-Pop  
**Schwierigkeit:** Hard

```text
Write a Greek laiko-pop chorus about regret and lost love.

Requirements:
- Greek lyrics only
- emotional but not cheesy
- strong chorus hook
- natural Greek everyday language
- clean rhymes where possible
- suitable for a modern laiko-pop song
- no explanations
```

Checks:

```python
["greek", "laiko", "genre", "hook", "natural_language", "not_cheesy"]
```

---

## `songwriting_genre_deutschrap`

**Kategorie:** Genre  
**Sprache:** Deutsch  
**Genre:** Deutschrap / Pop-Rap  
**Schwierigkeit:** Medium

```text
Schreibe eine Deutschrap-Hook über jemanden, der nach außen kalt wirkt, aber innerlich noch liebt.

Anforderungen:
- nur deutscher Text
- moderner Sprachstil
- Hook muss eingängig sein
- keine Gewaltverherrlichung
- keine Beleidigungen
- keine Erklärung
```

Checks:

```python
["german", "rap", "hook", "modern_language", "safe_content", "catchy"]
```

---

## `songwriting_genre_frenchcore`

**Kategorie:** Genre  
**Sprache:** Englisch  
**Genre:** Frenchcore / Hardcore  
**Schwierigkeit:** Medium

```text
Write short vocal lines for a Frenchcore track.

Theme:
Breaking free after emotional pain.

Requirements:
- aggressive energy but no hate speech
- short shoutable lines
- include [Build-Up] and [Drop]
- suitable for high BPM electronic music
- no long verses
- lyrics only
```

Checks:

```python
["frenchcore", "high_bpm", "drop", "short_lines", "energy", "safe_content"]
```

---

## `songwriting_genre_kpop`

**Kategorie:** Genre  
**Sprache:** Englisch/Koreanisch gemischt  
**Genre:** K-Pop  
**Schwierigkeit:** Hard

```text
Write a K-pop chorus with a memorable English hook and short Korean phrases.

Theme:
A confident comeback after heartbreak.

Requirements:
- mix mostly English with short Korean phrases
- catchy repeated hook
- bright pop energy
- no full translation
- no explanations
- chorus only
```

Checks:

```python
["kpop", "hook", "english", "korean_phrase", "repetition", "confidence"]
```

---

## `songwriting_genre_reggaeton`

**Kategorie:** Genre  
**Sprache:** Spanisch  
**Genre:** Reggaeton Pop  
**Schwierigkeit:** Medium

```text
Write a Spanish reggaeton-pop chorus about wanting to dance with someone one last time.

Requirements:
- Spanish lyrics only
- catchy rhythm
- short lines
- repeatable hook
- romantic but not explicit
- no explanations
```

Checks:

```python
["spanish", "reggaeton", "hook", "rhythm", "romantic", "safe_content"]
```

---

# 12. Suno / AI-Music Format Tests

## `songwriting_suno_greek_pop_format`

**Kategorie:** Suno Format  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Hard

```text
Write a Suno-ready Greek pop song.

Requirements:
- Greek lyrics only
- include section tags
- include short music direction tags where useful
- no explanations
- no translations
- chorus must be hook-first
- radio-ready structure

Use this structure:
[Instrumental Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Pre-Chorus]
[Chorus]
[Bridge]
[Final Chorus]
[Outro]
```

Checks:

```python
["suno", "section_tags", "greek", "hook_first", "radio_structure", "no_explanation"]
```

---

## `songwriting_suno_edm_drop_format`

**Kategorie:** Suno Format  
**Sprache:** Englisch  
**Genre:** EDM / Dance Pop  
**Schwierigkeit:** Medium

```text
Write a Suno-ready EDM song section.

Theme:
Letting go of the past and dancing through the night.

Requirements:
- include [Intro], [Build-Up], [Chorus], [Drop], [Breakdown], [Final Drop]
- short vocal phrases
- strong drop chant
- no explanations
- no production essay
- lyrics and section tags only
```

Checks:

```python
["suno", "edm", "drop", "section_tags", "short_phrases", "no_explanation"]
```

---

# 13. Rewrite and Improvement Tests

## `songwriting_rewrite_bad_chorus`

**Kategorie:** Rewrite  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Hard

```text
Improve this weak chorus without changing the meaning.

Original:
I miss you every day
I do not know what to say
My heart is very sad
Because things went bad

Requirements:
- stronger hook
- better rhymes
- more natural wording
- easier to sing
- keep the same emotion
- return only the improved chorus
```

Checks:

```python
["rewrite", "hook", "rhyme", "natural_language", "meaning_preserved", "singable"]
```

---

## `songwriting_rewrite_greek_naturalize`

**Kategorie:** Rewrite  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Hard

```text
Βελτίωσε αυτό το ελληνικό ρεφρέν ώστε να ακούγεται πιο φυσικό και πιο δυνατό.

Αρχικό:
Σε σκέφτομαι κάθε νύχτα πολύ
Η καρδιά μου πονάει γιατί είσαι εσύ
Δεν ξέρω τι να κάνω πια
Μου λείπεις μέσα στην καρδιά

Απαιτήσεις:
- κράτα το ίδιο νόημα
- πιο φυσικά ελληνικά
- καλύτερες ρίμες
- πιο δυνατό hook
- να τραγουδιέται εύκολα
- δώσε μόνο το βελτιωμένο ρεφρέν
```

Checks:

```python
["rewrite", "greek", "natural_language", "rhyme", "hook", "meaning_preserved"]
```

---

## `songwriting_rewrite_meter_fix`

**Kategorie:** Rewrite  
**Sprache:** Deutsch  
**Genre:** Pop  
**Schwierigkeit:** Hard

```text
Verbessere diesen Text auf Singbarkeit und Metrik.

Original:
Ich habe so viele Gedanken in meinem Kopf und kann sie nicht sortieren
Jede Nacht liege ich wach und frage mich, warum wir uns verlieren

Anforderungen:
- Bedeutung behalten
- kürzere Zeilen
- besserer Rhythmus
- singbarer
- keine Erklärung
- nur die verbesserte Version ausgeben
```

Checks:

```python
["rewrite", "meter", "german", "short_lines", "singable", "meaning_preserved"]
```

---

# 14. Originality / Anti-Copy Tests

## `songwriting_original_greek_summer`

**Kategorie:** Originality  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Medium

```text
Write an original Greek pop chorus with a nostalgic summer feeling.

Requirements:
- Greek lyrics only
- do not imitate any existing artist or song
- use common genre conventions but create original lyrics
- no famous phrases
- no translation
- no explanations
```

Checks:

```python
["originality", "greek", "summer", "no_imitation", "no_famous_phrases", "chorus"]
```

---

## `songwriting_original_pop_no_cliche`

**Kategorie:** Originality  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Hard

```text
Write an original pop chorus about missing someone.

Requirements:
- avoid obvious clichés like "broken heart", "tears", "darkness", "rain"
- simple but fresh wording
- strong hook
- easy to sing
- no explanations
```

Checks:

```python
["originality", "no_cliche", "hook", "fresh_wording", "singable"]
```

---

# 15. Title and Concept Tests

## `songwriting_titles_greek_ballad`

**Kategorie:** Title Generation  
**Sprache:** Griechisch  
**Genre:** Greek Ballad  
**Schwierigkeit:** Easy

```text
Generate 20 strong Greek song titles for a ballad about missed love.

Requirements:
- Greek titles only
- short titles
- emotional but not generic
- suitable for a chorus hook
- no explanations
```

Checks:

```python
["titles", "greek", "short", "emotional", "not_generic", "hook_ready"]
```

---

## `songwriting_concept_album_singles`

**Kategorie:** Concept  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Create 10 original song concepts for a pop artist.

Requirements:
- each concept needs title, main emotion, one-sentence story, and chorus hook idea
- no generic love song ideas
- no artist imitation
- keep each concept short
```

Checks:

```python
["concept", "title", "emotion", "story", "hook_idea", "originality"]
```

---

# 16. Multilingual Songwriting Tests

## `songwriting_language_german_pop`

**Kategorie:** Language  
**Sprache:** Deutsch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Schreibe einen deutschen Pop-Refrain über jemanden, der eine Person nicht vergessen kann.

Anforderungen:
- nur deutscher Text
- natürlich und modern
- keine steife Übersetzungssprache
- klare Hook
- 4 bis 6 Zeilen
- keine Erklärung
```

Checks:

```python
["german", "natural_language", "modern", "hook", "chorus", "no_translation_style"]
```

---

## `songwriting_language_english_pop`

**Kategorie:** Language  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Easy

```text
Write an English pop chorus about someone who still feels close even after leaving.

Requirements:
- natural English
- simple words
- strong hook
- 4 to 6 lines
- easy to sing
- no explanations
```

Checks:

```python
["english", "natural_language", "hook", "simple_words", "singable"]
```

---

## `songwriting_language_greek_pop`

**Kategorie:** Language  
**Sprache:** Griechisch  
**Genre:** Greek Pop  
**Schwierigkeit:** Hard

```text
Γράψε ένα ελληνικό pop ρεφρέν για κάποιον που έχασε την ευκαιρία να πει όσα ένιωθε.

Απαιτήσεις:
- μόνο ελληνικά
- φυσική καθημερινή γλώσσα
- όχι γερμανική δομή πρότασης
- καθαρό hook
- 4 έως 6 γραμμές
- χωρίς εξηγήσεις
```

Checks:

```python
["greek", "natural_language", "no_german_structure", "hook", "chorus", "singable"]
```

---

## `songwriting_language_spanish_reggaeton`

**Kategorie:** Language  
**Sprache:** Spanisch  
**Genre:** Reggaeton Pop  
**Schwierigkeit:** Medium

```text
Escribe un coro de reggaetón pop sobre una última noche bailando con alguien que todavía amas.

Requisitos:
- solo letra en español
- lenguaje natural
- hook repetible
- líneas cortas
- romántico pero no explícito
- sin explicación
```

Checks:

```python
["spanish", "natural_language", "reggaeton", "hook", "short_lines", "safe_content"]
```

---

## `songwriting_language_french_pop`

**Kategorie:** Language  
**Sprache:** Französisch  
**Genre:** French Pop  
**Schwierigkeit:** Medium

```text
Écris un refrain pop français sur le regret d'avoir laissé partir quelqu'un.

Exigences:
- paroles en français uniquement
- langage naturel
- 4 à 6 lignes
- refrain mémorable
- pas de traduction
- pas d'explication
```

Checks:

```python
["french", "natural_language", "chorus", "hook", "regret", "no_translation"]
```

---

## `songwriting_language_polish_pop`

**Kategorie:** Language  
**Sprache:** Polnisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Napisz polski refren pop o kimś, kto wciąż czeka na wiadomość od dawnej miłości.

Wymagania:
- tylko tekst po polsku
- naturalny język
- 4 do 6 wersów
- mocny hook
- proste emocje
- bez wyjaśnień
```

Checks:

```python
["polish", "natural_language", "hook", "chorus", "simple_emotion"]
```

---

## `songwriting_language_turkish_pop`

**Kategorie:** Language  
**Sprache:** Türkisch  
**Genre:** Turkish Pop  
**Schwierigkeit:** Medium

```text
Eski bir aşkı unutamayan biri hakkında Türkçe pop nakaratı yaz.

Gereksinimler:
- sadece Türkçe şarkı sözü
- doğal günlük dil
- 4 ila 6 kısa satır
- güçlü hook
- açıklama yok
```

Checks:

```python
["turkish", "natural_language", "hook", "chorus", "short_lines"]
```

---

## `songwriting_language_albanian_pop`

**Kategorie:** Language  
**Sprache:** Albanisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Shkruaj një refren pop në shqip për dikë që ende mendon për dashurinë e humbur.

Kërkesa:
- vetëm tekst në shqip
- gjuhë natyrale
- 4 deri në 6 rreshta
- hook i fortë
- pa shpjegime
```

Checks:

```python
["albanian", "natural_language", "hook", "chorus", "short_lines"]
```

---

## `songwriting_language_dutch_pop`

**Kategorie:** Language  
**Sprache:** Niederländisch  
**Genre:** Pop  
**Schwierigkeit:** Medium

```text
Schrijf een Nederlands poprefrein over iemand die een verloren liefde niet kan vergeten.

Vereisten:
- alleen Nederlandse songtekst
- natuurlijke taal
- 4 tot 6 regels
- sterke hook
- geen uitleg
```

Checks:

```python
["dutch", "natural_language", "hook", "chorus", "short_lines"]
```

---

## `songwriting_language_korean_kpop`

**Kategorie:** Language  
**Sprache:** Koreanisch/Englisch  
**Genre:** K-Pop  
**Schwierigkeit:** Hard

```text
Write a K-pop chorus using mostly Korean with one short English hook phrase.

Theme:
Coming back stronger after heartbreak.

Requirements:
- mostly Korean lyrics
- one repeatable English hook phrase
- catchy pop rhythm
- confident emotion
- no translation
- no explanations
```

Checks:

```python
["korean", "english_hook", "kpop", "confidence", "chorus", "no_translation"]
```

---

# 17. Suno Style Prompt Tests

## `songwriting_suno_style_prompt_greek_pop`

**Kategorie:** Suno Style Prompt  
**Sprache:** Englisch für Style Prompt  
**Genre:** Greek Pop  
**Schwierigkeit:** Medium

```text
Create a short Suno style prompt for a Greek pop/laiko song.

Song mood:
Emotional, nostalgic, romantic, modern radio sound.

Requirements:
- one compact style prompt only
- include genre, mood, vocal style, tempo feel, and instruments
- no lyrics
- no explanations
- maximum 35 words
```

Checks:

```python
["suno_style", "genre", "mood", "vocal_style", "instruments", "short"]
```

---

## `songwriting_suno_style_prompt_edm`

**Kategorie:** Suno Style Prompt  
**Sprache:** Englisch  
**Genre:** EDM  
**Schwierigkeit:** Medium

```text
Create a short Suno style prompt for an emotional EDM dance song.

Requirements:
- one compact prompt only
- include BPM feel, synths, drums, vocal mood, and drop energy
- no lyrics
- no explanations
- maximum 35 words
```

Checks:

```python
["suno_style", "edm", "bpm_feel", "drop", "vocal_mood", "short"]
```

---

# 18. Advanced Tests

## `songwriting_advanced_same_theme_three_genres`

**Kategorie:** Advanced  
**Sprache:** Englisch  
**Genre:** Multi-Genre  
**Schwierigkeit:** Hard

```text
Write three chorus versions for the same theme in three different genres.

Theme:
I still love you, but I will not beg anymore.

Genres:
1. Pop Ballad
2. Pop-Rap
3. EDM

Requirements:
- each chorus must match its genre
- each chorus must have 4 lines
- keep the same core emotion
- make each version clearly different
- no explanations
```

Checks:

```python
["multi_genre", "chorus", "genre_control", "same_emotion", "variation"]
```

---

## `songwriting_advanced_hook_variations`

**Kategorie:** Advanced  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Hard

```text
Generate 12 hook lines for a pop song.

Theme:
Someone's name is enough to bring all memories back.

Requirements:
- each hook must be one line
- hooks must be singable
- avoid generic phrases
- no explanations
- number the hooks 1 to 12
```

Checks:

```python
["hook_generation", "singable", "variation", "no_generic", "numbered"]
```

---

## `songwriting_advanced_section_consistency`

**Kategorie:** Advanced  
**Sprache:** Englisch  
**Genre:** Pop  
**Schwierigkeit:** Hard

```text
Write Verse 1, Pre-Chorus, and Chorus for a pop song.

Theme:
A person hears one name and all memories return.

Requirements:
- all sections must belong to the same song
- verse must set the scene
- pre-chorus must build tension
- chorus must release the main emotion
- no repeated filler
- lyrics only
```

Checks:

```python
["section_consistency", "verse", "pre_chorus", "chorus", "emotional_arc", "no_filler"]
```

---

# 19. Recommended Minimal Benchmark Set

Wenn du schnell prüfen willst, ob ein Modell Songwriting wirklich kann, nutze diese 12 Prompts:

```text
songwriting_hook_pop_chorus
songwriting_hook_greek_pop_chorus
songwriting_full_greek_pop_suno
songwriting_rhyme_greek_natural
songwriting_meter_128bpm_dance_pop
songwriting_story_progression
songwriting_emotion_regret_only
songwriting_genre_greek_laiko
songwriting_suno_greek_pop_format
songwriting_rewrite_bad_chorus
songwriting_rewrite_greek_naturalize
songwriting_original_pop_no_cliche
```

---

# 20. Suggested Prompt Metadata List

Diese Liste kann direkt als Grundlage für `PROMPTS` in Python genutzt werden:

```python
SONGWRITING_PROMPT_KEYS = [
    "songwriting_hook_pop_chorus",
    "songwriting_hook_greek_pop_chorus",
    "songwriting_hook_german_schlager",
    "songwriting_chorus_emotional_release",
    "songwriting_chorus_final_line",
    "songwriting_verse_story_setup",
    "songwriting_verse_greek_story",
    "songwriting_prechorus_tension_build",
    "songwriting_prechorus_greek_build",
    "songwriting_bridge_emotional_turn",
    "songwriting_bridge_german_regret",
    "songwriting_full_pop_structure",
    "songwriting_full_greek_pop_suno",
    "songwriting_full_german_pop_rap",
    "songwriting_rhyme_clean_end_rhymes",
    "songwriting_rhyme_greek_natural",
    "songwriting_rhyme_repair",
    "songwriting_meter_128bpm_dance_pop",
    "songwriting_meter_greek_singable",
    "songwriting_story_progression",
    "songwriting_story_greek_lost_chance",
    "songwriting_emotion_regret_only",
    "songwriting_emotion_euphoric_edm",
    "songwriting_genre_greek_laiko",
    "songwriting_genre_deutschrap",
    "songwriting_genre_frenchcore",
    "songwriting_genre_kpop",
    "songwriting_genre_reggaeton",
    "songwriting_suno_greek_pop_format",
    "songwriting_suno_edm_drop_format",
    "songwriting_rewrite_bad_chorus",
    "songwriting_rewrite_greek_naturalize",
    "songwriting_rewrite_meter_fix",
    "songwriting_original_greek_summer",
    "songwriting_original_pop_no_cliche",
    "songwriting_titles_greek_ballad",
    "songwriting_concept_album_singles",
    "songwriting_language_german_pop",
    "songwriting_language_english_pop",
    "songwriting_language_greek_pop",
    "songwriting_language_spanish_reggaeton",
    "songwriting_language_french_pop",
    "songwriting_language_polish_pop",
    "songwriting_language_turkish_pop",
    "songwriting_language_albanian_pop",
    "songwriting_language_dutch_pop",
    "songwriting_language_korean_kpop",
    "songwriting_suno_style_prompt_greek_pop",
    "songwriting_suno_style_prompt_edm",
    "songwriting_advanced_same_theme_three_genres",
    "songwriting_advanced_hook_variations",
    "songwriting_advanced_section_consistency",
]
```

---

# 21. Acceptance Criteria

Die Songwriting-Benchmark-Erweiterung gilt als fertig, wenn:

- alle Prompt-Keys stabil vorhanden sind
- Prompts im UI unter `Songwriting Tests` gruppiert werden
- jeder Prompt Metadaten besitzt: `category`, `sub_category`, `language`, `genre`, `difficulty`, `checks`
- Ergebnisse pro Prompt gespeichert werden
- Ranking Songwriting-Badges anzeigen kann
- alte Benchmarks ohne Songwriting-Daten nicht crashen
- die Bewertung Hook, Reim, Metrik, Struktur, Emotion, Genre, Suno-Format und Originalität getrennt ausgeben kann
- Suno-Prompts keine Erklärungen oder Übersetzungen ausgeben sollen
- griechische Tests explizit auf natürliche Sprache und keine deutsche Satzstruktur prüfen

---

# 22. Optionaler späterer Ausbau

Später kann eine feinere Songwriting-Auswertung ergänzt werden:

```text
hook_score
rhyme_score
meter_score
structure_score
emotion_score
genre_score
language_naturalness_score
suno_format_score
originality_score
rewrite_score
```

Empfohlene Gesamtformel:

```python
songwriting_score = (
    hook_score * 0.20
    + singability_score * 0.15
    + structure_score * 0.15
    + emotion_score * 0.15
    + rhyme_score * 0.10
    + genre_score * 0.10
    + language_naturalness_score * 0.10
    + originality_score * 0.05
)
```

