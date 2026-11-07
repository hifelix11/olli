import type { Task } from "../api/client";
import { BarChart } from "./BarChart";
import { Clock } from "./Clock";
import { countersFor } from "./counters";
import { Dice } from "./Dice";
import { DigitalClock } from "./DigitalClock";
import { Grid } from "./Grid";
import { Lengths } from "./Lengths";
import { Money } from "./Money";
import { NumberLine } from "./NumberLine";
import { pickRepresentation, seedOf } from "./pick";
import { Ruler } from "./Ruler";
import { Scattered } from "./Scattered";
import { Shapes } from "./Shapes";
import { Table } from "./Table";
import { TwentyField } from "./TwentyField";
import { Units } from "./Units";

const num = (task: Task, key: string) => Number(task.operands[key]);
const str = (task: Task, key: string) => String(task.operands[key] ?? "");

/** Das Bild zur Aufgabe. Nichts, wenn die Aufgabe nur als Text erscheint. */
export function Figure({ task, revealed }: { task: Task; revealed: boolean }) {
  switch (pickRepresentation(task)) {
    case "twenty_field": {
      const counters = countersFor(task);
      return counters ? <TwentyField counters={counters} revealed={revealed} /> : null;
    }
    case "dice":
      return <Dice n={num(task, "n")} />;
    case "scattered":
      return <Scattered n={num(task, "n")} seed={seedOf(task.id)} />;
    case "number_line":
      return <NumberLine n={num(task, "n")} />;
    case "shapes":
      return <Shapes shapes={str(task, "shapes")} rotation={num(task, "rotation") || 0} />;
    case "grid":
      return (
        <Grid
          width={num(task, "width")}
          height={num(task, "height")}
          cells={str(task, "cells")}
          copy={str(task, "copy")}
          axis={str(task, "axis")}
          start={str(task, "start")}
          marks={str(task, "marks")}
        />
      );
    case "clock":
      return <Clock hour={num(task, "hour")} minute={num(task, "minute")} />;
    case "digital_clock":
      return <DigitalClock hour={num(task, "hour")} minute={num(task, "minute")} />;
    case "money":
      return <Money coins={str(task, "coins")} unit={str(task, "unit")} />;
    case "lengths":
      return <Lengths a={num(task, "a")} b={num(task, "b")} />;
    case "units":
      return <Units n={num(task, "n")} unit={str(task, "unit")} />;
    case "ruler":
      return <Ruler n={num(task, "n")} />;
    case "bar_chart":
      return (
        <BarChart
          title={str(task, "title")}
          categories={str(task, "categories")}
          values={str(task, "values")}
        />
      );
    case "table":
      return (
        <Table
          title={str(task, "title")}
          categories={str(task, "categories")}
          values={str(task, "values")}
        />
      );
    default:
      return null;
  }
}
