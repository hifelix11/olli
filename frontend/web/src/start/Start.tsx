import type { Child } from "../api/client";
import { Olli } from "../child/Olli";

type Props = {
  kids: Child[];
  onPractice: (child: Child) => void;
  onParent: () => void;
};

export function Start({ kids, onPractice, onParent }: Props) {
  return (
    <div className="start">
      <h1>
        <Olli size={64} />
        Hallo, ich bin Olli.
      </h1>
      <section>
        {kids.length ? (
          <>
            <h2>Wer übt heute?</h2>
            <div className="child-list">
              {kids.map((child) => (
                <button
                  key={child.id}
                  type="button"
                  className="btn btn-primary"
                  onClick={() => onPractice(child)}
                >
                  {child.name}
                </button>
              ))}
            </div>
          </>
        ) : (
          <>
            <h2>Noch kein Kind angelegt</h2>
            <p>Das geht im Elternbereich.</p>
          </>
        )}
      </section>
      <button type="button" className="btn btn-quiet" onClick={onParent}>
        Eltern
      </button>
    </div>
  );
}
