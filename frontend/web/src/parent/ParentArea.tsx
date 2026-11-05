import { useEffect, useState } from "react";
import { api, type Child, type MasteryRow, type MasteryStatus } from "../api/client";
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

export function ParentArea({ child, onExit }: { child: Child; onExit: () => void }) {
  const [pin, setPin] = useState("");
  const [open, setOpen] = useState(false);
  const [wrong, setWrong] = useState(false);
  const [rows, setRows] = useState<MasteryRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    api
      .mastery(child.id)
      .then(setRows)
      .catch((e: unknown) => setError(String(e)));
  }, [open, child.id]);

  const check = () => {
    if (pin === PIN) setOpen(true);
    else {
      setWrong(true);
      setPin("");
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

  const mastered = rows?.filter((r) => r.status === "mastered").length ?? 0;
  const inProgress = rows?.filter((r) => r.status === "in_progress").length ?? 0;

  return (
    <div className="parent">
      <header>
        <h1>Lernstand von {child.name}</h1>
        <button type="button" className="btn btn-quiet" onClick={onExit}>
          Zurück zum Start
        </button>
      </header>
      {error && <p className="error">{error}</p>}
      {rows && (
        <>
          <p className="summary">
            {mastered} von {rows.length} Fähigkeiten sitzen, {inProgress} sind in Arbeit.
            Mathematik, Jahrgangsstufe 1. Blass gezeichnete Fähigkeiten kann Olli noch nicht
            üben.
          </p>
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
              <h2>{area.title}</h2>
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
