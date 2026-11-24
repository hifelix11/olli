import { useEffect, useState } from "react";
import {
  api,
  auth,
  type Child,
  type MasteryRow,
  type MasteryStatus,
  type Progress,
  type Sign,
} from "../api/client";
import { Icon } from "../child/Icon";
import { SignIcon } from "../child/Sign";
import { freeSign } from "../child/signs";
import { PinPad } from "./PinPad";
import { SignPicker } from "./SignPicker";

const OFFLINE = "Olli erreicht den Server nicht.";

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
  const [forgot, setForgot] = useState(false);
  const [selected, setSelected] = useState<Child | null>(kids[0] ?? null);
  const [name, setName] = useState("");
  // Vorschlag: das erste Zeichen, das noch kein Geschwisterkind hat.
  const [sign, setSign] = useState<Sign>(freeSign(kids.map((k) => k.sign)));
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

  const check = async () => {
    try {
      const { correct } = await api.checkPin(pin);
      setOpen(correct);
      setWrong(!correct);
      setError(null);
    } catch {
      setError(OFFLINE);
    }
    setPin("");
  };

  /** Neue PIN nur nach Login mit Passwort: PIN löschen, abmelden, das Onboarding fragt danach. */
  const resetPin = async () => {
    try {
      await api.resetPin();
      auth.logout();
    } catch {
      setError(OFFLINE);
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
      const child = await api.createChild(trimmed, sign);
      onAdd(child);
      select(child);
      setName("");
      setSign(freeSign([...kids.map((k) => k.sign), sign]));
      setError(null);
    } catch (e) {
      setError(`${OFFLINE} ${String(e)}`);
    }
  };

  if (!open) {
    return (
      <div className="center-page">
        <span className="lock">
          <Icon name="lock" size={44} />
        </span>
        <h1>Elternbereich</h1>
        <p>Bitte PIN eingeben.</p>
        {wrong && <p className="error">Die PIN stimmt nicht.</p>}
        {error && <p className="error">{error}</p>}
        <PinPad value={pin} onChange={setPin} onSubmit={() => void check()} submitLabel="Öffnen" />
        {forgot ? (
          <>
            <p>Für eine neue PIN mit E-Mail und Passwort neu anmelden.</p>
            <button type="button" className="btn" onClick={() => void resetPin()}>
              Abmelden und neue PIN wählen
            </button>
          </>
        ) : (
          <button type="button" className="btn btn-quiet" onClick={() => setForgot(true)}>
            PIN vergessen?
          </button>
        )}
        <button type="button" className="btn btn-quiet" onClick={onExit}>
          Zurück zum Start
        </button>
      </div>
    );
  }

  return (
    <div className="parent">
      <header className="parent-top">
        <h1>Elternbereich</h1>
        <div>
          <button type="button" className="btn btn-quiet" onClick={onExit}>
            Zurück zum Start
          </button>
          <button type="button" className="btn btn-quiet" onClick={auth.logout}>
            Abmelden
          </button>
        </div>
      </header>
      <section className="panel">
        <h2>Kinder</h2>
        {kids.length > 0 && (
          <div className="tabs">
            {kids.map((child) => (
              <button
                key={child.id}
                type="button"
                className={`tab${child.id === selected?.id ? " on" : ""}`}
                onClick={() => select(child)}
              >
                <SignIcon sign={child.sign} size={40} />
                {child.name}
              </button>
            ))}
          </div>
        )}
        <p className="summary">
          Jedes Kind bekommt ein Zeichen. Daran findet es sich auf der Startseite, auch ohne lesen
          zu können.
        </p>
        <SignPicker value={sign} onChange={setSign} />
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
        <section className="panel">
          <h2>Lernstand von {selected.name}</h2>
          <div className="goal">
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
          </div>
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
        </section>
      )}
    </div>
  );
}
