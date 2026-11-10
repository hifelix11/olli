import { useState } from "react";
import { api, type Child, type Sign } from "../api/client";
import { Olli } from "../child/Olli";
import { freeSign } from "../child/signs";
import { PinPad } from "../parent/PinPad";
import { SignPicker } from "../parent/SignPicker";
import { unlockAudio } from "../sound";

type Step = "child" | "pin" | "done";

type Props = {
  needsChild: boolean;
  needsPin: boolean;
  onAdd: (child: Child) => void;
  /** child: das neue Kind übt gleich. null: zurück zum Start. */
  onDone: (child: Child | null) => void;
};

const OFFLINE = "Olli erreicht den Server nicht.";

/** Erster Start nach der Anmeldung. Zeigt nur, was noch fehlt: Kind, PIN. */
export function Onboarding({ needsChild, needsPin, onAdd, onDone }: Props) {
  const steps = (["child", "pin", "done"] as Step[]).filter((s) =>
    s === "pin" ? needsPin : needsChild,
  );
  const [index, setIndex] = useState(0);
  const [child, setChild] = useState<Child | null>(null);
  const [name, setName] = useState("");
  const [sign, setSign] = useState<Sign>(freeSign([]));
  const [pin, setPin] = useState("");
  const [first, setFirst] = useState<string | null>(null); // erste Eingabe, wartet auf Wiederholung
  const [error, setError] = useState<string | null>(null);

  const next = (created: Child | null) => {
    setError(null);
    if (index + 1 < steps.length) setIndex(index + 1);
    else onDone(created);
  };

  const addChild = async () => {
    try {
      const created = await api.createChild(name.trim(), sign);
      onAdd(created);
      setChild(created);
      next(created);
    } catch {
      setError(OFFLINE);
    }
  };

  const choosePin = async () => {
    setPin("");
    if (first === null) {
      setFirst(pin);
      setError(null);
    } else if (pin !== first) {
      setFirst(null);
      setError("Die beiden PINs sind verschieden. Bitte neu wählen.");
    } else {
      try {
        await api.setPin(pin);
        next(child);
      } catch {
        setFirst(null);
        setError(OFFLINE);
      }
    }
  };

  const step = steps[index];
  return (
    <div className="start onboarding">
      <h1>
        <Olli size={64} />
        Hallo, ich bin Olli.
      </h1>
      {step === "child" && (
        <section>
          <h2>Wer übt mit mir?</h2>
          <p>
            Ich übe Mathe mit Kindern der ersten Jahrgangsstufe. Ich merke mir, was sitzt, und gehe
            zurück, wo es hängt.
          </p>
          <p>
            Zuerst ein Zeichen. Daran findet sich das Kind auf der Startseite, auch ohne lesen zu
            können.
          </p>
          <SignPicker value={sign} onChange={setSign} />
          <form
            className="add"
            onSubmit={(e) => {
              e.preventDefault();
              void addChild();
            }}
          >
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Vorname"
              aria-label="Vorname des Kindes"
              maxLength={30}
              autoFocus
            />
            <button type="submit" className="btn btn-primary" disabled={!name.trim()}>
              Weiter
            </button>
          </form>
          {error && <p className="error">{error}</p>}
          <p>Ein Vorname oder Spitzname reicht. Weitere Kinder kommen im Elternbereich dazu.</p>
        </section>
      )}
      {step === "pin" && (
        <section>
          <h2>{first === null ? "PIN für den Elternbereich" : "PIN noch einmal"}</h2>
          <p>
            {first === null
              ? "Vier Ziffern. Die PIN hält Kinder aus dem Elternbereich. Bitte nicht die PIN der Bankkarte."
              : "Zur Sicherheit die gleiche PIN noch einmal."}
          </p>
          {error && <p className="error">{error}</p>}
          <PinPad
            value={pin}
            onChange={setPin}
            onSubmit={() => void choosePin()}
            submitLabel="Weiter"
          />
        </section>
      )}
      {step === "done" && child && (
        <section>
          <h2>Fertig</h2>
          <p>
            Jetzt ist {child.name} dran. Zuerst schaue ich, was {child.name} schon kann. Fehler sind
            dabei ganz normal.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => {
              unlockAudio();
              onDone(child);
            }}
          >
            Los geht's
          </button>
        </section>
      )}
    </div>
  );
}
