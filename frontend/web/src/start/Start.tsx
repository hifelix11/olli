import type { Child } from "../api/client";
import { Olli } from "../child/Olli";
import { SignIcon } from "../child/Sign";
import { unlockAudio } from "../sound";

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
        <h2>Wer übt heute?</h2>
        <div className="child-list">
          {kids.map((child) => (
            <button
              key={child.id}
              type="button"
              className="child-tile"
              onClick={() => {
                unlockAudio();
                onPractice(child);
              }}
            >
              <SignIcon sign={child.sign} size={72} />
              {child.name}
            </button>
          ))}
        </div>
      </section>
      <button type="button" className="btn btn-quiet" onClick={onParent}>
        Eltern
      </button>
    </div>
  );
}
