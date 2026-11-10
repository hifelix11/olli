import type { Task } from "../api/client";

/**
 * Plättchen für das Zwanzigerfeld: rot, blau, weggenommen, noch leer.
 * Gelegt wird zeilenweise, die obere Reihe zuerst. `pairs` legt spaltenweise, oben und unten
 * (gerade, ungerade). `mirror` legt die roten oben und den Rest unten (verdoppeln, halbieren).
 */
export type Counters = {
  red: number;
  blue: number;
  removed: number;
  empty: number;
  layout?: "pairs" | "mirror";
};

const none: Counters = { red: 0, blue: 0, removed: 0, empty: 0 };
const num = (task: Task, key: string) => Number(task.operands[key]);

/** null, wenn die Aufgabenart kein Zwanzigerfeld hat. Ob es gezeigt wird, entscheidet Figure. */
export function countersFor(task: Task): Counters | null {
  switch (task.kind) {
    case "count":
      return { ...none, red: num(task, "n") };
    case "addition":
      return { ...none, red: num(task, "a"), blue: num(task, "b") };
    case "subtraction":
      return { ...none, red: num(task, "a") - num(task, "b"), removed: num(task, "b") };
    case "missing_number":
      if (task.operands.form !== "a+_=c") return null;
      return { ...none, red: num(task, "a"), empty: num(task, "c") - num(task, "a") };
    case "double_half": {
      const value = num(task, "value");
      return task.operands.mode === "double"
        ? { ...none, red: value, empty: value, layout: "mirror" }
        : { ...none, red: value / 2, blue: value / 2, layout: "mirror" };
    }
    case "even_odd":
      return { ...none, red: num(task, "n"), layout: "pairs" };
    case "picture_equation":
      if (task.operands.op === "+") return { ...none, red: num(task, "a"), blue: num(task, "b") };
      return { ...none, red: num(task, "a") - num(task, "b"), removed: num(task, "b") };
    case "switch_representation":
      if (task.operands.form !== "twenty_field") return null;
      return { ...none, red: num(task, "n") };
    default:
      return null;
  }
}
