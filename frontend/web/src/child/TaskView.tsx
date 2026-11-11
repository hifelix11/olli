import { useEffect } from "react";
import type { Task } from "../api/client";
import { Figure } from "../representations/Figure";
import { optionPicture } from "../representations/OptionPicture";
import { hasWords, speak } from "../speech";
import { Burst } from "./Burst";
import { Icon } from "./Icon";
import { Keypad } from "./Keypad";

type Props = {
  task: Task;
  /** Getippte Zahl oder gewählte Antwort. Zählt erst mit dem Haken. */
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
  /** Richtig: Formen fliegen aus der Tafel. */
  cheer: boolean;
  /** Zweiter Versuch: die Tafel wackelt einmal. */
  shake: boolean;
  /** Antwort, die Olli gerade vorliest. Sie leuchtet auf. */
  reading: number | null;
  /** Lautsprecher: Frage und Antworten noch einmal. */
  onRead: () => void;
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
  const { task, value, onChange, onSubmit, closed, solution, canSkip, busy, onNext, cheer, shake } =
    props;
  const { reading, onRead } = props;
  const choice = task.options !== null;
  const { question, figure } = split(task.prompt);
  const gap = aroundGap(figure);
  const shown = solution !== null ? String(solution) : value;
  // Lange Rechnungen ("1 Zehner und 4 Einer") und lange Antworten ("Wie viele Kinder sind es jetzt?") kleiner.
  const longFigure = figure.length > 14;
  // Bild und Wort, wenn jede Antwort ein Bild hat. Nicht beim Benennen: Das Bild auf der Tafel ist die Frage.
  const pictures =
    choice && task.kind !== "shape_name" ? task.options!.map((o) => optionPicture(String(o))) : [];
  const withPictures = pictures.length > 0 && pictures.every(Boolean);
  const stacked =
    choice && !withPictures && task.options!.some((option) => String(option).length > 12);
  // Wie beim Zahlenblock: erst wählen, dann mit dem Haken bestätigen.
  const answer = choice
    ? (task.options!.find((option) => String(option) === value) ?? null)
    : value
      ? Number(value)
      : null;

  /** Antippen wählt aus und sagt die Antwort. Das Kind kann noch wechseln. */
  const select = (option: number | string) => {
    const text = String(option);
    onChange(text);
    if (hasWords(text)) speak(text);
  };

  useEffect(() => {
    if (closed || busy) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Enter" && answer !== null) onSubmit(answer);
      else if (choice) return;
      else if (/^[0-9]$/.test(e.key) && value.length < 2) onChange(value + e.key);
      else if (e.key === "Backspace") onChange(value.slice(0, -1));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [choice, closed, busy, value, answer, onChange, onSubmit]);

  const gapBox = (
    <span className={`gap${shown ? "" : " blank"}`} aria-label="Lücke">
      {shown}
    </span>
  );

  return (
    <>
      <main className="stage-main">
        <div className={`board${shake ? " shake" : ""}`}>
          {question && (
            <p className={`question${question.length > 40 ? " long" : ""}`}>
              <button
                type="button"
                className="speak"
                onClick={onRead}
                aria-label="Vorlesen"
              >
                <Icon name="speaker" size={26} />
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
          {cheer && <Burst />}
        </div>
      </main>
      <footer className="stage-bottom">
        {!closed && choice && (
          <div className="choice">
            <div className={`options${stacked ? " stacked" : ""}`}>
              {task.options!.map((option, i) => (
                <button
                  key={String(option)}
                  type="button"
                  className={[
                    "option",
                    withPictures && "with-picture",
                    reading === i && "reading",
                    String(option) === value && "selected",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  onClick={() => select(option)}
                  aria-pressed={String(option) === value}
                  disabled={busy}
                >
                  {withPictures && <span className="option-picture">{pictures[i]}</span>}
                  <span>{option}</span>
                </button>
              ))}
            </div>
            <button
              type="button"
              className="next"
              onClick={() => answer !== null && onSubmit(answer)}
              disabled={busy || answer === null}
              aria-label="Fertig"
            >
              <Icon name="check" size={44} />
            </button>
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
            <Icon name="next" size={44} />
          </button>
        )}
      </footer>
    </>
  );
}
