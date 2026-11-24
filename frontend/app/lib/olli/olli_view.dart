import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

enum Mood { neutral, happy, thinking }

const _fur = Color(0xFFF08A3C);
const _dark = Color(0xFFD9702A);
const _cream = Color(0xFFFFE6CC);
const _cheek = Color(0xFFFF9EC4);
const _ink = Tokens.ink;

/// Olli, der Otter: ein runder Kiesel mit kleinen Ohren, heller Schnauze und Schnurrhaaren.
/// Wird Olli fröhlich, hüpft er einmal.
class OlliView extends StatefulWidget {
  const OlliView({super.key, this.mood = Mood.neutral, this.size = 72});

  final Mood mood;
  final double size;

  @override
  State<OlliView> createState() => _OlliViewState();
}

class _OlliViewState extends State<OlliView> with SingleTickerProviderStateMixin {
  late final _hop = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));

  @override
  void initState() {
    super.initState();
    if (widget.mood == Mood.happy) _hop.forward();
  }

  @override
  void didUpdateWidget(OlliView old) {
    super.didUpdateWidget(old);
    if (widget.mood == Mood.happy && old.mood != Mood.happy) _hop.forward(from: 0);
  }

  @override
  void dispose() {
    _hop.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final picture = Sketch(
      const Size(120, 120),
      (canvas) => _draw(canvas, widget.mood),
      width: widget.size,
      label: 'Olli',
    );
    if (reducedMotion(context)) return picture;
    return AnimatedBuilder(
      animation: _hop,
      child: picture,
      builder: (context, child) {
        final (dy, sx, sy) = _hopAt(_hop.value);
        return Transform.translate(
          offset: Offset(0, dy),
          child: Transform.scale(
            scaleX: sx,
            scaleY: sy,
            alignment: Alignment.bottomCenter,
            child: child,
          ),
        );
      },
    );
  }
}

/// Hüpfer: hoch und gestreckt, landen und gestaucht, zurück zur Ruhe.
(double dy, double sx, double sy) _hopAt(double t) {
  double between(double from, double to, double a, double b) =>
      a + (b - a) * Curves.easeOut.transform(((t - from) / (to - from)).clamp(0, 1));
  if (t < 0.3) return (between(0, 0.3, 0, -14), between(0, 0.3, 1, 0.95), between(0, 0.3, 1, 1.06));
  if (t < 0.6) {
    return (
      between(0.3, 0.6, -14, 0),
      between(0.3, 0.6, 0.95, 1.06),
      between(0.3, 0.6, 1.06, 0.94),
    );
  }
  return (0, between(0.6, 1, 1.06, 1), between(0.6, 1, 0.94, 1));
}

void _draw(Canvas canvas, Mood mood) {
  final happy = mood == Mood.happy;
  final thinking = mood == Mood.thinking;

  // Ohren
  for (final x in [24.0, 96.0]) {
    canvas.dot(x, 40, 9, _fur);
    canvas.dot(x, 40, 4, _dark);
  }
  // Arme: hoch beim Jubeln, sonst am Körper.
  if (happy) {
    canvas.turned(-30, 11, 65, () => canvas.box(3, 50, 16, 30, _dark, r: 8));
    canvas.turned(30, 109, 65, () => canvas.box(101, 50, 16, 30, _dark, r: 8));
  } else {
    canvas.turned(16, 17, 90, () => canvas.box(9, 76, 16, 28, _dark, r: 8));
    canvas.turned(-16, 103, 90, () => canvas.box(95, 76, 16, 28, _dark, r: 8));
  }
  // Körper, Bauch, Schnauze
  canvas.fill(
    'M60 22C90 22 106 40 107 68C108 98 90 116 60 116C30 116 12 98 13 68C14 40 30 22 60 22Z',
    _fur,
  );
  canvas.oval(60, 104, 24, 10, _cream);
  canvas.oval(60, 71, 27, 16, _cream);
  canvas.stroke('M36 70l-14-3M36 75l-14 2M84 70l14-3M84 75l14 2', _ink.withValues(alpha: 0.7), 2.2);
  // Augen
  if (happy) {
    canvas.oval(34, 60, 6, 3.6, _cheek);
    canvas.oval(86, 60, 6, 3.6, _cheek);
    canvas.stroke('M40 55q6-8 12 0', _ink, 4);
    canvas.stroke('M68 55q6-8 12 0', _ink, 4);
  } else {
    // Beim Nachdenken schaut Olli nach oben rechts.
    final (dx, dy) = thinking ? (1.5, -2.0) : (0.0, 0.0);
    for (final x in [46.0, 74.0]) {
      canvas.dot(x + dx, 52 + dy, 5.5, _ink);
      canvas.dot(x + 2 + dx, 50 + dy, 1.8, Tokens.white);
    }
  }
  if (thinking) canvas.stroke('M67 40l13-4', _ink, 3.5);
  // Nase und Mund
  canvas.oval(60, 64, 7.5, 5, _ink);
  if (happy) {
    canvas.fill('M51 71q9 13 18 0Z', _ink);
    canvas.stroke('M51 71q9 13 18 0Z', _ink, 2);
  } else if (thinking) {
    canvas.dot(61, 75, 3, _ink);
  } else {
    canvas.stroke('M52 71q4 5 8 0q4 5 8 0', _ink, 3);
  }
}
