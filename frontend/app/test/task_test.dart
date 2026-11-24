import 'package:flutter_test/flutter_test.dart';
import 'package:olli/api/models.dart';
import 'package:olli/child/task_view.dart';
import 'package:olli/representations/counters.dart';
import 'package:olli/representations/figure.dart';

import 'fake_backend.dart';

void main() {
  test('splitPrompt trennt Frage und Rechnung', () {
    expect(splitPrompt('8 + 5 = ?'), (question: '', figure: '8 + 5 = ?'));
    expect(splitPrompt('Welche Zahl fehlt? 2, 3, _, 5'), (
      question: 'Welche Zahl fehlt?',
      figure: '2, 3, _, 5',
    ));
    expect(splitPrompt('3 + 4 = 7. Also: 7 − 4 = _'), (
      question: '3 + 4 = 7. Also:',
      figure: '7 − 4 = _',
    ));
    expect(splitPrompt('Wie viele sind es?'), (question: 'Wie viele sind es?', figure: ''));
  });

  test('aroundGap findet die Lücke', () {
    expect(aroundGap('8 + 5 = ?'), ('8 + 5 = ', ''));
    expect(aroundGap('3 + _ = 7'), ('3 + ', ' = 7'));
    expect(aroundGap('3 < 5'), isNull);
  });

  test('pickRepresentation nimmt nur, was die App zeichnen kann', () {
    Task task(String kind, List<String> representations) =>
        Task.fromJson(taskJson('t1', kind: kind, representations: representations));
    expect(pickRepresentation(task('addition', ['plain'])), isNull);
    expect(pickRepresentation(task('addition', ['plain', 'twenty_field'])), 'twenty_field');
    expect(pickRepresentation(task('count', ['fingers'])), 'twenty_field');
    final both = task('bar', ['bar_chart', 'table']);
    expect(pickRepresentation(both), pickRepresentation(both)); // dieselbe Aufgabe, dasselbe Bild
  });

  test('countersFor legt Plättchen je Aufgabenart', () {
    Counters? counters(String kind, Map<String, dynamic> operands) =>
        countersFor(Task.fromJson(taskJson('t1', kind: kind, operands: operands)));
    final minus = counters('subtraction', {'a': 9, 'b': 4})!;
    expect((minus.red, minus.removed), (5, 4));
    final half = counters('double_half', {'value': 8, 'mode': 'half'})!;
    expect((half.red, half.blue, half.layout), (4, 4, CounterLayout.mirror));
    expect(counters('missing_number', {'a': 3, 'c': 7, 'form': '_+b=c'}), isNull);
    expect(counters('compare', {'a': 3, 'b': 7}), isNull);
  });

  test('labelOf zeigt bei Auswahl das Label, sonst die Zahl', () {
    final task = Task.fromJson(
      taskJson(
        't1',
        options: [
          {'value': 'even', 'label': 'gerade'},
        ],
      ),
    );
    expect(task.labelOf('even'), 'gerade');
    expect(task.labelOf(13), '13');
  });
}
