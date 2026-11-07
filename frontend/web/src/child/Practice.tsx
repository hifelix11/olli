import { useCallback, useEffect, useState } from "react";
import { api, type AnswerResult, type Child, type Task } from "../api/client";
import { Olli, type Mood } from "./Olli";
import { TaskView } from "./TaskView";

const SESSION_LENGTH = 10;

type Phase =
  | { kind: "loading" }
  | { kind: "task"; task: Task }
  | { kind: "result"; task: Task; result: AnswerResult }
  | { kind: "done"; everything: boolean }
  | { kind: "error"; message: string };

export function Practice({ child, onExit }: { child: Child; onExit: () => void }) {
  const [phase, setPhase] = useState<Phase>({ kind: "loading" });
  const [value, setValue] = useState("");
  const [answered, setAnswered] = useState(0);
  const [busy, setBusy] = useState(false);

  const [generation, setGeneration] = useState(0);

  // Jede Generation holt eine neue Aufgabe. Wer neu lädt, setzt vorher die Phase auf "loading".
  useEffect(() => {
    let cancelled = false;
    api
      .nextTask(child.id)
      .then((task) => {
        if (cancelled) return;
        setValue("");
        setPhase(task ? { kind: "task", task } : { kind: "done", everything: true });
      })
      .catch((error: unknown) => {
        if (!cancelled) setPhase({ kind: "error", message: String(error) });
      });
    return () => {
      cancelled = true;
    };
  }, [child.id, generation]);

  const reload = useCallback(() => {
    setPhase({ kind: "loading" });
    setGeneration((g) => g + 1);
  }, []);

  const submit = useCallback(
    async (answer: number | string) => {
      if (phase.kind !== "task" || busy) return;
      setBusy(true);
      try {
        const result = await api.answer(child.id, phase.task.id, answer);
        setAnswered((n) => n + 1);
        setPhase({ kind: "result", task: phase.task, result });
      } catch (error) {
        setPhase({ kind: "error", message: String(error) });
      } finally {
        setBusy(false);
      }
    },
    [phase, busy, child.id],
  );

  const advance = useCallback(() => {
    if (answered >= SESSION_LENGTH) setPhase({ kind: "done", everything: false });
    else reload();
  }, [answered, reload]);

  useEffect(() => {
    if (phase.kind !== "result" || !phase.result.correct) return;
    const timer = setTimeout(advance, 1100);
    return () => clearTimeout(timer);
  }, [phase, advance]);

  const mood: Mood =
    phase.kind === "result" ? (phase.result.correct ? "happy" : "thinking") : "neutral";

  if (phase.kind === "error") {
    return (
      <div className="center-page">
        <Olli mood="thinking" size={120} />
        <h1>Olli erreicht den Server nicht.</h1>
        <p className="error">{phase.message}</p>
        <button type="button" className="btn btn-primary" onClick={reload}>
          Nochmal versuchen
        </button>
        <button type="button" className="btn btn-quiet" onClick={onExit}>
          Zurück zum Start
        </button>
      </div>
    );
  }

  if (phase.kind === "done") {
    return (
      <div className="center-page">
        <Olli mood="happy" size={140} />
        <h1>{phase.everything ? "Du kannst schon alles!" : "Fertig für heute!"}</h1>
        {!phase.everything && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => {
              setAnswered(0);
              reload();
            }}
          >
            Noch eine Runde
          </button>
        )}
        <button type="button" className="btn btn-quiet" onClick={onExit}>
          Zurück zum Start
        </button>
      </div>
    );
  }

  const task = phase.kind === "loading" ? null : phase.task;
  const result = phase.kind === "result" ? phase.result : null;

  return (
    <div className="heft">
      <header className="heft-top">
        <div className="who">
          <Olli mood={mood} size={56} />
          <p className="who-text">
            {task?.placement
              ? `Olli schaut, was ${child.name} schon kann`
              : `Olli übt mit ${child.name}`}
            <b>{task?.title ?? "…"}</b>
          </p>
        </div>
        <div className="session" aria-label={`${answered} von ${SESSION_LENGTH} Aufgaben`}>
          {Array.from({ length: SESSION_LENGTH }, (_, i) => (
            <span key={i} className={i < answered ? "filled" : ""} />
          ))}
        </div>
        <button type="button" className="btn btn-quiet" onClick={onExit}>
          Zurück
        </button>
      </header>

      {task ? (
        <TaskView
          task={task}
          value={value}
          onChange={setValue}
          onSubmit={(answer) => void submit(answer)}
          result={result}
          busy={busy}
        />
      ) : (
        <main className="heft-main" />
      )}

      {result && (
        <footer className="heft-bottom">
          {result.correct ? (
            <div className="feedback right">Richtig!</div>
          ) : (
            <div className="feedback">
              <span>Die Lösung ist {result.answer}.</span>
              <button type="button" className="btn btn-primary" onClick={advance}>
                Weiter
              </button>
              {result.backtracked_to && (
                <span className="note">Olli sagt: Wir üben erst etwas Leichteres.</span>
              )}
              {task?.placement && <span className="note">Olli sagt: Das üben wir später.</span>}
            </div>
          )}
        </footer>
      )}
    </div>
  );
}
