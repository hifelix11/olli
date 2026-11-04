import { useState } from "react";
import type { Child } from "./api/client";
import { Practice } from "./child/Practice";
import { ParentArea } from "./parent/ParentArea";
import { Start } from "./start/Start";

type View = { name: "start" } | { name: "practice"; child: Child } | { name: "parent"; child: Child };

export default function App() {
  const [view, setView] = useState<View>({ name: "start" });
  const home = () => setView({ name: "start" });

  if (view.name === "practice") return <Practice child={view.child} onExit={home} />;
  if (view.name === "parent") return <ParentArea child={view.child} onExit={home} />;
  return (
    <Start
      onPractice={(child) => setView({ name: "practice", child })}
      onParent={(child) => setView({ name: "parent", child })}
    />
  );
}
