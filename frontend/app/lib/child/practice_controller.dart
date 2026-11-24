import 'dart:async';

import 'package:flutter/foundation.dart';

import '../api/client.dart';
import '../api/models.dart';

const sessionLength = 10;
const _nextAfterRight = Duration(milliseconds: 1100);
const _nextAfterPlacement = Duration(milliseconds: 1400);

/// Olli spricht in der ersten Person. Den Namen des Kindes sagt Olli nie.
const greetingPlacement = [
  'Ich will sehen, was du schon kannst.',
  'Manches ist noch schwer. Das ist okay.',
  'Weißt du etwas nicht? Dann tipp auf das Fragezeichen.',
];
const greetingPractice = [
  'Heute üben wir zusammen.',
  'Nach zehn Aufgaben bekommst du einen Stempel.',
];
const _placementOver = 'Jetzt weiß ich, was du kannst. Ab jetzt üben wir.';
const _stepBack = 'Wir üben erst etwas, das dir dabei hilft.';

/// Wo die Sitzung gerade steht.
sealed class Phase {
  const Phase();
}

final class Loading extends Phase {
  const Loading();
}

/// Begrüßung. Die erste Aufgabe wartet schon dahinter.
final class Welcome extends Phase {
  const Welcome(this.task);

  final Task task;
}

final class Asking extends Phase {
  const Asking(this.task, {required this.retry});

  final Task task;

  /// Zweiter Versuch nach einer falschen Antwort.
  final bool retry;
}

final class Answered extends Phase {
  const Answered(this.task, this.result);

  final Task task;
  final AnswerResult result;
}

final class Done extends Phase {
  const Done({required this.everything});

  /// true: Es gibt nichts mehr zu üben. false: zehn Aufgaben geschafft.
  final bool everything;
}

final class Failed extends Phase {
  const Failed(this.message);

  final String message;
}

/// Der Ablauf einer Sitzung: begrüßen, Aufgabe holen, Antwort schicken, weiter, Stempel.
/// Ohne Oberfläche, damit er sich allein testen lässt.
class PracticeController extends ChangeNotifier {
  PracticeController(this._api, this._childId) {
    _first();
  }

  final Api _api;
  final String _childId;

  Phase phase = const Loading();

  /// Getippte Zahl oder der Wert der gewählten Antwort. Zählt erst mit dem Haken.
  String value = '';

  /// Was Olli gerade sagt.
  String line = '';
  int answered = 0;

  /// Titel der Kompetenzen, die in dieser Sitzung neu sitzen.
  final learned = <String>[];
  bool busy = false;

  /// Zählt die zweiten Versuche. Bei jedem wackelt die Tafel einmal.
  int retries = 0;

  String? _intro; // sagt Olli vor der nächsten Aufgabe
  Timer? _timer;
  bool _disposed = false;

  /// Die gewählte Antwort bei Aufgaben mit Auswahl.
  Option? get selected {
    final phase = this.phase;
    if (phase is! Asking) return null;
    return phase.task.options?.where((o) => '${o.value}' == value).firstOrNull;
  }

  /// Was der Haken abschickt. null: noch nichts gewählt oder getippt.
  Object? get answer {
    final phase = this.phase;
    if (phase is! Asking) return null;
    if (phase.task.options != null) return selected?.value;
    return value.isEmpty ? null : int.parse(value);
  }

  void _set(Phase next) {
    if (_disposed) return;
    phase = next;
    notifyListeners();
  }

  /// Die erste Aufgabe lädt hinter der Begrüßung.
  Future<void> _first() async {
    try {
      final task = await _api.nextTask(_childId);
      _set(task == null ? const Done(everything: true) : Welcome(task));
    } catch (error) {
      _set(Failed('$error'));
    }
  }

  /// Das Kind tippt auf Play.
  void start() {
    final phase = this.phase;
    if (phase is Welcome) _show(phase.task);
  }

  /// Zeigt die Aufgabe, mit Ollis Satz davor, falls einer wartet.
  void _show(Task task) {
    value = '';
    line = _intro ?? '';
    _intro = null;
    _set(Asking(task, retry: false));
  }

  /// Holt die nächste Aufgabe. `previous` ist die Aufgabe davor.
  Future<void> load([Task? previous]) async {
    _set(const Loading());
    try {
      final task = await _api.nextTask(_childId);
      if (_disposed) return;
      if (task == null) return _set(const Done(everything: true));
      if (previous != null && previous.placement && !task.placement) _intro = _placementOver;
      _show(task);
    } catch (error) {
      _set(Failed('$error'));
    }
  }

  void type(String next) {
    value = next;
    notifyListeners();
  }

  /// `answer` null: "Weiß ich noch nicht".
  Future<void> submit(Object? answer) async {
    final phase = this.phase;
    if (phase is! Asking || busy) return;
    final task = phase.task;
    busy = true;
    notifyListeners();
    try {
      final result = await _api.answer(_childId, task.id, answer);
      if (_disposed) return;
      if (result.backtrackedTo != null) _intro = _stepBack;
      if (result.retry) {
        value = '';
        line = 'Schau nochmal.';
        retries++;
        this.phase = Asking(task, retry: true);
        return;
      }
      answered++;
      if (result.mastered && !learned.contains(task.title)) learned.add(task.title);
      final solution = result.answer;
      if (task.placement) {
        // Der Standortcheck probiert absichtlich zu Schweres: kein richtig oder falsch.
        line = answer == null ? 'Das üben wir später.' : 'Gemerkt!';
      } else if (result.correct) {
        line = 'Richtig!';
      } else if (solution != null) {
        line = 'Die Lösung ist ${task.labelOf(solution)}.';
      }
      this.phase = Answered(task, result);
      // Richtig und Standortcheck gehen von selbst weiter. Nach einem Fehler tippt das Kind auf den Pfeil.
      final delay = task.placement
          ? _nextAfterPlacement
          : result.correct
          ? _nextAfterRight
          : null;
      if (delay != null) _timer = Timer(delay, advance);
    } catch (error) {
      this.phase = Failed('$error');
    } finally {
      busy = false;
      if (!_disposed) notifyListeners();
    }
  }

  /// Weiter zur nächsten Aufgabe oder zum Stempel.
  void advance() {
    final phase = this.phase;
    if (phase is! Answered) return;
    _timer?.cancel();
    if (answered >= sessionLength) {
      _set(const Done(everything: false));
    } else {
      load(phase.task);
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _timer?.cancel();
    super.dispose();
  }
}
