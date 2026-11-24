import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

const _cell = Tokens.cell;
const _x0 = 36.0;
const _max = 10;

/// Zwei Stäbe A und B, linksbündig, Länge in Kästchen.
class Lengths extends StatelessWidget {
  const Lengths({super.key, required this.a, required this.b});

  final num a;
  final num b;

  @override
  Widget build(BuildContext context) =>
      Sketch(const Size(_x0 + _max * _cell + 8, 84), label: 'Zwei Stäbe A und B', (canvas) {
        void bar(String label, num value, double y) {
          canvas.label(label, 12, y + _cell / 2, size: 22, weight: FontWeight.w700, middle: true);
          canvas.box(_x0, y, value * _cell, _cell, Tokens.blue);
        }

        bar('A', a, 6);
        bar('B', b, 50);
      });
}

const _unit = 36.0;

/// Ein Stab, darunter n Büroklammern (oder eine andere Einheit) Stück an Stück.
class Units extends StatelessWidget {
  const Units({super.key, required this.n, required this.unit});

  final int n;
  final String unit;

  @override
  Widget build(BuildContext context) =>
      Sketch(Size(n * _unit + 16, 76), label: 'Ein Stab und $unit darunter', (canvas) {
        canvas.box(8, 8, n * _unit, 20, Tokens.blue);
        for (var i = 0; i < n; i++) {
          final cx = 8 + (i + 0.5) * _unit;
          canvas.oval(cx, 52, 16, 8, Tokens.ink, outline: 2.5);
          canvas.oval(cx, 52, 10, 4, Tokens.ink, outline: 1.5);
        }
      });
}

const _step = 24.0;

/// Ein Stab ab 0, darunter ein Lineal mit Zentimetern bis 20.
class Ruler extends StatelessWidget {
  const Ruler(this.n, {super.key});

  final num n;

  @override
  Widget build(BuildContext context) =>
      Sketch(const Size(520, 96), width: 600, label: 'Ein Stab über einem Lineal', (canvas) {
        canvas.box(16, 6, n * _step, 22, Tokens.blue);
        canvas.box(6, 38, 508, 52, Tokens.board);
        canvas.box(6, 38, 508, 52, Tokens.ink, outline: 2);
        for (var i = 0; i <= 20; i++) {
          final x = 16 + i * _step;
          final big = i % 5 == 0;
          canvas.seg(x, 38, x, big ? 56 : 49, Tokens.ink, big ? 2.5 : 1.5);
          canvas.label('$i', x, 80, size: 16);
        }
        canvas.label('cm', 510, 64, size: 13, color: Tokens.inkSoft, align: TextAlign.end);
      });
}
