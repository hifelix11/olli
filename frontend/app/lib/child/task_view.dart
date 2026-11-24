import 'package:flutter/widgets.dart';

import '../api/models.dart';
import '../representations/figure.dart';
import '../representations/option_picture.dart';
import '../ui/controls.dart';
import '../ui/icons.dart';
import '../ui/sketch.dart';
import '../ui/tokens.dart';
import 'burst.dart';
import 'keypad.dart';

/// Trennt die Frage ("Welche Zahl fehlt?") von der Rechnung ("2, 3, 4, _").
({String question, String figure}) splitPrompt(String prompt) {
  final q = prompt.indexOf('? ');
  if (q >= 0) return (question: prompt.substring(0, q + 1), figure: prompt.substring(q + 2));
  final c = prompt.indexOf(': ');
  if (c >= 0) return (question: prompt.substring(0, c + 1), figure: prompt.substring(c + 2));
  if (prompt.contains('_') || prompt.endsWith('= ?')) return (question: '', figure: prompt);
  return (question: prompt, figure: '');
}

/// Zerlegt die Rechnung an der Lücke, damit die Eingabe mitten in der Zeile steht.
(String before, String after)? aroundGap(String figure) {
  final i = figure.indexOf('_');
  if (i >= 0) return (figure.substring(0, i), figure.substring(i + 1));
  if (figure.endsWith('= ?')) return (figure.substring(0, figure.length - 1), '');
  return null;
}

/// Die Tafel: Frage, Rechnung mit Lücke, Bild.
class TaskBoard extends StatelessWidget {
  const TaskBoard({
    super.key,
    required this.task,
    required this.shown,
    required this.revealed,
    required this.cheer,
  });

  final Task task;

  /// Steht in der Lücke: getippte Ziffern, die gewählte Antwort oder die Lösung.
  final String shown;

  /// Die Lösung ist da: Leere Plättchen füllen sich.
  final bool revealed;

  /// Richtig: Formen fliegen aus der Tafel.
  final bool cheer;

  @override
  Widget build(BuildContext context) {
    final compact = isCompact(context);
    final (:question, :figure) = splitPrompt(task.prompt);
    final gap = aroundGap(figure);
    // Lange Rechnungen ("1 Zehner und 4 Einer") kleiner.
    final size = figure.length > 14 ? (compact ? 30.0 : 40.0) : (compact ? 54.0 : 76.0);
    final numbers = jost(
      size,
      FontWeight.w700,
      height: 1.1,
    ).copyWith(fontFeatures: const [FontFeature.tabularFigures()]);
    final gapBox = _GapBox(shown, style: numbers);
    final picture = figureFor(task, revealed: revealed);

    Widget line(List<Widget> parts) => Wrap(
      alignment: WrapAlignment.center,
      crossAxisAlignment: WrapCrossAlignment.center,
      spacing: 0.22 * size,
      runSpacing: 0.1 * size,
      children: parts,
    );

    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          width: double.infinity,
          padding: compact
              ? const EdgeInsets.fromLTRB(16, 24, 16, 28)
              : const EdgeInsets.fromLTRB(28, 32, 28, 36),
          decoration: BoxDecoration(
            color: Tokens.board,
            borderRadius: BorderRadius.circular(compact ? 28 : 36),
          ),
          child: Column(
            spacing: compact ? 20 : 28,
            children: [
              if (question.isNotEmpty)
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 460),
                  child: Text(
                    question,
                    textAlign: TextAlign.center,
                    style: jost(
                      compact || question.length > 40 ? 23 : 28,
                      FontWeight.w600,
                      height: 1.25,
                    ),
                  ),
                ),
              if (figure.isNotEmpty)
                DefaultTextStyle.merge(
                  style: numbers,
                  child: line([
                    if (gap == null)
                      Text(figure)
                    else ...[
                      if (gap.$1.trim().isNotEmpty) Text(gap.$1.trim()),
                      gapBox,
                      if (gap.$2.trim().isNotEmpty) Text(gap.$2.trim()),
                    ],
                  ]),
                ),
              ?picture,
              if (figure.isEmpty && task.options == null) gapBox,
            ],
          ),
        ),
        if (cheer) const Positioned.fill(child: Burst()),
      ],
    );
  }
}

/// Die Lücke in der Rechnung. Leer ist sie gestrichelt und hellblau.
class _GapBox extends StatelessWidget {
  const _GapBox(this.shown, {required this.style});

  final String shown;
  final TextStyle style;

  @override
  Widget build(BuildContext context) {
    final size = style.fontSize!;
    final content = ConstrainedBox(
      constraints: BoxConstraints(minWidth: 1.35 * size),
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: 0.14 * size + 5, vertical: 0.04 * size + 5),
        child: Text(
          shown.isEmpty ? ' ' : shown,
          textAlign: TextAlign.center,
          style: style.copyWith(color: Tokens.blue),
        ),
      ),
    );
    return Semantics(
      label: 'Lücke',
      child: shown.isEmpty
          ? DashedBorder(
              color: Tokens.blue,
              width: 5,
              radius: 22,
              fill: Tokens.blueSoft,
              child: content,
            )
          : DecoratedBox(
              decoration: BoxDecoration(
                border: Border.all(color: Tokens.blue, width: 5),
                borderRadius: BorderRadius.circular(22),
              ),
              child: content,
            ),
    );
  }
}

/// Antworten unter der Tafel. Antworten geht immer gleich: Zahl tippen oder Antwort antippen,
/// ändern geht, erst der gelbe Haken prüft. Nur "Weiß ich noch nicht" zählt sofort.
class TaskInput extends StatelessWidget {
  const TaskInput({
    super.key,
    required this.task,
    required this.value,
    required this.onChange,
    required this.onSubmit,
    required this.closed,
    required this.canSkip,
    required this.busy,
    required this.onNext,
  });

  final Task task;
  final String value;
  final ValueChanged<String> onChange;

  /// null: "Weiß ich noch nicht".
  final ValueChanged<Object?> onSubmit;

  /// Beantwortet: keine Eingabe mehr.
  final bool closed;

  /// Nur im Standortcheck.
  final bool canSkip;
  final bool busy;

  /// Pfeil nach einer falschen Antwort. Sonst geht es von selbst weiter.
  final VoidCallback? onNext;

  @override
  Widget build(BuildContext context) {
    final compact = isCompact(context);
    final options = task.options;
    final onNext = this.onNext;
    return Column(
      spacing: 16,
      children: [
        if (!closed && options != null) _choice(options, compact),
        if (!closed && options == null)
          Keypad(
            layout: KeypadLayout.row,
            value: value,
            onChange: onChange,
            onSubmit: () => onSubmit(int.parse(value)),
            disabled: busy,
          ),
        if (!closed && canSkip) _skip(),
        if (onNext != null) RoundButton(IconName.next, onTap: onNext, label: 'Weiter'),
      ],
    );
  }

  /// Auswahl und Haken in einer Reihe, der Haken rechts wie beim Zahlenblock.
  Widget _choice(List<Option> options, bool compact) {
    final pictureSize = compact ? 48.0 : 64.0;
    // Bild und Wort, wenn jede Antwort ein Bild hat. Nicht beim Benennen: Das Bild auf der Tafel ist die Frage.
    final pictures = task.kind == 'shape_name'
        ? const <Widget?>[]
        : [for (final o in options) optionPicture(o.value, pictureSize)];
    final withPictures = pictures.isNotEmpty && !pictures.contains(null);
    // Lange Antworten ("Wie viele Kinder sind es jetzt?") untereinander.
    final stacked = !withPictures && options.any((o) => o.label.length > 12);
    final selected = options.where((o) => '${o.value}' == value).firstOrNull;

    Widget button(int i) {
      final option = options[i];
      return Tap(
        onTap: busy ? null : () => onChange('${option.value}'),
        radius: 24,
        builder: (pressed) => Container(
          constraints: BoxConstraints(
            minWidth: withPictures ? (compact ? 100 : 132) : 104,
            minHeight: stacked ? 68 : 80,
          ),
          padding: withPictures
              ? (compact
                    ? const EdgeInsets.fromLTRB(12, 10, 12, 8)
                    : const EdgeInsets.fromLTRB(20, 14, 20, 12))
              : EdgeInsets.symmetric(horizontal: 24, vertical: stacked ? 12 : 0),
          decoration: BoxDecoration(
            color: !pressed
                ? Tokens.board
                : withPictures
                ? Tokens.blueSoft
                : Tokens.blue,
            borderRadius: BorderRadius.circular(24),
          ),
          // Gewählt, noch nicht bestätigt: blauer Rand wie die gefüllte Lücke.
          foregroundDecoration: option == selected
              ? BoxDecoration(
                  border: Border.all(color: Tokens.blue, width: 5),
                  borderRadius: BorderRadius.circular(24),
                )
              : null,
          child: Center(
            widthFactor: 1,
            heightFactor: 1,
            child: withPictures
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    spacing: 4,
                    children: [
                      pictures[i]!,
                      Text(
                        option.label,
                        style: jost(compact ? 18 : 22, FontWeight.w700, height: 1.2),
                      ),
                    ],
                  )
                : Text(
                    option.label,
                    textAlign: TextAlign.center,
                    style: jost(
                      stacked ? 22 : 32,
                      FontWeight.w700,
                      height: 1.3,
                      color: pressed ? Tokens.white : Tokens.ink,
                    ),
                  ),
          ),
        ),
      );
    }

    final buttons = [for (var i = 0; i < options.length; i++) button(i)];
    return Wrap(
      alignment: WrapAlignment.center,
      crossAxisAlignment: WrapCrossAlignment.center,
      spacing: 24,
      runSpacing: 16,
      children: [
        if (stacked)
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              spacing: 12,
              children: buttons,
            ),
          )
        else
          Wrap(alignment: WrapAlignment.center, spacing: 12, runSpacing: 12, children: buttons),
        RoundButton(
          IconName.check,
          onTap: busy || selected == null ? null : () => onSubmit(selected.value),
          label: 'Fertig',
        ),
      ],
    );
  }

  Widget _skip() => Tap(
    onTap: busy ? null : () => onSubmit(null),
    builder: (_) => Container(
      padding: const EdgeInsets.fromLTRB(6, 6, 22, 6),
      decoration: BoxDecoration(color: Tokens.board, borderRadius: BorderRadius.circular(999)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        spacing: 12,
        children: [
          Container(
            width: 44,
            height: 44,
            alignment: Alignment.center,
            decoration: const BoxDecoration(color: Tokens.pink, shape: BoxShape.circle),
            child: ExcludeSemantics(
              child: Text('?', style: jost(26, FontWeight.w800, color: Tokens.ink, height: 1)),
            ),
          ),
          Flexible(
            child: Text(
              'Weiß ich noch nicht',
              style: jost(18, FontWeight.w600, color: Tokens.inkSoft),
            ),
          ),
        ],
      ),
    ),
  );
}
