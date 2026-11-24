import 'package:flutter_test/flutter_test.dart';
import 'package:olli/child/practice_controller.dart';

import 'fake_backend.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  /// Startet eine Sitzung und wartet auf die Begrüßung.
  Future<PracticeController> session(FakeBackend backend) async {
    final controller = PracticeController(await backend.api(), 'k1');
    await pumpEventQueue();
    return controller;
  }

  test('freie Eingabe: zweiter Versuch, dann die Lösung, weiter mit dem Pfeil', () async {
    final backend = FakeBackend(
      tasks: [taskJson('t1'), taskJson('t2')],
      results: [resultJson(correct: false, answer: null, retry: true), resultJson(correct: false)],
    );
    final c = await session(backend);
    expect(c.phase, isA<Welcome>());

    c.start();
    expect(c.phase, isA<Asking>());
    expect(c.answer, isNull);

    c.type('12');
    await c.submit(c.answer);
    expect((c.phase as Asking).retry, isTrue);
    expect(c.line, 'Schau nochmal.');
    expect(c.value, '');
    expect(c.retries, 1);
    expect(c.answered, 0);

    c.type('11');
    await c.submit(c.answer);
    expect(c.phase, isA<Answered>());
    expect(c.line, 'Die Lösung ist 13.');
    expect(c.answered, 1);

    c.advance();
    await pumpEventQueue();
    expect((c.phase as Asking).task.id, 't2');
    expect(backend.sent.where((s) => s.contains('/answers')), [
      'POST /children/k1/answers {"task_id":"t1","answer":12}',
      'POST /children/k1/answers {"task_id":"t1","answer":11}',
    ]);
  });

  testWidgets('richtig geht von selbst weiter', (tester) async {
    final backend = FakeBackend(tasks: [taskJson('t1'), taskJson('t2')], results: [resultJson()]);
    final c = PracticeController(await backend.api(), 'k1');
    await tester.pump();
    c.start();
    c.type('13');
    await c.submit(c.answer);
    expect(c.line, 'Richtig!');
    expect(c.phase, isA<Answered>());

    await tester.pump(const Duration(milliseconds: 1100));
    await tester.pump();
    expect((c.phase as Asking).task.id, 't2');
  });

  test('Auswahl: Der Haken schickt den Wert, Olli nennt das Label', () async {
    final options = [
      {'value': 'even', 'label': 'gerade'},
      {'value': 'odd', 'label': 'ungerade'},
    ];
    final backend = FakeBackend(
      tasks: [
        taskJson('t1', kind: 'even_odd', prompt: 'Ist 7 gerade oder ungerade?', options: options),
      ],
      results: [resultJson(correct: false, answer: 'odd')],
    );
    final c = await session(backend);
    c.start();
    expect(c.answer, isNull);

    c.type('even');
    expect(c.selected?.label, 'gerade');
    await c.submit(c.answer);
    expect(c.line, 'Die Lösung ist ungerade.');
    expect(backend.sent.last, contains('"answer":"even"'));
  });

  testWidgets('Standortcheck: kein richtig oder falsch, danach beginnt das Üben', (tester) async {
    final backend = FakeBackend(
      tasks: [taskJson('p1', placement: true), taskJson('t2')],
      results: [resultJson(correct: false)],
    );
    final c = PracticeController(await backend.api(), 'k1');
    await tester.pump();
    c.start();
    await c.submit(null); // "Weiß ich noch nicht"
    expect(c.line, 'Das üben wir später.');

    await tester.pump(const Duration(milliseconds: 1400));
    await tester.pump();
    expect((c.phase as Asking).task.id, 't2');
    expect(c.line, 'Jetzt weiß ich, was du kannst. Ab jetzt üben wir.');
  });

  test('zurück zu den Grundlagen: Olli kündigt es vor der nächsten Aufgabe an', () async {
    final backend = FakeBackend(
      tasks: [taskJson('t1'), taskJson('t2')],
      results: [resultJson(correct: false, backtrackedTo: 'plus_bis_10')],
    );
    final c = await session(backend);
    c.start();
    c.type('1');
    await c.submit(c.answer);
    c.advance();
    await pumpEventQueue();
    expect(c.line, 'Wir üben erst etwas, das dir dabei hilft.');
  });

  test('nach zehn Aufgaben ist Schluss, neu Gemeistertes steht einmal auf der Liste', () async {
    final backend = FakeBackend(
      tasks: [for (var i = 0; i < 11; i++) taskJson('t$i')],
      results: [for (var i = 0; i < 10; i++) resultJson(correct: false, mastered: i < 2)],
    );
    final c = await session(backend);
    c.start();
    for (var i = 0; i < sessionLength; i++) {
      c.type('1');
      await c.submit(c.answer);
      c.advance();
      await pumpEventQueue();
    }
    expect(c.phase, isA<Done>());
    expect((c.phase as Done).everything, isFalse);
    expect(c.learned, ['Plus bis 20']);
  });

  test('nichts mehr zu üben: Ende ohne Aufgabe', () async {
    final c = await session(FakeBackend());
    expect((c.phase as Done).everything, isTrue);
  });

  test('Server nicht erreichbar: Fehler statt Aufgabe', () async {
    final backend = FakeBackend(tasks: [taskJson('t1')]); // kein Ergebnis für die Antwort
    final c = await session(backend);
    c.start();
    c.type('1');
    await c.submit(c.answer);
    expect(c.phase, isA<Failed>());
  });
}
