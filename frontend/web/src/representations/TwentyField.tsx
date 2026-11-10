import type { Counters } from "./counters";

type Slot = "red" | "blue" | "removed" | "empty" | "none";

/** Zwei Reihen à zehn, mit Lücke nach fünf (Kraft der Fünf). Wird die Antwort geprüft, füllen sich die leeren Plättchen. */
export function TwentyField({ counters, revealed }: { counters: Counters; revealed: boolean }) {
  const all: Slot[] = [];
  const push = (slot: Slot, n: number) => {
    for (let i = 0; i < n; i++) all.push(slot);
  };
  push("red", counters.red);
  push("blue", counters.blue);
  push("removed", counters.removed);
  push(revealed ? "blue" : "empty", counters.empty);

  const [top, bottom] =
    counters.layout === "pairs"
      ? [all.filter((_, i) => i % 2 === 0), all.filter((_, i) => i % 2 === 1)]
      : counters.layout === "mirror"
        ? [all.slice(0, counters.red), all.slice(counters.red)]
        : [all.slice(0, 10), all.slice(10)];
  const row = (slots: Slot[]) => [...slots, ...Array<Slot>(10 - slots.length).fill("none")];

  const label = `${counters.red} rote und ${counters.blue} blaue Plättchen`;
  return (
    <div className="twenty-field" role="img" aria-label={label}>
      {[top, bottom].map((slots, r) => (
        <div className="twenty-row" key={r}>
          {row(slots).map((slot, i) => (
            <span key={i} className={`counter counter-${slot}${i === 5 ? " counter-gap" : ""}`} />
          ))}
        </div>
      ))}
    </div>
  );
}
