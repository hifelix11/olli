import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

const _step = 28.0;
const _x0 = 20.0;
const _y = 46.0;

/// Zahlenstrahl von 0 bis 20, ein roter Pfeil zeigt auf n. Die Zahl an n steht nicht dran.
class NumberLine extends StatelessWidget {
  const NumberLine(this.n, {super.key});

  final num n;

  @override
  Widget build(BuildContext context) =>
      Sketch(const Size(600, 84), label: 'Zahlenstrahl von 0 bis 20 mit einem Pfeil', (canvas) {
        canvas.seg(_x0, _y, _x0 + 20 * _step, _y, Tokens.ink, 3);
        for (var i = 0; i <= 20; i++) {
          final x = _x0 + i * _step;
          final big = i % 5 == 0;
          final length = big ? 11.0 : 6.0;
          canvas.seg(x, _y - length, x, _y + length, Tokens.ink, big ? 3 : 2);
          if (big) canvas.label('$i', x, _y + 34, size: 22, weight: FontWeight.w700);
        }
        final x = _x0 + n * _step;
        canvas.poly('$x,${_y - 13} ${x - 10},${_y - 32} ${x + 10},${_y - 32}', Tokens.red);
      });
}
