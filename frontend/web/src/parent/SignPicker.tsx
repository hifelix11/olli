import type { Sign } from "../api/client";
import { SignIcon } from "../child/Sign";
import { SIGN_NAMES, SIGNS } from "../child/signs";

/** Zeichen für ein neues Kind wählen. Im Elternbereich und im Onboarding. */
export function SignPicker({ value, onChange }: { value: Sign; onChange: (sign: Sign) => void }) {
  return (
    <div className="signs" role="radiogroup" aria-label="Zeichen">
      {SIGNS.map((s) => (
        <button
          key={s}
          type="button"
          role="radio"
          aria-checked={s === value}
          aria-label={SIGN_NAMES[s]}
          className={`sign-choice${s === value ? " on" : ""}`}
          onClick={() => onChange(s)}
        >
          <SignIcon sign={s} size={36} />
        </button>
      ))}
    </div>
  );
}
