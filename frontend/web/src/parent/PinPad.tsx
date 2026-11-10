import { Keypad } from "../child/Keypad";

const LENGTH = 4;

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  submitLabel: string;
};

/** Vier Punkte und der Zahlenblock. Abschicken geht erst mit vier Ziffern. */
export function PinPad({ value, onChange, onSubmit, submitLabel }: Props) {
  return (
    <div className="pin">
      <div className="pin-dots" aria-label={`${value.length} von ${LENGTH} Ziffern`}>
        {Array.from({ length: LENGTH }, (_, i) => (
          <span key={i} className={i < value.length ? "on" : ""} />
        ))}
      </div>
      <Keypad
        value={value}
        onChange={onChange}
        onSubmit={onSubmit}
        minLength={LENGTH}
        maxLength={LENGTH}
        submitLabel={submitLabel}
      />
    </div>
  );
}
