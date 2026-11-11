import { Icon } from "./Icon";

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  minLength?: number;
  maxLength?: number;
  /** Ohne Text zeigt der Knopf einen Haken. */
  submitLabel?: string;
  disabled?: boolean;
};

export function Keypad({
  value,
  onChange,
  onSubmit,
  minLength = 1,
  maxLength = 2,
  submitLabel,
  disabled = false,
}: Props) {
  const press = (digit: string) => {
    if (value.length < maxLength) onChange(value + digit);
  };
  return (
    <div className="keypad">
      {["1", "2", "3", "4", "5", "6", "7", "8", "9"].map((d) => (
        <button key={d} type="button" className="key" onClick={() => press(d)} disabled={disabled}>
          {d}
        </button>
      ))}
      <button
        type="button"
        className="key"
        onClick={() => onChange(value.slice(0, -1))}
        disabled={disabled || value.length === 0}
        aria-label="Letzte Ziffer löschen"
      >
        <Icon name="erase" size={34} />
      </button>
      <button type="button" className="key" onClick={() => press("0")} disabled={disabled}>
        0
      </button>
      <button
        type="button"
        className="key key-submit"
        onClick={onSubmit}
        disabled={disabled || value.length < minLength}
        aria-label={submitLabel ? undefined : "Fertig"}
      >
        {submitLabel ?? <Icon name="check" size={34} />}
      </button>
    </div>
  );
}
