/** Wer zuletzt vorlesen ließ. Bekommt null, sobald etwas anderes gesprochen wird. */
let previous: ((index: number | null) => void) | null = null;
let run = 0;

/**
 * Liest vor. Erstklässler lesen noch nicht flüssig.
 * Mehrere Teile kommen nacheinander, `onPart` meldet, welcher gerade dran ist, und null am Ende.
 */
export function speak(text: string | string[], onPart?: (index: number | null) => void): void {
  if (!("speechSynthesis" in window)) return;
  const parts = typeof text === "string" ? [text] : text;
  previous?.(null);
  previous = onPart ?? null;
  const current = ++run;
  const report = (index: number | null) => {
    if (current === run) onPart?.(index);
  };
  window.speechSynthesis.cancel();
  parts.forEach((part, i) => {
    const utterance = new SpeechSynthesisUtterance(spoken(part));
    utterance.lang = "de-DE";
    utterance.rate = 0.9;
    utterance.onstart = () => report(i);
    utterance.onerror = () => report(null);
    if (i === parts.length - 1) utterance.onend = () => report(null);
    window.speechSynthesis.speak(utterance);
  });
}

function spoken(text: string): string {
  return text
    .replace(/\+/g, " plus ")
    .replace(/−/g, " minus ")
    .replace(/=/g, " gleich ")
    .replace(/_/g, " wie viel ")
    .replace(/\?/g, "");
}

/** Wörter liest Olli vor. Zahlen, Rechnungen und Zeichen wie A oder < liest das Kind selbst. */
export function hasWords(text: string): boolean {
  return /\p{L}{2}/u.test(text);
}
