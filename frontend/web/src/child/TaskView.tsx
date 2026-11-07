import { useEffect } from "react";
import type { AnswerResult, Task } from "../api/client";
import { Figure } from "../representations/Figure";
import { speak } from "../speech";
import { Keypad } from "./Keypad";

type Props = {
  task: Task;
  value: string;
  onChange: (value: string) => void;
  onSubmit: (answer: number | string) => void;
  result: AnswerResult | null;
  busy: boolean;
};

/** Trennt die Frage ("Welche Zahl fehlt?") von der Rechnung ("2, 3, 4, _"). */
function split(prompt: string): { question: string; figure: string } {
  const q = prompt.indexOf("? ");
  if (q >= 0) return { question: prompt.slice(0, q + 1), figure: prompt.slice(q + 2) };
  const c = prompt.indexOf(": ");
  if (c >= 0) return { question: prompt.slice(0, c + 1), figure: prompt.slice(c + 2) };
  if (prompt.includes("_") || prompt.endsWith("= ?")) return { question: "", figure: prompt };
  return { question: prompt, figure: "" };
}

/** Zerlegt die Rechnung an der Lücke, damit die Eingabe mitten in der Zeile steht. */
function aroundGap(figure: string): [string, string] | null {
  const i = figure.indexOf("_");
  if (i >= 0) return [figure.slice(0, i), figure.slice(i + 1)];
  if (figure.endsWith("= ?")) return [figure.slice(0, -1), ""];
  return null;
}

export function TaskView({ task, value, onChange, onSubmit, result, busy }: Props) {
  const choice = task.options !== null;
  const { question, figure } = split(task.prompt);
  const gap = aroundGap(figure);
  const shown = result ? String(result.answer) : value;
  // Lange Rechnungen ("1 Zehner und 4 Einer") und lange Antworten ("Wie viele Kinder sind es jetzt?") kleiner.
  const longFigure = figure.length > 14;
  const stacked = choice && task.options!.some((option) => String(option).length > 12);

  useEffect(() => {
    if (choice || result || busy) return;
    const onKey = (e: KeyboardEvent) => {
      if (/^[0-9]$/.test(e.key) && value.length < 2) onChange(value + e.key);
      else if (e.key === "Backspace") onChange(value.slice(0, -1));
      else if (e.key === "Enter" && value) onSubmit(Number(value));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [choice, result, busy, value, onChange, onSubmit]);

  const gapBox = (
    <span className={`gap${shown ? "" : " blank"}`} aria-label="Lücke">
      {shown}
    </span>
  );

  return (
    <>
      <main className="heft-main">
        {question && (
          <p className={`question${question.length > 40 ? " long" : ""}`}>
            <button
              type="button"
              className="speak"
              onClick={() => speak(task.prompt)}
              aria-label="Vorlesen"
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M4 9v6h4l5 4V5L8 9H4z" fill="currentColor" />
                <path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11" />
              </svg>
            </button>
            <span>{question}</span>
          </p>
        )}
        {figure && (
          <div className={`figure${longFigure ? " long" : ""}`}>
            {gap ? (
              <>
                <span>{gap[0]}</span>
                {gapBox}
                <span>{gap[1]}</span>
              </>
            ) : (
              <span>{figure}</span>
            )}
          </div>
        )}
        <Figure task={task} revealed={result !== null} />
        {!figure && !choice && <div className="figure">{gapBox}</div>}
      </main>
      <footer className="heft-bottom">
        {result === null && choice && (
          <div className={`options${stacked ? " stacked" : ""}`}>
            {task.options!.map((option) => (
              <button
                key={String(option)}
                type="button"
                className="option"
                onClick={() => onSubmit(option)}
                disabled={busy}
              >
                {option}
              </button>
            ))}
          </div>
        )}
        {result === null && !choice && (
          <Keypad
            value={value}
            onChange={onChange}
            onSubmit={() => onSubmit(Number(value))}
            disabled={busy}
          />
        )}
      </footer>
    </>
  );
}
