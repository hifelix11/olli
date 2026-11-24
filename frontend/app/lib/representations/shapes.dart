import 'dart:math';

import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

/// Ecken eines regelmäßigen Vielecks um (40, 40), erste Ecke oben.
String _regular(int sides, double r) => [
  for (var i = 0; i < sides; i++)
    '${40 + r * cos(-pi / 2 + i * 2 * pi / sides)},${40 + r * sin(-pi / 2 + i * 2 * pi / sides)}',
].join(' ');

/// Formen, die [drawShape] zeichnen kann.
const shapeIds = {
  'circle',
  'semicircle',
  'triangle',
  'square',
  'rectangle',
  'quadrilateral',
  'pentagon',
  'hexagon',
};

/// Eine Form in einem Feld von 80 mal 80, gedreht um die Mitte.
void drawShape(Canvas canvas, String id, {num rotation = 0}) {
  const fill = Tokens.blue;
  canvas.turned(rotation.toDouble(), 40, 40, () {
    switch (id) {
      case 'circle':
        canvas.dot(40, 40, 30, fill);
      case 'square':
        canvas.box(14, 14, 52, 52, fill);
      case 'rectangle':
        canvas.box(6, 22, 68, 36, fill);
      case 'semicircle':
        canvas.fill('M8 56 A32 32 0 0 1 72 56 Z', fill);
      case 'triangle':
        canvas.poly('40,8 70,66 10,66', fill);
      case 'quadrilateral':
        canvas.poly('22,12 66,18 72,66 8,60', fill);
      case 'pentagon':
        canvas.poly(_regular(5, 32), fill);
      case 'hexagon':
        canvas.poly(_regular(6, 32), fill);
    }
  });
}

/// Eine Reihe Formen, jede in ihrem Kästchen. `_` ist eine Lücke mit Fragezeichen.
class Shapes extends StatelessWidget {
  const Shapes({super.key, required this.shapes, required this.rotation});

  /// IDs mit Leerzeichen getrennt, etwa "circle square _".
  final String shapes;
  final num rotation;

  @override
  Widget build(BuildContext context) {
    final ids = shapes.split(' ').where((id) => id.isNotEmpty).toList();
    return Semantics(
      label: ids.length == 1 ? 'Eine Form' : 'Eine Reihe aus Formen',
      image: true,
      child: Wrap(
        alignment: WrapAlignment.center,
        spacing: 10,
        runSpacing: 10,
        children: [
          for (final id in ids)
            if (id == '_')
              DashedBorder(
                color: Tokens.blue,
                width: 4,
                radius: 18,
                fill: Tokens.blueSoft,
                child: SizedBox.square(
                  dimension: 76,
                  child: Center(
                    child: Text(
                      '?',
                      style: jost(38, FontWeight.w700, color: Tokens.blue, height: 1),
                    ),
                  ),
                ),
              )
            else
              Sketch(
                const Size(80, 80),
                width: 76,
                (canvas) => drawShape(canvas, id, rotation: rotation),
              ),
        ],
      ),
    );
  }
}
