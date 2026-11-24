import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';
import 'shapes.dart';

const _skin = Color(0xFFF6C49B);
const _blue = Tokens.blue;
const _ink = Tokens.ink;
final _light = Color.lerp(Tokens.white, _blue, 0.45)!;
final _dark = Color.lerp(const Color(0xFF000000), _blue, 0.7)!;

typedef _Draw = void Function(Canvas canvas);

/// Körper schräg von oben: die helle Fläche oben, die dunkle rechts.
final _solids = <String, _Draw>{
  'cube': (c) {
    c.poly('40,10 66,25 40,40 14,25', _light);
    c.poly('14,25 40,40 40,70 14,55', _blue);
    c.poly('40,40 66,25 66,55 40,70', _dark);
  },
  'cuboid': (c) {
    c.poly('30,45 68,23 50,12 12,34', _light);
    c.poly('12,34 30,45 30,69 12,58', _blue);
    c.poly('30,45 68,23 68,47 30,69', _dark);
  },
  'sphere': (c) {
    c.dot(40, 40, 30, _blue);
    c.dot(30, 29, 8, _light);
  },
  'cylinder': (c) {
    c.fill('M20 18 V62 A20 7 0 0 0 60 62 V18 Z', _blue);
    c.fill('M40 18 V69 A20 7 0 0 0 60 62 V18 Z', _dark);
    c.oval(40, 18, 20, 7, _light);
  },
  'cone': (c) {
    c.fill('M40 10 L18 62 A22 7 0 0 0 40 69 Z', _blue);
    c.fill('M40 10 L62 62 A22 7 0 0 1 40 69 Z', _dark);
  },
  'pyramid': (c) {
    c.poly('40,14 8,52 40,66', _blue);
    c.poly('40,14 40,66 72,52', _dark);
  },
};

void _shoulders(Canvas c) {
  c.fill('M12 80 C12 62 24 57 40 57 C56 57 68 62 68 80 Z', _blue);
  c.box(34, 44, 12, 16, _skin);
}

/// Kopf und Schultern. Von vorn mit Gesicht, von hinten nur Haare.
final _people = <String, _Draw>{
  'face': (c) {
    _shoulders(c);
    c.dot(40, 30, 20, _ink);
    c.oval(40, 36, 16, 15, _skin);
    c.dot(33, 35, 2.6, _ink);
    c.dot(47, 35, 2.6, _ink);
    c.stroke('M34 42 Q40 47 46 42', _ink, 2.6);
  },
  'back': (c) {
    _shoulders(c);
    c.dot(20, 35, 5, _skin);
    c.dot(60, 35, 5, _skin);
    c.dot(40, 30, 20, _ink);
  },
  'feet': (c) {
    c.box(18, 6, 14, 50, Tokens.inkSoft);
    c.box(48, 6, 14, 50, Tokens.inkSoft);
    c.fill('M8 72 C8 58 16 52 25 52 C34 52 38 58 38 72 Z', _blue);
    c.fill('M42 72 C42 58 46 52 55 52 C64 52 72 58 72 72 Z', _blue);
    c.box(6, 70, 34, 6, _ink, r: 3);
    c.box(40, 70, 34, 6, _ink, r: 3);
  },
};

const _check = 'M16 42 L32 58 L64 24';
const _cross = 'M22 22 L58 58 M58 22 L22 58';

/// Haken, Kreuz und Pfeile als dicke Striche.
const _signs = {
  'yes': _check,
  'correct': _check,
  'no': _cross,
  'incorrect': _cross,
  'left': 'M64 40 H16 M34 22 L16 40 L34 58',
  'right': 'M16 40 H64 M46 22 L64 40 L46 58',
};

const _colors = {'red': Tokens.red, 'blue': Tokens.blue, 'green': Tokens.green};

final _two = RegExp(r'^two_(\w+)s$');

/// Bild zu einer Antwort, gefunden über ihren Wert ("circle", "two_triangles", "sphere", "yes").
/// null, wenn es keins gibt. Ein Erstklässler liest noch nicht: Bild und Wort zusammen.
Widget? optionPicture(Object value, double size) {
  if (value is! String) return null;
  Widget picture(_Draw draw) => Sketch(const Size(80, 80), draw, width: size);

  final two = _two.firstMatch(value)?.group(1);
  final shape = two ?? value;
  if (shapeIds.contains(shape)) {
    final one = picture((c) => drawShape(c, shape));
    if (two == null) return one;
    // Zwei Formen rücken zusammen.
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        one,
        Transform.translate(offset: const Offset(-4, 0), child: one),
      ],
    );
  }
  final sign = _signs[value];
  final color = _colors[value];
  final draw =
      _solids[value] ??
      _people[value] ??
      (sign != null ? (Canvas c) => c.stroke(sign, _ink, 8) : null) ??
      (color != null ? (Canvas c) => c.dot(40, 40, 30, color) : null);
  return draw == null ? null : picture(draw);
}
