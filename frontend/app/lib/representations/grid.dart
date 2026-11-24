import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

const _cell = Tokens.cell;

typedef _Point = (num x, num y);

_Point _point(String text) {
  final parts = text.split(',');
  return (num.parse(parts[0]), num.parse(parts[1]));
}

/// Punkte wie "0,0 1,0 1,1".
List<_Point> _points(String text) => [
  for (final p in text.split(' '))
    if (p.isNotEmpty) _point(p),
];

/// Buchstaben auf Kästchen wie "A:0,1 B:2,3".
List<(String, _Point)> _marks(String text) => [
  for (final m in text.split(' '))
    if (m.isNotEmpty) (m.split(':')[0], _point(m.split(':')[1])),
];

/// Gitterfigur: gefüllte Kästchen, Spiegelachse, Startpunkt, Buchstaben.
/// Mit `copy` steht daneben eine zweite Figur.
class Grid extends StatelessWidget {
  const Grid({
    super.key,
    required this.width,
    required this.height,
    required this.cells,
    required this.copy,
    required this.axis,
    required this.start,
    required this.marks,
  });

  final int width;
  final int height;
  final String cells;
  final String copy;
  final String axis;
  final String start;
  final String marks;

  @override
  Widget build(BuildContext context) {
    final template = _cells(
      _points(cells),
      axis: axis,
      start: _points(start).firstOrNull,
      marks: _marks(marks),
    );
    if (copy.isEmpty) return Semantics(label: 'Gitter', image: true, child: template);

    Widget named(Widget grid, String name) => Column(
      mainAxisSize: MainAxisSize.min,
      spacing: 6,
      children: [
        grid,
        Text(name, style: const TextStyle(fontWeight: FontWeight.w600)),
      ],
    );
    return Semantics(
      label: 'Vorlage und Kopie im Gitter',
      image: true,
      child: Wrap(
        alignment: WrapAlignment.center,
        spacing: 24,
        runSpacing: 24,
        children: [named(template, 'Vorlage'), named(_cells(_points(copy)), 'Kopie')],
      ),
    );
  }

  /// Ein Gitter. x nach rechts, y nach unten, Zeile 0 oben.
  Widget _cells(
    List<_Point> filled, {
    String axis = '',
    _Point? start,
    List<(String, _Point)> marks = const [],
  }) {
    final w = width * _cell;
    final h = height * _cell;
    return Sketch(Size(w + 4, h + 4), (canvas) {
      canvas.translate(2, 2);
      canvas.box(0, 0, w, h, Tokens.board);
      for (final (x, y) in filled) {
        canvas.box(x * _cell, y * _cell, _cell, _cell, Tokens.blue);
      }
      for (var i = 0; i <= width; i++) {
        canvas.seg(i * _cell, 0, i * _cell, h, Tokens.inkSoft, 1);
      }
      for (var i = 0; i <= height; i++) {
        canvas.seg(0, i * _cell, w, i * _cell, Tokens.inkSoft, 1);
      }
      canvas.box(0, 0, w, h, Tokens.ink, outline: 2);
      if (axis == 'vertical') {
        final line = Path()
          ..moveTo(w / 2, -2)
          ..lineTo(w / 2, h + 2);
        canvas.drawPath(
          dashed(line, 6, 5),
          Paint()
            ..color = Tokens.red
            ..style = PaintingStyle.stroke
            ..strokeWidth = 3,
        );
      }
      if (start != null) {
        canvas.dot((start.$1 + 0.5) * _cell, (start.$2 + 0.5) * _cell, 9, Tokens.red);
      }
      for (final (label, (x, y)) in marks) {
        canvas.label(
          label,
          (x + 0.5) * _cell,
          (y + 0.5) * _cell,
          size: 18,
          weight: FontWeight.w700,
          middle: true,
        );
      }
    });
  }
}
