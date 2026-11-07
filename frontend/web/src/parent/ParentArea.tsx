import { useEffect, useState } from "react";
import { api, type Child, type MasteryRow, type MasteryStatus, type Progress } from "../api/client";
import { Keypad } from "../child/Keypad";

/** Platzhalter, bis es Elternkonten gibt. */
const PIN = "1234";

const AREAS: { key: string; title: string }[] = [
  { key: "numbers_operations", title: "Zahlen und Rechnen" },
  { key: "space_shape", title: "Formen und Raum" },
  { key: "quantities_measurement", title: "Größen und Messen" },
  { key: "data_chance", title: "Daten und Zufall" },
];

const STATUS: Record<MasteryStatus, string> = {
  mastered: "sitzt",
  in_progress: "in Arbeit",
  not_started: "kommt noch",
};

type Props = {
  kids: Child[];
  onAdd: (child: Child) => void;
  onExit: () => void;
};

export function ParentArea({ kids, onAdd, onExit }: Props) {
  const [pin, setPin] = useState("");
  const [open, setOpen] = useState(false);
  const [wrong, setWrong] = useState(false);
  const [selected, setSelected] = useState<Child | null>(kids[0] ?? null);
  const [name, setName] = useState("");
  const [rows, setRows] = useState<MasteryRow[] | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !selected) return;
    let cancelled = false;
    Promise.all([api.mastery(selected.id), api.progress(selected.id)])
      .then(([mastery, progress]) => {
        if (cancelled) return;
        setRows(mastery);
        setProgress(progress);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [open, selected]);

  const check = () => {
    if (pin === PIN) setOpen(true);
    else {
      setWrong(true);
      setPin("");
    }
  };

  const select = (child: Child) => {
    setSelected(child);
    setRows(null);
    setProgress(null);
  };

  const add = async () => {
    const trimmed = name.trim();
    if (!trimmed) return;
    try {
      const child = await api.createChild(trimmed);
      onAdd(child);
      select(child);
      setName("");
      setError(null);
    } catch (e) {
      setError(`Olli erreicht den Server nicht. ${String(e)}`);
    }
  };

  if (!open) {
    return (
      <div className="center-page">
        <h1>Elternbereich</h1>
        <p>Bitte PIN eingeben.</p>
        <div className="pin-dots" aria-label={`${pin.length} von 4 Ziffern`}>
          {[0, 1, 2, 3].map((i) => (
            <span key={i} className={i < pin.length ? "on" : ""} />
          ))}
        </div>
        {wrong && <p className="error">Die PIN stimmt nicht.</p>}
        <Keypad value={pin} onChange={setPin} onSubmit={check} maxLength={4} submitLabel="Öffnen" />
        <button type="button" className="btn btn-quiet" onClick={onExit}>
          Zurück zum Start
        </button>
      </div>
    );
  }

  return (
    <div className="parent">
      <header>
        <h1>Elternbereich</h1>
        <button type="button" className="btn btn-quiet" onClick={onExit}>
          Zurück zum Start
        </button>
      </header>
      <section>
        <h2>Kinder</h2>
        {kids.length > 0 && (
          <div className="tabs">
            {kids.map((child) => (
              <button
                key={child.id}
                type="button"
                className={`btn${child.id === selected?.id ? " btn-primary" : ""}`}
                onClick={() => select(child)}
              >
                {child.name}
              </button>
            ))}
          </div>
        )}
        <form
          className="add"
          onSubmit={(e) => {
            e.preventDefault();
            void add();
          }}
        >
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            aria-label="Name des Kindes"
            maxLength={30}
          />
          <button type="submit" className="btn btn-primary" disabled={!name.trim()}>
            Kind anlegen
          </button>
        </form>
      </section>
      {error && <p className="error">{error}</p>}
      {selected && rows && progress && (
        <>
          <h2>Lernstand von {selected.name}</h2>
          <section className="goal">
            <h3>Ziel bis Ende der Jahrgangsstufe {progress.grade}</h3>
            <div
              className="bar"
              role="img"
              aria-label={`${progress.mastered} von ${progress.checkable} Fähigkeiten sitzen`}
            >
              <b style={{ width: `${(100 * progress.mastered) / progress.checkable}%` }} />
            </div>
            <p className="summary">
              Zum Ziel gehören {progress.goal} Fähigkeiten, {progress.checkable} davon kann Olli
              prüfen. Davon sitzen {progress.mastered}, {progress.in_progress} sind in Arbeit.
              Quelle: {progress.curriculum}.
            </p>
            {!progress.placement_done && (
              <p className="summary">
                Olli schaut noch, was {selected.name} schon kann. Nach den ersten Aufgaben zeigt
                die Karte mehr.
              </p>
            )}
          </section>
          <h3>Karte</h3>
          <p className="summary">Blass gezeichnete Fähigkeiten kann Olli noch nicht üben.</p>
          <div className="legend">
            {(Object.keys(STATUS) as MasteryStatus[]).map((s) => (
              <span key={s}>
                <i className={s} />
                {STATUS[s]}
              </span>
            ))}
          </div>
          {AREAS.map((area) => (
            <section key={area.key}>
              <h3>{area.title}</h3>
              <div className="map">
                {rows
                  .filter((r) => r.area === area.key)
                  .map((r) => (
                    <div
                      key={r.competency}
                      className={`cell cell-${r.status}${r.practicable ? "" : " cell-later"}`}
                      title={
                        r.practicable
                          ? `${STATUS[r.status]}, ${Math.round(r.p_known * 100)} %`
                          : "Kann Olli noch nicht üben"
                      }
                    >
                      <span>{r.title}</span>
                      <i>
                        <b style={{ width: `${Math.round(r.p_known * 100)}%` }} />
                      </i>
                    </div>
                  ))}
              </div>
            </section>
          ))}
        </>
      )}
    </div>
  );
}
