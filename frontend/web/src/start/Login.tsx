import { useState } from "react";
import { ApiError, auth } from "../api/client";
import { Entry } from "./Entry";

const MESSAGES: Record<string, string> = {
  invalid_credentials: "E-Mail oder Passwort stimmt nicht.",
  user_already_exists: "Zu dieser E-Mail gibt es schon ein Konto.",
  weak_password: "Das Passwort ist zu kurz oder zu einfach.",
  email_not_confirmed: "Die E-Mail-Adresse ist noch nicht bestätigt. Der Link steht in der E-Mail.",
  email_address_invalid: "Die E-Mail-Adresse sieht nicht richtig aus.",
  validation_failed: "Die E-Mail-Adresse sieht nicht richtig aus.",
  over_request_rate_limit: "Zu viele Versuche. Bitte in ein paar Minuten noch einmal.",
  over_email_send_rate_limit: "Zu viele Versuche. Bitte in ein paar Minuten noch einmal.",
};

function message(error: unknown): string {
  if (!(error instanceof ApiError)) return "Olli erreicht den Server nicht.";
  return MESSAGES[error.code] ?? `Das hat nicht geklappt (${error.code}).`;
}

type Props = { onDone: () => void };

export function Login({ onDone }: Props) {
  const [signup, setSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const submit = async () => {
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      if (!signup) {
        await auth.login(email.trim(), password);
        onDone();
      } else if (await auth.signup(email.trim(), password)) {
        onDone();
      } else {
        setSignup(false);
        setInfo("Fast geschafft. Bitte den Link in der E-Mail öffnen und dann hier anmelden.");
      }
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };

  const title = signup ? "Konto anlegen" : "Anmelden";
  return (
    <Entry>
      <section>
        <h2>{title}</h2>
        <p>Das Konto gehört den Eltern. Kinder üben ohne eigenes Konto.</p>
        <form
          className="login"
          onSubmit={(e) => {
            e.preventDefault();
            void submit();
          }}
        >
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="E-Mail"
            aria-label="E-Mail"
            autoComplete="email"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Passwort"
            aria-label="Passwort"
            autoComplete={signup ? "new-password" : "current-password"}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={busy || !email.trim() || !password}
          >
            {title}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
        {info && <p>{info}</p>}
      </section>
      <button
        type="button"
        className="btn btn-quiet"
        onClick={() => {
          setSignup(!signup);
          setError(null);
          setInfo(null);
        }}
      >
        {signup ? "Schon ein Konto? Anmelden" : "Noch kein Konto? Konto anlegen"}
      </button>
    </Entry>
  );
}
