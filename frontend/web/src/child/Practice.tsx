import { useCallback, useEffect, useRef, useState } from "react";
import { api, labelOf, type AnswerResult, type Child, type Task } from "../api/client";
import { chime } from "../sound";
import { speak } from "../speech";
import { Icon } from "./Icon";
import { Olli, type Mood } from "./Olli";
import { Stamp } from "./Stamp";
import { TaskView } from "./TaskView";

const SESSION_LENGTH = 10;
const NEXT_AFTER_RIGHT = 1100;
const NEXT_AFTER_PLACEMENT = 1400;

/** Olli spricht in der ersten Person. Den Namen des Kindes spricht Olli nie aus. */
const GREETING = {
  placement: [
    "Ich will sehen, was du schon kannst.",
    "Manches ist noch schwer. Das ist okay.",
    "Weißt du etwas nicht? Dann tipp auf das Fragezeichen.",
  ],
  practice: ["Heute üben wir zusammen.", "Nach zehn Aufgaben bekommst du einen Stempel."],
};
const PLACEMENT_OVER = "Jetzt weiß ich, was du kannst. Ab jetzt üben wir.";
const STEP_BACK = "Wir üben erst etwas, das dir dabei hilft.";

type Phase =
  | { kind: "loading" }
  | { kind: "welcome"; task: Task }
  | { kind: "task"; task: Task; retry: boolean }
  | { kind: "result"; task: Task; result: AnswerResult }
  | { kind: "done"; everything: boolean }
  | { kind: "error"; message: string };

export function Practice({ child, onExit }: { child: Child; onExit: () => void }) {
  const [phase, setPhase] = useState<Phase>({ kind: "loading" });
  const [value, setValue] = useState("");
  const [line, setLine] = useState("");
  const [answered, setAnswered] = useState(0);
  const [learned, setLearned] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const intro = useRef<string | null>(null); // sagt Olli vor der nächsten Aufgabe
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);

  const say = useCallback((text: string) => {
    setLine(text);
    speak(text);
  }, []);

  /** Zeigt die Aufgabe und liest sie vor, mit Ollis Satz davor, falls einer wartet. */
  const show = useCallback((task: Task) => {
    const before = intro.current;
    intro.current = null;
    setValue("");
    setLine(before ?? "");
    setPhase({ kind: "task", task, retry: false });
    speak(before ? `${before} ${task.prompt}` : task.prompt);
  }, []);

  const load = useCallback(
    async (previous: Task | null) => {
      setPhase({ kind: "loading" });
      try {
        const task = await api.nextTask(child.id);
        if (!alive.current) return;
        if (!task) return setPhase({ kind: "done", everything: true });
        if (previous?.placement && !task.placement) intro.current = PLACEMENT_OVER;
        show(task);
      } catch (error) {
        if (alive.current) setPhase({ kind: "error", message: String(error) });
      }
    },
    [child.id, show],
  );

  // Die erste Aufgabe lädt hinter der Begrüßung.
  useEffect(() => {
    let cancelled = false;
    api
      .nextTask(child.id)
      .then((task) => {
        if (cancelled) return;
        setPhase(task ? { kind: "welcome", task } : { kind: "done", everything: true });
      })
      .catch((error: unknown) => {
        if (!cancelled) setPhase({ kind: "error", message: String(error) });
      });
    return () => {
      cancelled = true;
    };
  }, [child.id]);

  const placementFirst = phase.kind === "welcome" ? phase.task.placement : null;
  useEffect(() => {
    if (placementFirst === null) return;
    speak(["Hallo!", ...GREETING[placementFirst ? "placement" : "practice"]].join(" "));
  }, [placementFirst]);

  const submit = useCallback(
    async (answer: number | string | null) => {
      if (phase.kind !== "task" || busy) return;
      const { task } = phase;
      setBusy(true);
      try {
        const result = await api.answer(child.id, task.id, answer);
        if (!alive.current) return;
        if (result.backtracked_to) intro.current = STEP_BACK;
        if (result.retry) {
          setValue("");
          setPhase({ kind: "task", task, retry: true });
          say("Schau nochmal.");
          return;
        }
        setAnswered((n) => n + 1);
        if (result.mastered) setLearned((titles) => [...titles, task.title]);
        setPhase({ kind: "result", task, result });
        if (task.placement) say(answer === null ? "Das üben wir später." : "Gemerkt!");
        else if (result.correct) {
          chime();
          setLine("Richtig!");
        } else if (result.answer !== null) say(`Die Lösung ist ${labelOf(task, result.answer)}.`);
      } catch (error) {
        if (alive.current) setPhase({ kind: "error", message: String(error) });
      } finally {
        setBusy(false);
      }
    },
    [phase, busy, child.id, say],
  );

  const advance = useCallback(() => {
    if (phase.kind !== "result") return;
    if (answered >= SESSION_LENGTH) setPhase({ kind: "done", everything: false });
    else void load(phase.task);
  }, [phase, answered, load]);

  // Richtig und Standortcheck gehen von selbst weiter. Nach einem Fehler tippt das Kind auf den Pfeil.
  useEffect(() => {
    if (phase.kind !== "result") return;
    const delay = phase.task.placement
      ? NEXT_AFTER_PLACEMENT
      : phase.result.correct
        ? NEXT_AFTER_RIGHT
        : null;
    if (delay === null) return;
    const timer = setTimeout(advance, delay);
    return () => clearTimeout(timer);
  }, [phase, advance]);

  const everything = phase.kind === "done" ? phase.everything : null;
  const newTitles = [...new Set(learned)];
  const newTitlesKey = newTitles.join(", ");
  useEffect(() => {
    if (everything === null) return;
    const first = everything ? "Du kannst schon alles!" : "Fertig für heute! Hier ist dein Stempel.";
    speak(newTitlesKey ? `${first} Das kannst du jetzt neu: ${newTitlesKey}.` : first);
  }, [everything, newTitlesKey]);

  if (phase.kind === "error") {
    return (
      <div className="center-page">
        <Olli mood="thinking" size={120} />
        <h1>Ich erreiche den Server nicht.</h1>
        <p className="error">{phase.message}</p>
        <button type="button" className="btn btn-primary" onClick={() => void load(null)}>
          Nochmal versuchen
        </button>
        <HomeButton onExit={onExit} />
      </div>
    );
  }

  if (phase.kind === "welcome") {
    const lines = GREETING[phase.task.placement ? "placement" : "practice"];
    return (
      <div className="center-page welcome">
        <Olli size={140} />
        <h1>Hallo, {child.name}!</h1>
        <div>
          {lines.map((l) => (
            <p key={l}>{l}</p>
          ))}
        </div>
        <button
          type="button"
          className="play"
          onClick={() => show(phase.task)}
          aria-label="Los geht's"
        >
          <Icon name="play" size={52} />
        </button>
        <HomeButton onExit={onExit} />
      </div>
    );
  }

  if (phase.kind === "done") {
    return (
      <div className="center-page">
        <Stamp special={newTitles.length > 0} />
        <h1>{phase.everything ? "Du kannst schon alles!" : "Fertig für heute!"}</h1>
        {newTitles.length > 0 && (
          <ul className="learned">
            {newTitles.map((title) => (
              <li key={title}>Neu: {title}</li>
            ))}
          </ul>
        )}
        <button type="button" className="btn btn-primary btn-icon" onClick={onExit}>
          <Icon name="home" />
          Zum Start
        </button>
      </div>
    );
  }

  const task = phase.kind === "loading" ? null : phase.task;
  const result = phase.kind === "result" ? phase.result : null;
  const mood: Mood =
    phase.kind === "task" && phase.retry
      ? "thinking"
      : result && !task?.placement
        ? result.correct
          ? "happy"
          : "thinking"
        : "neutral";

  return (
    <div className="heft">
      <header className="heft-top">
        <div className="who">
          <Olli mood={mood} size={56} />
          {line && <p className="bubble">{line}</p>}
        </div>
        <div className="session" aria-label={`${answered} von ${SESSION_LENGTH} Aufgaben`}>
          {Array.from({ length: SESSION_LENGTH }, (_, i) => (
            <span key={i} className={i < answered ? "filled" : ""} />
          ))}
        </div>
        <HomeButton onExit={onExit} />
      </header>

      {task ? (
        <TaskView
          task={task}
          value={value}
          onChange={setValue}
          onSubmit={(answer) => void submit(answer)}
          closed={result !== null}
          solution={result?.answer != null && !task.placement ? labelOf(task, result.answer) : null}
          canSkip={task.placement}
          busy={busy}
          onNext={result && !task.placement && !result.correct ? advance : null}
        />
      ) : (
        <main className="heft-main" />
      )}
    </div>
  );
}

function HomeButton({ onExit }: { onExit: () => void }) {
  return (
    <button type="button" className="home" onClick={onExit} aria-label="Zum Start">
      <Icon name="home" />
    </button>
  );
}
