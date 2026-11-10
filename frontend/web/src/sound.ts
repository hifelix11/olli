/** Ton für richtige Antworten. Ohne Dateien, aus zwei Sinustönen. */

let context: AudioContext | null = null;

/**
 * Safari spielt Ton und Sprache erst, wenn ein Tippen sie startet.
 * Beim Tippen auf ein Kind aufrufen, danach geht beides auch ohne Tippen.
 */
export function unlockAudio(): void {
  try {
    context ??= new AudioContext();
    void context.resume();
    if ("speechSynthesis" in window) speechSynthesis.speak(new SpeechSynthesisUtterance(""));
  } catch {
    // Kein Ton ist kein Fehler.
  }
}

/** Kurzer Zweiklang, aufsteigend. */
export function chime(): void {
  if (!context) return;
  const start = context.currentTime;
  [660, 880].forEach((frequency, i) => {
    const t = start + i * 0.12;
    const tone = context!.createOscillator();
    const volume = context!.createGain();
    tone.frequency.value = frequency;
    volume.gain.setValueAtTime(0.0001, t);
    volume.gain.exponentialRampToValueAtTime(0.2, t + 0.02);
    volume.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
    tone.connect(volume).connect(context!.destination);
    tone.start(t);
    tone.stop(t + 0.4);
  });
}
