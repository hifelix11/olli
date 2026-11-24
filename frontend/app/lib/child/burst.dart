import 'dart:math' as math;

import 'package:flutter/widgets.dart';

import '../ui/tokens.dart';

const _colors = [Tokens.sun, Tokens.blue, Tokens.red, Tokens.pink];
const _size = 26.0;
const _curve = Cubic(0.2, 0.8, 0.3, 1);

/// Richtig! Ein Schwung Formen fliegt aus der Mitte der Tafel.
class Burst extends StatefulWidget {
  const Burst({super.key});

  @override
  State<Burst> createState() => _BurstState();
}

class _BurstState extends State<Burst> with SingleTickerProviderStateMixin {
  late final _fly = AnimationController(vsync: this, duration: const Duration(milliseconds: 800))
    ..forward();

  @override
  void dispose() {
    _fly.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (reducedMotion(context)) return const SizedBox();
    return IgnorePointer(
      child: ExcludeSemantics(child: CustomPaint(painter: _BurstPainter(_fly))),
    );
  }
}

class _BurstPainter extends CustomPainter {
  const _BurstPainter(this.fly) : super(repaint: fly);

  final Animation<double> fly;

  @override
  void paint(Canvas canvas, Size size) {
    final t = _curve.transform(fly.value);
    final fade = fly.value < 0.7 ? 1.0 : 1 - (fly.value - 0.7) / 0.3;
    // Zwölf Formen im Kreis, abwechselnd nah und fern.
    for (var i = 0; i < 12; i++) {
      final angle = i / 12 * 2 * math.pi + 0.2;
      final distance = i.isOdd ? 250.0 : 340.0;
      final paint = Paint()..color = _colors[i % 4].withValues(alpha: fade);
      canvas.save();
      canvas.translate(
        size.width / 2 + math.cos(angle) * distance * t,
        size.height / 2 + math.sin(angle) * distance * 0.6 * t,
      );
      canvas.rotate(i * 47 * math.pi / 180 * t);
      canvas.scale(0.3 + 0.7 * t);
      const box = Rect.fromLTWH(-_size / 2, -_size / 2, _size, _size);
      switch (i % 3) {
        case 0:
          canvas.drawOval(box, paint);
        case 1:
          canvas.drawRRect(RRect.fromRectAndRadius(box, const Radius.circular(4)), paint);
        default:
          final triangle = Path()
            ..moveTo(0, -_size / 2)
            ..lineTo(_size / 2, _size / 2)
            ..lineTo(-_size / 2, _size / 2)
            ..close();
          canvas.drawPath(triangle, paint);
      }
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(_BurstPainter old) => false;
}
