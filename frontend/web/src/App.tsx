import { useState } from "react";
import type { Child } from "./api/client";
import { Practice } from "./child/Practice";
import { ParentArea } from "./parent/ParentArea";
import { Start } from "./start/Start";
import { loadChildren, saveChildren } from "./storage";

type View = { name: "start" } | { name: "practice"; child: Child } | { name: "parent" };

export default function App() {
  const [view, setView] = useState<View>({ name: "start" });
  const [kids, setKids] = useState<Child[]>(loadChildren);
  const home = () => setView({ name: "start" });
  const add = (child: Child) => {
    const next = [...kids, child];
    setKids(next);
    saveChildren(next);
  };

  if (view.name === "practice") return <Practice child={view.child} onExit={home} />;
  if (view.name === "parent") return <ParentArea kids={kids} onAdd={add} onExit={home} />;
  return (
    <Start
      kids={kids}
      onPractice={(child) => setView({ name: "practice", child })}
      onParent={() => setView({ name: "parent" })}
    />
  );
}
