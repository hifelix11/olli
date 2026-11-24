import 'dart:math' as math;

import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

/// Der Stempel am Ende jeder Sitzung, mit Wellenrand wie ein Aufkleber.
/// Blau mit Gesicht für eine geschaffte Sitzung, rot mit Stern, wenn etwas Neues sitzt.
class Stamp extends StatelessWidget {
  const Stamp({super.key, required this.special, this.size = 184});

  final bool special;
  final double size;

  @override
  Widget build(BuildContext context) {
    final stamp = Transform.rotate(
      angle: -8 * math.pi / 180,
      child: Sketch(
        const Size(120, 120),
        width: size,
        label: special ? 'Stempel mit Stern' : 'Stempel',
        (canvas) => _draw(canvas, special),
      ),
    );
    if (reducedMotion(context)) return stamp;
    // Der Stempel fällt: groß und blass, dann sitzt er.
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 450),
      curve: const Cubic(0.3, 1.4, 0.5, 1),
      child: stamp,
      builder: (context, t, child) => Opacity(
        opacity: t.clamp(0, 1),
        child: Transform.scale(scale: 1.8 - 0.8 * t, child: child),
      ),
    );
  }
}

void _draw(Canvas canvas, bool special) {
  final color = special ? Tokens.red : Tokens.blue;
  canvas.dot(60, 60, 46, color);
  for (var i = 0; i < 12; i++) {
    final a = 2 * math.pi * i / 12;
    canvas.dot(60 + 44 * math.cos(a), 60 + 44 * math.sin(a), 13, color);
  }
  if (special) {
    const star =
        'M60,30L67.6,49.6L88.5,50.7L72.3,63.9L77.6,84.3L60,72.9L42.4,84.3L47.7,63.9L31.5,50.7L52.4,49.6Z';
    canvas.fill(star, Tokens.white);
    canvas.stroke(star, Tokens.white, 4);
  } else {
    canvas.dot(47, 52, 6, Tokens.white);
    canvas.dot(73, 52, 6, Tokens.white);
    canvas.fill('M42 66q18 22 36 0Z', Tokens.white);
    canvas.stroke('M42 66q18 22 36 0Z', Tokens.white, 3);
  }
}
