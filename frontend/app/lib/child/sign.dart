import 'dart:math' as math;

import 'package:flutter/widgets.dart';

import '../api/models.dart';
import '../ui/sketch.dart';
import '../ui/tokens.dart';

const _ink = Tokens.ink;
const _sun = Tokens.sun;
const _red = Tokens.red;
const _blue = Tokens.blue;
const _green = Tokens.green;
const _orange = Color(0xFFF08A3C);
const _violet = Color(0xFF7C5CF0);

const signNames = {
  Sign.sun: 'Sonne',
  Sign.moon: 'Mond',
  Sign.star: 'Stern',
  Sign.heart: 'Herz',
  Sign.fish: 'Fisch',
  Sign.apple: 'Apfel',
  Sign.flower: 'Blume',
  Sign.boat: 'Boot',
};

/// Vorschlag: das erste Zeichen, das noch kein Geschwisterkind hat.
Sign freeSign(Iterable<Sign> taken) =>
    Sign.values.where((s) => !taken.contains(s)).firstOrNull ?? Sign.values.first;

/// Jedes Zeichen hat sein Farbfeld, damit Geschwister sich auch an der Farbe unterscheiden.
const _tiles = {
  Sign.sun: Color(0xFFDCE5FF),
  Sign.moon: Color(0xFF2E2A66),
  Sign.star: Color(0xFFEAE3FF),
  Sign.heart: Color(0xFFFFDDD8),
  Sign.fish: Color(0xFFD4F1EC),
  Sign.apple: Color(0xFFE0F3D9),
  Sign.flower: Color(0xFFFFEFC4),
  Sign.boat: Color(0xFFFFE3CC),
};

/// Das Zeichen eines Kindes auf seinem Farbfeld.
class SignIcon extends StatelessWidget {
  const SignIcon(this.sign, {super.key, this.size = 48});

  final Sign sign;
  final double size;

  @override
  Widget build(BuildContext context) =>
      Sketch(const Size(24, 24), width: size, label: signNames[sign], (canvas) {
        canvas.box(0, 0, 24, 24, _tiles[sign]!, r: 7);
        _draw(canvas, sign);
      });
}

/// Kleines Gesicht wie bei Olli: zwei Punkte, ein Lächeln.
void _face(Canvas canvas, double cx, double cy, [Color color = _ink]) {
  canvas.dot(cx - 2, cy - 0.6, 0.85, color);
  canvas.dot(cx + 2, cy - 0.6, 0.85, color);
  canvas.stroke('M${cx - 1.3} ${cy + 1}q1.3 1.4 2.6 0', color, 0.8);
}

/// n Richtungen im Kreis, die erste nach oben.
Iterable<(double x, double y)> _around(int n) sync* {
  for (var i = 0; i < n; i++) {
    final a = 2 * math.pi * i / n - math.pi / 2;
    yield (math.cos(a), math.sin(a));
  }
}

void _draw(Canvas canvas, Sign sign) {
  switch (sign) {
    case Sign.sun:
      for (final (x, y) in _around(8)) {
        canvas.seg(12 + x * 6.8, 12 + y * 6.8, 12 + x * 9.2, 12 + y * 9.2, _sun, 1.9, round: true);
      }
      canvas.dot(12, 12, 5.2, _sun);
      _face(canvas, 12, 12);
    case Sign.moon:
      canvas.fill('M14.5 4.5A7.8 7.8 0 1 0 19.8 15A6.2 6.2 0 1 1 14.5 4.5Z', _sun);
      canvas.dot(10.2, 12.4, 0.85, _ink);
      canvas.stroke('M9.2 14.4q1.1 1.1 2.2 0', _ink, 0.8);
    case Sign.star:
      const star =
          'M12,3.6L14.4,9.2L20.4,9.6L15.8,13.5L17.3,19.4L12,16.2L6.7,19.4L8.2,13.5L3.6,9.6L9.6,9.2Z';
      canvas.fill(star, _sun);
      canvas.stroke(star, _sun, 1.6);
      _face(canvas, 12, 12.4);
    case Sign.heart:
      canvas.fill(
        'M12 20s-7.5-4.6-8.6-9.6A4.6 4.6 0 0 1 12 7a4.6 4.6 0 0 1 8.6 3.4C19.5 15.4 12 20 12 20z',
        _red,
      );
      _face(canvas, 12, 12.2, Tokens.white);
    case Sign.fish:
      canvas.fill('M15 12L21 7.4V16.6Z', _orange);
      canvas.oval(10, 12, 7, 5, _orange);
      canvas.dot(6.8, 11, 1.3, Tokens.white);
      canvas.dot(6.8, 11, 0.7, _ink);
    case Sign.apple:
      canvas.fill(
        'M12 8.6c-2-1.4-7.6-1.4-7.6 4.6 0 4 3 7.6 5 7.6 1 0 1.6-.5 2.6-.5s1.6.5 2.6.5c2 0 5-3.6 5-7.6 0-6-5.6-6-7.6-4.6z',
        _red,
      );
      canvas.stroke('M12 8.6V5', _ink, 1.4);
      canvas.fill('M12.6 5.6c1-2 3.2-2.6 4.8-2-.6 1.6-2.8 2.6-4.8 2z', _green);
    case Sign.flower:
      for (final (x, y) in _around(5)) {
        canvas.dot(12 + x * 4.8, 12 + y * 4.8, 3.6, _violet);
      }
      canvas.dot(12, 12, 3, _orange);
    case Sign.boat:
      canvas.stroke('M11.6 3.6V15', _ink, 1.4);
      canvas.fill('M12.8 4.4L19 13.6H12.8Z', _red);
      canvas.fill('M3 15.4H21L17.6 20.4H6.4Z', _blue);
  }
}
