import 'package:flutter/widgets.dart';

import '../api/models.dart';
import 'clock.dart';
import 'counters.dart';
import 'data.dart';
import 'dice.dart';
import 'grid.dart';
import 'lengths.dart';
import 'money.dart';
import 'number_line.dart';
import 'scattered.dart';
import 'shapes.dart';
import 'twenty_field.dart';

/// Darstellungen, die die App zeichnen kann. `plain` ist keine.
const _renderable = {
  'twenty_field',
  'dice',
  'scattered',
  'number_line',
  'shapes',
  'grid',
  'clock',
  'digital_clock',
  'money',
  'lengths',
  'units',
  'ruler',
  'bar_chart',
  'table',
};

/// Kleine Zahl aus der Aufgaben-ID, damit dieselbe Aufgabe immer dasselbe Bild bekommt.
int seedOf(String id) {
  var h = 7;
  for (final unit in id.codeUnits) {
    h = (h * 31 + unit) & 0xFFFFFFFF;
  }
  return h;
}

/// Erste zeichenbare Darstellung der Aufgabe. Bei mehreren entscheidet die ID.
/// Zählaufgaben zeigen immer ein Bild.
String? pickRepresentation(Task task) {
  final renderable = task.representations.where(_renderable.contains).toList();
  if (renderable.isEmpty) return task.kind == 'count' ? 'twenty_field' : null;
  return renderable[seedOf(task.id) % renderable.length];
}

/// Das Bild zur Aufgabe. null, wenn die Aufgabe nur als Text erscheint.
Widget? figureFor(Task task, {required bool revealed}) {
  int n(String key) => task.number(key).toInt();
  switch (pickRepresentation(task)) {
    case 'twenty_field':
      final counters = countersFor(task);
      return counters == null ? null : TwentyField(counters, revealed: revealed);
    case 'dice':
      return Dice(n('n'));
    case 'scattered':
      return Scattered(n('n'), seed: seedOf(task.id));
    case 'number_line':
      return NumberLine(task.number('n'));
    case 'shapes':
      return Shapes(shapes: task.text('shapes'), rotation: task.number('rotation'));
    case 'grid':
      return Grid(
        width: n('width'),
        height: n('height'),
        cells: task.text('cells'),
        copy: task.text('copy'),
        axis: task.text('axis'),
        start: task.text('start'),
        marks: task.text('marks'),
      );
    case 'clock':
      return Clock(hour: n('hour'), minute: n('minute'));
    case 'digital_clock':
      return DigitalClock(hour: n('hour'), minute: n('minute'));
    case 'money':
      return Money(coins: task.text('coins'), unit: task.text('unit'));
    case 'lengths':
      return Lengths(a: task.number('a'), b: task.number('b'));
    case 'units':
      return Units(n: n('n'), unit: task.text('unit'));
    case 'ruler':
      return Ruler(task.number('n'));
    case 'bar_chart':
      return BarChart(
        title: task.text('title'),
        categories: task.text('categories'),
        values: task.text('values'),
      );
    case 'table':
      return ValueTable(
        title: task.text('title'),
        categories: task.text('categories'),
        values: task.text('values'),
      );
    default:
      return null;
  }
}
