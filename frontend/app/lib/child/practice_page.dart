import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

import '../api/client.dart';
import '../api/models.dart';
import '../olli/olli_view.dart';
import '../ui/controls.dart';
import '../ui/icons.dart';
import '../ui/tokens.dart';
import 'practice_controller.dart';
import 'stamp.dart';
import 'task_view.dart';

/// Eine Sitzung: Begrüßung, zehn Aufgaben, Stempel. Danach ist Schluss, ohne "Noch eine Runde".
class PracticePage extends StatefulWidget {
  const PracticePage({super.key, required this.api, required this.child, required this.onExit});

  final Api api;
  final Child child;
  final VoidCallback onExit;

  @override
  State<PracticePage> createState() => _PracticePageState();
}

class _PracticePageState extends State<PracticePage> {
  late final _session = PracticeController(widget.api, widget.child.id);

  @override
  void dispose() {
    _session.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: _session,
    builder: (context, _) => switch (_session.phase) {
      Failed(:final message) => CenterPage(
        onHome: widget.onExit,
        children: [
          const OlliView(mood: Mood.thinking, size: 120),
          const PageTitle('Ich erreiche den Server nicht.'),
          ErrorText(message),
          Btn('Nochmal versuchen', kind: BtnKind.primary, onTap: _session.load),
        ],
      ),
      Welcome(:final task) => _welcome(context, task),
      Done(:final everything) => _done(everything),
      _ => _Stage(_session, onExit: widget.onExit),
    },
  );

  /// Volle Farbe nur an den Rändern der Sitzung: die Begrüßung ist blau.
  Widget _welcome(BuildContext context, Task task) => CenterPage(
    color: Tokens.blue,
    textColor: Tokens.white,
    onHome: widget.onExit,
    children: [
      const OlliView(mood: Mood.happy, size: 184),
      PageTitle('Hallo, ${widget.child.name}!'),
      ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 340),
        child: Column(
          children: [
            for (final line in task.placement ? greetingPlacement : greetingPractice)
              Text(line, style: jost(24, FontWeight.w500)),
          ],
        ),
      ),
      RoundButton(
        IconName.play,
        onTap: _session.start,
        label: "Los geht's",
        size: 136,
        iconSize: 64,
        nudge: 10,
      ),
    ],
  );

  /// Das Ende ist gelb. Rot mit Stern ist der Stempel, wenn etwas neu sitzt.
  Widget _done(bool everything) => CenterPage(
    color: Tokens.sun,
    children: [
      Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        spacing: 8,
        children: [
          const OlliView(mood: Mood.happy, size: 128),
          Stamp(special: _session.learned.isNotEmpty),
        ],
      ),
      PageTitle(everything ? 'Du kannst schon alles!' : 'Fertig für heute!'),
      if (_session.learned.isNotEmpty)
        Wrap(
          alignment: WrapAlignment.center,
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final title in _session.learned)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                decoration: BoxDecoration(
                  color: Tokens.board,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text('Neu: $title', style: jost(20, FontWeight.w700)),
              ),
          ],
        ),
      Btn('Zum Start', kind: BtnKind.primary, icon: IconName.home, onTap: widget.onExit),
    ],
  );
}

/// Üben: oben Haus und Fortschritt, in der Mitte Olli auf der Kante der Tafel, darunter die Antworten.
/// Die Aufgabe bleibt ruhig: weiße Tafel auf Kreide.
class _Stage extends StatelessWidget {
  const _Stage(this.session, {required this.onExit});

  final PracticeController session;
  final VoidCallback onExit;

  /// Auf dem Rechner geht auch die Tastatur: Ziffern, Löschen, Enter.
  KeyEventResult _onKey(FocusNode node, KeyEvent event) {
    final phase = session.phase;
    if (event is! KeyDownEvent || phase is! Asking || session.busy) return KeyEventResult.ignored;
    final key = event.logicalKey;
    if (key == LogicalKeyboardKey.enter || key == LogicalKeyboardKey.numpadEnter) {
      final answer = session.answer;
      if (answer == null) return KeyEventResult.ignored;
      session.submit(answer);
      return KeyEventResult.handled;
    }
    if (phase.task.options != null) return KeyEventResult.ignored;
    final value = session.value;
    final digit = event.character;
    if (digit != null && RegExp(r'^[0-9]$').hasMatch(digit) && value.length < 2) {
      session.type(value + digit);
      return KeyEventResult.handled;
    }
    if (key == LogicalKeyboardKey.backspace && value.isNotEmpty) {
      session.type(value.substring(0, value.length - 1));
      return KeyEventResult.handled;
    }
    return KeyEventResult.ignored;
  }

  @override
  Widget build(BuildContext context) {
    final compact = isCompact(context);
    final phase = session.phase;
    final (task, result) = switch (phase) {
      Asking(:final task) => (task, null),
      Answered(:final task, :final result) => (task, result),
      _ => (null, null),
    };
    final retry = phase is Asking && phase.retry;
    final placement = task?.placement ?? false;
    final judged =
        result != null && !placement; // Der Standortcheck zeigt kein richtig oder falsch.
    final mood = retry
        ? Mood.thinking
        : judged
        ? (result.correct ? Mood.happy : Mood.thinking)
        : Mood.neutral;
    final solution = judged ? result.answer : null;
    // In der Lücke steht die Lösung, sonst die gewählte Antwort oder die getippten Ziffern.
    final shown = solution != null && task != null
        ? task.labelOf(solution)
        : session.selected?.label ?? session.value;

    final olliSize = compact ? 72.0 : 100.0;
    final talkTop = compact ? 4.0 : 8.0;
    final overlap = compact ? 18.0 : 24.0; // so tief sitzt Olli auf der Tafel

    return Focus(
      autofocus: true,
      onKeyEvent: _onKey,
      child: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: Column(
              children: [
                Padding(
                  padding: compact
                      ? const EdgeInsets.fromLTRB(16, 12, 16, 0)
                      : const EdgeInsets.fromLTRB(20, 16, 20, 0),
                  child: Row(
                    children: [
                      HomeButton(onExit),
                      Expanded(child: Center(child: _SessionDots(session.answered))),
                      const SizedBox(width: 56),
                    ],
                  ),
                ),
                Expanded(
                  child: CenterScroll(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Stack(
                          children: [
                            Padding(
                              padding: EdgeInsets.fromLTRB(
                                compact ? 12 : 20,
                                talkTop + olliSize - overlap,
                                compact ? 12 : 20,
                                0,
                              ),
                              child: Center(
                                child: ConstrainedBox(
                                  constraints: const BoxConstraints(maxWidth: 760),
                                  child: task == null
                                      ? const SizedBox(width: double.infinity)
                                      : _Shake(
                                          session.retries,
                                          child: TaskBoard(
                                            task: task,
                                            shown: shown,
                                            revealed: solution != null,
                                            cheer: judged && result.correct,
                                          ),
                                        ),
                                ),
                              ),
                            ),
                            Positioned(
                              top: talkTop,
                              left: 0,
                              right: 0,
                              child: Center(
                                child: ConstrainedBox(
                                  constraints: const BoxConstraints(maxWidth: 800),
                                  child: Padding(
                                    padding: EdgeInsets.symmetric(horizontal: compact ? 24 : 36),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      spacing: 12,
                                      children: [
                                        OlliView(mood: mood, size: olliSize),
                                        if (session.line.isNotEmpty)
                                          Flexible(child: _Bubble(session.line, compact: compact)),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                        Padding(
                          padding: const EdgeInsets.fromLTRB(20, 24, 20, 28),
                          child: task == null
                              ? null
                              : TaskInput(
                                  task: task,
                                  value: session.value,
                                  onChange: session.type,
                                  onSubmit: session.submit,
                                  closed: result != null,
                                  canSkip: placement,
                                  busy: session.busy,
                                  onNext: judged && !result.correct ? session.advance : null,
                                ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Zehn Plättchen für zehn Aufgaben, mit Lücke nach fünf wie im Zwanzigerfeld.
class _SessionDots extends StatelessWidget {
  const _SessionDots(this.answered);

  final int answered;

  @override
  Widget build(BuildContext context) {
    final compact = isCompact(context);
    final size = compact ? 15.0 : 20.0;

    Widget dot(int i) {
      final filled = i < answered;
      final dot = Container(
        width: size,
        height: size,
        margin: EdgeInsets.only(left: i == 5 ? (compact ? 7 : 10) : 0),
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: filled ? Tokens.blue : null,
          border: filled ? null : Border.all(color: Tokens.line, width: compact ? 2.5 : 3),
        ),
      );
      if (!filled || reducedMotion(context)) return dot;
      // Ein Plättchen ploppt in den Fortschritt.
      return TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.2, end: 1),
        duration: const Duration(milliseconds: 400),
        curve: const Cubic(0.3, 1.6, 0.5, 1),
        child: dot,
        builder: (context, scale, child) => Transform.scale(scale: scale, child: child),
      );
    }

    return Semantics(
      label: '$answered von $sessionLength Aufgaben',
      child: Row(
        mainAxisSize: MainAxisSize.min,
        spacing: compact ? 4 : 6,
        children: [for (var i = 0; i < sessionLength; i++) dot(i)],
      ),
    );
  }
}

/// Ollis Sprechblase, mit Zipfel zu Olli hin.
class _Bubble extends StatelessWidget {
  const _Bubble(this.text, {required this.compact});

  final String text;
  final bool compact;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(top: 6),
    child: Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          constraints: const BoxConstraints(maxWidth: 360),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          decoration: BoxDecoration(color: Tokens.pink, borderRadius: BorderRadius.circular(24)),
          child: Semantics(
            liveRegion: true,
            child: Text(text, style: jost(compact ? 19 : 22, FontWeight.w600, height: 1.3)),
          ),
        ),
        const Positioned(
          left: -9,
          top: 22,
          child: CustomPaint(size: Size(10, 20), painter: _TailPainter()),
        ),
      ],
    ),
  );
}

class _TailPainter extends CustomPainter {
  const _TailPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final tail = Path()
      ..moveTo(size.width, 0)
      ..lineTo(0, size.height / 2)
      ..lineTo(size.width, size.height)
      ..close();
    canvas.drawPath(tail, Paint()..color = Tokens.pink);
  }

  @override
  bool shouldRepaint(_TailPainter old) => false;
}

/// Zweiter Versuch: Die Tafel wackelt einmal, jedes Mal, wenn `count` steigt.
class _Shake extends StatelessWidget {
  const _Shake(this.count, {required this.child});

  final int count;
  final Widget child;

  static const _steps = [0.0, -10.0, 8.0, -5.0, 3.0, 0.0];

  @override
  Widget build(BuildContext context) {
    if (reducedMotion(context)) return child;
    return TweenAnimationBuilder<double>(
      tween: Tween(end: count.toDouble()),
      duration: const Duration(milliseconds: 450),
      child: child,
      builder: (context, value, child) {
        final at = (value - value.floor()) * (_steps.length - 1);
        final i = at.floor();
        final dx = _steps[i] + (_steps[(i + 1) % _steps.length] - _steps[i]) * (at - i);
        return Transform.translate(offset: Offset(dx, 0), child: child);
      },
    );
  }
}
