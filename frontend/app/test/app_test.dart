import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:olli/app_state.dart';
import 'package:olli/main.dart';

import 'fake_backend.dart';

const _lena = {'id': 'k1', 'name': 'Lena', 'sign': 'fish'};

void main() {
  Future<void> open(WidgetTester tester, FakeBackend backend, {bool signedIn = true}) async {
    tester.view.physicalSize = const Size(1180, 820);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(OlliApp(AppState(await backend.api(signedIn: signedIn))));
    await tester.pumpAndSettle();
  }

  testWidgets('ohne Anmeldung kommt der Login', (tester) async {
    await open(tester, FakeBackend(), signedIn: false);
    expect(find.text('Anmelden'), findsWidgets);
    expect(find.text('Wer übt heute?'), findsNothing);
  });

  testWidgets('fehlen Kind und PIN, kommt das Onboarding', (tester) async {
    await open(tester, FakeBackend(pinSet: false));
    expect(find.text('Wer übt mit mir?'), findsOneWidget);
  });

  testWidgets('ein Kind übt: Zeichen antippen, Play, Zahl tippen, Haken', (tester) async {
    final backend = FakeBackend(
      kids: [_lena],
      tasks: [
        taskJson('t1'),
        taskJson('t2', prompt: '4 + 4 = ?'),
      ],
      results: [resultJson()],
    );
    await open(tester, backend);
    expect(find.text('Wer übt heute?'), findsOneWidget);

    await tester.tap(find.text('Lena'));
    await tester.pumpAndSettle();
    expect(find.text('Hallo, Lena!'), findsOneWidget);

    await tester.tap(find.bySemanticsLabel("Los geht's"));
    await tester.pumpAndSettle();
    expect(find.text('8 + 5 ='), findsOneWidget);

    await tester.tap(find.text('1'));
    await tester.pump();
    await tester.tap(find.text('3'));
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('Fertig'));
    await tester.pump();
    expect(find.text('Richtig!'), findsOneWidget);
    expect(backend.sent, contains('POST /children/k1/answers {"task_id":"t1","answer":13}'));

    // Richtig geht von selbst weiter.
    await tester.pump(const Duration(milliseconds: 1100));
    await tester.pumpAndSettle();
    expect(find.text('4 + 4 ='), findsOneWidget);
  });

  testWidgets('der Elternbereich öffnet nur mit der PIN', (tester) async {
    await open(tester, FakeBackend(kids: [_lena]));
    await tester.tap(find.text('Eltern'));
    await tester.pumpAndSettle();

    Future<void> enter(String pin) async {
      for (final digit in pin.split('')) {
        await tester.tap(find.text(digit));
        await tester.pump();
      }
      await tester.tap(find.text('Öffnen'));
      await tester.pumpAndSettle();
    }

    await enter('1111');
    expect(find.text('Die PIN stimmt nicht.'), findsOneWidget);

    await enter('1234');
    expect(find.text('Lernstand von Lena'), findsOneWidget);
  });
}
