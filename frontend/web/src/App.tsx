import { useEffect, useState } from "react";
import { api, auth, type Child } from "./api/client";
import { Practice } from "./child/Practice";
import { ParentArea } from "./parent/ParentArea";
import { Login } from "./start/Login";
import { Onboarding } from "./start/Onboarding";
import { Start } from "./start/Start";

type View = { name: "start" } | { name: "practice"; child: Child } | { name: "parent" };

/** Was dem Konto noch fehlt. null: alles da, kein Onboarding. */
type Setup = { child: boolean; pin: boolean } | null;

export default function App() {
  const [signedIn, setSignedIn] = useState(auth.signedIn);
  const [view, setView] = useState<View>({ name: "start" });
  const [kids, setKids] = useState<Child[] | null>(null);
  const [setup, setSetup] = useState<Setup>(null);
  const [error, setError] = useState<string | null>(null);
  const home = () => setView({ name: "start" });

  useEffect(() => {
    auth.onSignOut(() => {
      setSignedIn(false);
      setKids(null);
      setView({ name: "start" });
    });
  }, []);

  useEffect(() => {
    if (!signedIn) return;
    let cancelled = false;
    Promise.all([api.children(), api.account()])
      .then(([list, account]) => {
        if (cancelled) return;
        const child = list.length === 0;
        const pin = !account.pin_set;
        setSetup(child || pin ? { child, pin } : null);
        setKids(list);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(`Olli erreicht den Server nicht. ${String(e)}`);
      });
    return () => {
      cancelled = true;
    };
  }, [signedIn]);

  if (!signedIn) return <Login onDone={() => setSignedIn(true)} />;
  if (kids === null) {
    return (
      <div className="center-page">
        {error ? <p className="error">{error}</p> : <p>Einen Moment.</p>}
        {error && (
          <button type="button" className="btn btn-quiet" onClick={() => location.reload()}>
            Nochmal versuchen
          </button>
        )}
      </div>
    );
  }

  if (setup) {
    return (
      <Onboarding
        needsChild={setup.child}
        needsPin={setup.pin}
        onAdd={(child) => setKids([...kids, child])}
        onDone={(child) => {
          setSetup(null);
          setView(child ? { name: "practice", child } : { name: "start" });
        }}
      />
    );
  }
  if (view.name === "practice") return <Practice child={view.child} onExit={home} />;
  if (view.name === "parent") {
    return <ParentArea kids={kids} onAdd={(child) => setKids([...kids, child])} onExit={home} />;
  }
  return (
    <Start
      kids={kids}
      onPractice={(child) => setView({ name: "practice", child })}
      onParent={() => setView({ name: "parent" })}
    />
  );
}
