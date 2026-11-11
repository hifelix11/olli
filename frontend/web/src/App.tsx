import { useEffect, useState } from "react";
import { api, auth, type Child } from "./api/client";
import { Olli } from "./child/Olli";
import { Practice } from "./child/Practice";
import { ParentArea } from "./parent/ParentArea";
import { navigate, useRoute } from "./route";
import { Login } from "./start/Login";
import { Onboarding } from "./start/Onboarding";
import { Start } from "./start/Start";

/** Was dem Konto noch fehlt. null: alles da, kein Onboarding. */
type Setup = { child: boolean; pin: boolean } | null;

export default function App() {
  const [signedIn, setSignedIn] = useState(auth.signedIn);
  const [kids, setKids] = useState<Child[] | null>(null);
  const [setup, setSetup] = useState<Setup>(null);
  const [error, setError] = useState<string | null>(null);
  const route = useRoute();
  const home = () => navigate({ name: "start" });
  const practicing = route?.name === "practice" ? kids?.find((k) => k.id === route.childId) : undefined;
  // Unbekannte Adresse oder fremdes Kind: zurück zum Start.
  const lost = kids !== null && (route === null || (route.name === "practice" && !practicing));

  useEffect(() => {
    auth.onSignOut(() => {
      setSignedIn(false);
      setKids(null);
      navigate({ name: "start" }, true);
    });
  }, []);

  useEffect(() => {
    if (lost) navigate({ name: "start" }, true);
  }, [lost]);

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
        <Olli mood="thinking" size={120} />
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
          navigate(child ? { name: "practice", childId: child.id } : { name: "start" });
        }}
      />
    );
  }
  if (practicing) return <Practice key={practicing.id} child={practicing} onExit={home} />;
  if (route?.name === "parent") {
    return <ParentArea kids={kids} onAdd={(child) => setKids([...kids, child])} onExit={home} />;
  }
  return (
    <Start
      kids={kids}
      onPractice={(child) => navigate({ name: "practice", childId: child.id })}
      onParent={() => navigate({ name: "parent" })}
    />
  );
}
