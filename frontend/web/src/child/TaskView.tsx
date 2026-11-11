import { useEffect } from "react";
import type { Task } from "../api/client";
import { Figure } from "../representations/Figure";
import { speak } from "../speech";
import { Icon } from "./Icon";
import { Keypad } from "./Keypad";

type Props = {
  task: Task;
  value: string;
  onChange: (value: string) => void;
  /** null: "Weiß ich noch nicht". */
  onSubmit: (answer: number | string | null) => void;
  /** Beantwortet: keine Eingabe mehr. */
  closed: boolean;
  /** Steht in der Lücke und füllt die Plättchen. null: nichts verraten. */
  solution: number | string | null;
  /** Nur im Standortcheck. */
  canSkip: boolean;
  busy: boolean;
  /** Pfeil nach einer falschen Antwort. Sonst geht es von selbst weiter. */
  onNext: (() => void) | null;
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

export function TaskView(props: Props) {
  const { task, value, onChange, onSubmit, closed, solution, canSkip, busy, onNext } = props;
  const choice = task.options !== null;
  const { question, figure } = split(task.prompt);
  const gap = aroundGap(figure);
  const shown = solution !== null ? String(solution) : value;
  // Lange Rechnungen ("1 Zehner und 4 Einer") und lange Antworten ("Wie viele Kinder sind es jetzt?") kleiner.
  const longFigure = figure.length > 14;
  const stacked = choice && task.options!.some((option) => option.label.length > 12);

  useEffect(() => {
    if (choice || closed || busy) return;
    const onKey = (e: KeyboardEvent) => {
      if (/^[0-9]$/.test(e.key) && value.length < 2) onChange(value + e.key);
      else if (e.key === "Backspace") onChange(value.slice(0, -1));
      else if (e.key === "Enter" && value) onSubmit(Number(value));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [choice, closed, busy, value, onChange, onSubmit]);

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
              <Icon name="speaker" size={22} />
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
        <Figure task={task} revealed={solution !== null} />
        {!figure && !choice && <div className="figure">{gapBox}</div>}
      </main>
      <footer className="heft-bottom">
        {!closed && choice && (
          <div className={`options${stacked ? " stacked" : ""}`}>
            {task.options!.map((option) => (
              <button
                key={String(option.value)}
                type="button"
                className="option"
                onClick={() => onSubmit(option.value)}
                disabled={busy}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
        {!closed && !choice && (
          <Keypad
            value={value}
            onChange={onChange}
            onSubmit={() => onSubmit(Number(value))}
            disabled={busy}
          />
        )}
        {!closed && canSkip && (
          <button type="button" className="skip" onClick={() => onSubmit(null)} disabled={busy}>
            <span aria-hidden="true">?</span>
            Weiß ich noch nicht
          </button>
        )}
        {onNext && (
          <button type="button" className="next" onClick={onNext} aria-label="Weiter">
            <Icon name="next" size={40} />
          </button>
        )}
      </footer>
    </>
  );
}
