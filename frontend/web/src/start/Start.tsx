import type { Child } from "../api/client";
import { Icon } from "../child/Icon";
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
    <div className="pick">
      <header className="pick-top">
        <span className="wordmark">olli</span>
        <button type="button" className="btn btn-quiet" onClick={onParent}>
          <Icon name="lock" size={20} />
          Eltern
        </button>
      </header>
      <div className="pick-hello">
        <Olli mood="happy" size={112} />
        <h1>Wer übt heute?</h1>
      </div>
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
            <SignIcon sign={child.sign} size={112} />
            {child.name}
          </button>
        ))}
      </div>
    </div>
  );
}
