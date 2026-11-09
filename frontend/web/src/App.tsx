import { useEffect, useState } from "react";
import { api, auth, type Child } from "./api/client";
import { Practice } from "./child/Practice";
import { ParentArea } from "./parent/ParentArea";
import { Login } from "./start/Login";
import { Start } from "./start/Start";

type View = { name: "start" } | { name: "practice"; child: Child } | { name: "parent" };

export default function App() {
  const [signedIn, setSignedIn] = useState(auth.signedIn);
  const [view, setView] = useState<View>({ name: "start" });
  const [kids, setKids] = useState<Child[] | null>(null);
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
    api
      .children()
      .then((list) => {
        if (!cancelled) setKids(list);
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
