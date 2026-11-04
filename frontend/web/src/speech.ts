/** Liest den Aufgabentext vor. Erstklässler lesen noch nicht flüssig. */
export function speak(text: string): void {
  if (!("speechSynthesis" in window)) return;
  const spoken = text
    .replace(/\+/g, " plus ")
    .replace(/−/g, " minus ")
    .replace(/=/g, " gleich ")
    .replace(/_/g, " wie viel ")
    .replace(/\?/g, "");
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(spoken);
  utterance.lang = "de-DE";
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}
