import 'dart:math';

import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

const _c = 100.0;

/// Punkt auf dem Zifferblatt: Winkel ab 12 Uhr im Uhrzeigersinn, Abstand r von der Mitte.
(double x, double y) _point(double angle, double r) => (_c + r * sin(angle), _c - r * cos(angle));

/// Analoguhr. Der Stundenzeiger wandert mit den Minuten weiter, bei halb steht er in der Mitte.
class Clock extends StatelessWidget {
  const Clock({super.key, required this.hour, required this.minute});

  final int hour;
  final int minute;

  @override
  Widget build(BuildContext context) => Sketch(const Size(200, 200), label: 'Uhr', (canvas) {
    canvas.dot(_c, _c, 92, Tokens.board);
    canvas.ring(_c, _c, 92, Tokens.ink, 3);
    for (var i = 1; i <= 12; i++) {
      final angle = i / 12 * 2 * pi;
      final (inX, inY) = _point(angle, 85);
      final (outX, outY) = _point(angle, 92);
      final (labelX, labelY) = _point(angle, 74);
      canvas.seg(inX, inY, outX, outY, Tokens.ink, 3);
      canvas.label('$i', labelX, labelY, size: 18, weight: FontWeight.w700, middle: true);
    }
    final (hourX, hourY) = _point((hour % 12 + minute / 60) / 12 * 2 * pi, 48);
    final (minuteX, minuteY) = _point(minute / 60 * 2 * pi, 70);
    canvas.seg(_c, _c, hourX, hourY, Tokens.ink, 7, round: true);
    canvas.seg(_c, _c, minuteX, minuteY, Tokens.ink, 4, round: true);
    canvas.dot(_c, _c, 5, Tokens.ink);
  });
}

/// Digitaluhr, zwölf Stunden: 3:30, 11:00.
class DigitalClock extends StatelessWidget {
  const DigitalClock({super.key, required this.hour, required this.minute});

  final int hour;
  final int minute;

  @override
  Widget build(BuildContext context) {
    final size = isCompact(context) ? 46.0 : 60.0;
    return Semantics(
      label: 'Digitaluhr',
      image: true,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 10),
        decoration: BoxDecoration(color: Tokens.ink, borderRadius: BorderRadius.circular(24)),
        child: Text(
          '$hour:${'$minute'.padLeft(2, '0')}',
          style: jost(
            size,
            FontWeight.w700,
            color: Tokens.white,
            height: 1.45,
            spacing: 0.04 * size,
          ).copyWith(fontFeatures: const [FontFeature.tabularFigures()]),
        ),
      ),
    );
  }
}
