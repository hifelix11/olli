import type { Counters } from "./counters";

type Slot = "red" | "blue" | "removed" | "empty" | "none";

/** Zwei Reihen à zehn, mit Lücke nach fünf (Kraft der Fünf). Wird die Antwort geprüft, füllen sich die leeren Plättchen. */
export function TwentyField({ counters, revealed }: { counters: Counters; revealed: boolean }) {
  const slots: Slot[] = [];
  const push = (slot: Slot, n: number) => {
    for (let i = 0; i < n; i++) slots.push(slot);
  };
  push("red", counters.red);
  push("blue", counters.blue);
  push("removed", counters.removed);
  push(revealed ? "blue" : "empty", counters.empty);
  while (slots.length < 20) slots.push("none");

  const label = `${counters.red} rote und ${counters.blue} blaue Plättchen`;
  return (
    <div className="twenty-field" role="img" aria-label={label}>
      {[0, 10].map((start) => (
        <div className="twenty-row" key={start}>
          {slots.slice(start, start + 10).map((slot, i) => (
            <span key={i} className={`counter counter-${slot}${i === 5 ? " counter-gap" : ""}`} />
          ))}
        </div>
      ))}
    </div>
  );
}
