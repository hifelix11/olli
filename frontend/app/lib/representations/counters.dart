import '../api/models.dart';

/// `rows`: zeilenweise, die obere Reihe zuerst. `pairs`: spaltenweise, oben und unten
/// (gerade, ungerade). `mirror`: die roten oben, der Rest unten (verdoppeln, halbieren).
enum CounterLayout { rows, pairs, mirror }

/// Plättchen für das Zwanzigerfeld: rot, blau, weggenommen, noch leer.
class Counters {
  const Counters({
    this.red = 0,
    this.blue = 0,
    this.removed = 0,
    this.empty = 0,
    this.layout = CounterLayout.rows,
  });

  final int red;
  final int blue;
  final int removed;
  final int empty;
  final CounterLayout layout;
}

/// null, wenn die Aufgabenart kein Zwanzigerfeld hat. Ob es gezeigt wird, entscheidet `figureFor`.
Counters? countersFor(Task task) {
  int n(String key) => task.number(key).toInt();
  switch (task.kind) {
    case 'count':
      return Counters(red: n('n'));
    case 'addition':
      return Counters(red: n('a'), blue: n('b'));
    case 'subtraction':
      return Counters(red: n('a') - n('b'), removed: n('b'));
    case 'missing_number':
      if (task.operands['form'] != 'a+_=c') return null;
      return Counters(red: n('a'), empty: n('c') - n('a'));
    case 'double_half':
      final value = n('value');
      return task.operands['mode'] == 'double'
          ? Counters(red: value, empty: value, layout: CounterLayout.mirror)
          : Counters(red: value ~/ 2, blue: value ~/ 2, layout: CounterLayout.mirror);
    case 'even_odd':
      return Counters(red: n('n'), layout: CounterLayout.pairs);
    case 'picture_equation':
      if (task.operands['op'] == '+') return Counters(red: n('a'), blue: n('b'));
      return Counters(red: n('a') - n('b'), removed: n('b'));
    case 'switch_representation':
      if (task.operands['form'] != 'twenty_field') return null;
      return Counters(red: n('n'));
    default:
      return null;
  }
}
