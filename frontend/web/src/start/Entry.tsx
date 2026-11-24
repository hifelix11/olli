import type { ReactNode } from "react";
import { Olli } from "../child/Olli";

/** Rahmen für Anmelden und Onboarding: Olli auf Rosa, daneben das Formular. */
export function Entry({ children }: { children: ReactNode }) {
  return (
    <div className="entry">
      <aside className="entry-hero">
        <span className="wordmark">olli</span>
        <div className="entry-hello">
          <Olli mood="happy" size={168} />
          <div>
            <h1>Hallo, ich bin Olli.</h1>
            <p>Ich übe Mathe mit Kindern der ersten Jahrgangsstufe.</p>
          </div>
        </div>
      </aside>
      <main className="entry-form">{children}</main>
    </div>
  );
}
