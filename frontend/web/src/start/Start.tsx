import { useState } from "react";
import { api, type Child } from "../api/client";
import { Olli } from "../child/Olli";
import { loadChildren, saveChildren } from "../storage";

type Props = {
  onPractice: (child: Child) => void;
  onParent: (child: Child) => void;
};

export function Start({ onPractice, onParent }: Props) {
  const [children, setChildren] = useState<Child[]>(loadChildren);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const add = async () => {
    const trimmed = name.trim();
    if (!trimmed) return;
    try {
      const child = await api.createChild(trimmed);
      const next = [...children, child];
      setChildren(next);
      saveChildren(next);
      setName("");
      setError(null);
    } catch (e) {
      setError(`Olli erreicht den Server nicht. ${String(e)}`);
    }
  };

  return (
    <div className="start">
      <h1>
        <Olli size={64} />
        Hallo, ich bin Olli.
      </h1>
      {children.length > 0 && (
        <section>
          <h2>Wer übt heute?</h2>
          <div className="child-list">
            {children.map((child) => (
              <div className="child-row" key={child.id}>
                <button type="button" className="btn btn-primary" onClick={() => onPractice(child)}>
                  {child.name}
                </button>
                <button type="button" className="btn btn-quiet" onClick={() => onParent(child)}>
                  Eltern
                </button>
              </div>
            ))}
          </div>
        </section>
      )}
      <section>
        <h2>{children.length ? "Noch ein Kind" : "Wie heißt du?"}</h2>
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
            Los
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>
    </div>
  );
}
