import 'dart:math';

import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

const _columns = 5;
const _rows = 4;
const _slot = 56.0;
const _radius = 16.0;
const _jitter = 10.0; // Nachbarplätze bleiben mindestens 36 auseinander, Plättchen sind 32 breit

/// n Plättchen ungeordnet in einem Kasten. Der Startwert hält sie bei jedem Zeichnen am selben Platz.
class Scattered extends StatelessWidget {
  const Scattered(this.n, {super.key, required this.seed});

  final int n;
  final int seed;

  @override
  Widget build(BuildContext context) {
    final random = Random(seed);
    final slots = List.generate(_columns * _rows, (i) => i)..shuffle(random);
    double shift() => (random.nextDouble() * 2 - 1) * _jitter;
    final points = [
      for (final slot in slots.take(n))
        Offset(
          (slot % _columns) * _slot + _slot / 2 + shift(),
          (slot ~/ _columns) * _slot + _slot / 2 + shift(),
        ),
    ];
    return Sketch(const Size(_columns * _slot, _rows * _slot), label: 'Verstreute Plättchen', (
      canvas,
    ) {
      for (final point in points) {
        canvas.dot(point.dx, point.dy, _radius, Tokens.blue);
      }
    });
  }
}
