import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

/// Münzen und Scheine in einer Reihe. Ab 5 € ist es ein Schein.
class Money extends StatelessWidget {
  const Money({super.key, required this.coins, required this.unit});

  /// Werte mit Leerzeichen getrennt, etwa "2 1 1".
  final String coins;
  final String unit;

  @override
  Widget build(BuildContext context) {
    final values = coins.split(' ').where((v) => v.isNotEmpty).map(num.parse);
    return Semantics(
      label: 'Münzen und Scheine',
      image: true,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 440),
        child: Wrap(
          alignment: WrapAlignment.center,
          crossAxisAlignment: WrapCrossAlignment.center,
          spacing: 10,
          runSpacing: 10,
          children: [
            for (final value in values) unit == '€' && value >= 5 ? _note(value) : _coin(value),
          ],
        ),
      ),
    );
  }

  Widget _coin(num value) => Sketch(const Size(64, 64), (canvas) {
    canvas.dot(32, 32, 29, Tokens.sunSoft);
    canvas.ring(32, 32, 29, Tokens.ink, 3);
    canvas.ring(32, 32, 23, Tokens.ink, 1);
    canvas.label('$value $unit', 32, 32, size: 16, weight: FontWeight.w700, middle: true);
  });

  Widget _note(num value) => Sketch(const Size(100, 56), (canvas) {
    canvas.box(2, 2, 96, 52, Tokens.blueSoft, r: 6);
    canvas.box(2, 2, 96, 52, Tokens.ink, r: 6, outline: 3);
    canvas.box(10, 10, 80, 36, Tokens.ink, outline: 1);
    canvas.label('$value €', 50, 28, size: 20, weight: FontWeight.w700, middle: true);
  });
}
