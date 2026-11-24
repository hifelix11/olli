import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

/// Augen auf einem 3×3-Raster, wie auf dem Spielwürfel.
const _pips = <int, List<(int, int)>>{
  1: [(1, 1)],
  2: [(0, 0), (2, 2)],
  3: [(0, 0), (1, 1), (2, 2)],
  4: [(0, 0), (2, 0), (0, 2), (2, 2)],
  5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
  6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)],
};

class Dice extends StatelessWidget {
  const Dice(this.n, {super.key});

  final int n;

  @override
  Widget build(BuildContext context) => Sketch(const Size(120, 120), label: 'Würfelbild', (canvas) {
    canvas.box(4, 4, 112, 112, Tokens.board, r: 18);
    canvas.box(4, 4, 112, 112, Tokens.ink, r: 18, outline: 3);
    for (final (column, row) in _pips[n] ?? const <(int, int)>[]) {
      canvas.dot(30 + column * 30, 30 + row * 30, 9, Tokens.ink);
    }
  });
}
