import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:path_parsing/path_parsing.dart';

import 'tokens.dart';

final _paths = <String, Path>{};

/// Pfad aus SVG-Pfaddaten, etwa "M4.5 12.5l5 5L19.5 7".
Path svgPath(String data) => _paths[data] ??= _parse(data);

Path _parse(String data) {
  final proxy = _Proxy();
  writeSvgPathDataToPath(data, proxy);
  return proxy.path;
}

class _Proxy extends PathProxy {
  final path = Path();

  @override
  void moveTo(double x, double y) => path.moveTo(x, y);

  @override
  void lineTo(double x, double y) => path.lineTo(x, y);

  @override
  void cubicTo(double x1, double y1, double x2, double y2, double x3, double y3) =>
      path.cubicTo(x1, y1, x2, y2, x3, y3);

  @override
  void close() => path.close();
}

/// Gestrichelte Fassung eines Pfads.
Path dashed(Path source, double dash, double gap) {
  final out = Path();
  for (final metric in source.computeMetrics()) {
    for (var at = 0.0; at < metric.length; at += dash + gap) {
      out.addPath(metric.extractPath(at, math.min(at + dash, metric.length)), Offset.zero);
    }
  }
  return out;
}

Paint _line(Color color, double width, bool round) => Paint()
  ..color = color
  ..style = PaintingStyle.stroke
  ..strokeWidth = width
  ..strokeCap = round ? StrokeCap.round : StrokeCap.butt
  ..strokeJoin = round ? StrokeJoin.round : StrokeJoin.miter;

/// Kurze Befehle zum Zeichnen. Koordinaten wie in einem SVG: x nach rechts, y nach unten.
extension Pen on Canvas {
  void fill(String path, Color color) => drawPath(svgPath(path), Paint()..color = color);

  void stroke(String path, Color color, double width, {bool round = true}) =>
      drawPath(svgPath(path), _line(color, width, round));

  /// Vieleck aus Punkten wie "40,10 66,25 40,40".
  void poly(String points, Color color) => fill('M${points.replaceAll(' ', 'L')}Z', color);

  void dot(double cx, double cy, double r, Color color) =>
      drawCircle(Offset(cx, cy), r, Paint()..color = color);

  void ring(double cx, double cy, double r, Color color, double width) =>
      drawCircle(Offset(cx, cy), r, _line(color, width, false));

  void oval(double cx, double cy, double rx, double ry, Color color, {double? outline}) => drawOval(
    Rect.fromCenter(center: Offset(cx, cy), width: 2 * rx, height: 2 * ry),
    outline == null ? (Paint()..color = color) : _line(color, outline, false),
  );

  void box(double x, double y, double w, double h, Color color, {double r = 0, double? outline}) =>
      drawRRect(
        RRect.fromRectAndRadius(Rect.fromLTWH(x, y, w, h), Radius.circular(r)),
        outline == null ? (Paint()..color = color) : _line(color, outline, false),
      );

  void seg(
    double x1,
    double y1,
    double x2,
    double y2,
    Color color,
    double width, {
    bool round = false,
  }) => drawLine(Offset(x1, y1), Offset(x2, y2), _line(color, width, round));

  /// Dreht alles, was `draw` zeichnet, um einen Punkt. Winkel in Grad.
  void turned(double degrees, double cx, double cy, VoidCallback draw) {
    save();
    translate(cx, cy);
    rotate(degrees * math.pi / 180);
    translate(-cx, -cy);
    draw();
    restore();
  }

  /// Text an einem Punkt. y ist die Grundlinie, mit `middle` die Mitte der Zeile.
  void label(
    String text,
    double x,
    double y, {
    required double size,
    FontWeight weight = FontWeight.w400,
    Color color = Tokens.ink,
    TextAlign align = TextAlign.center,
    bool middle = false,
  }) {
    final painter = TextPainter(
      text: TextSpan(
        text: text,
        style: jost(size, weight, color: color, height: 1),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    final dx = switch (align) {
      TextAlign.center => -painter.width / 2,
      TextAlign.end => -painter.width,
      _ => 0.0,
    };
    final dy = middle
        ? -painter.height / 2
        : -painter.computeDistanceToActualBaseline(TextBaseline.alphabetic);
    painter.paint(this, Offset(x + dx, y + dy));
    painter.dispose();
  }
}

/// Zeichnet in ein festes Koordinatenfeld, wie ein SVG mit viewBox. Schrumpft, wenn der Platz fehlt.
class Sketch extends StatelessWidget {
  const Sketch(this.box, this.draw, {super.key, this.width, this.label});

  final Size box;
  final void Function(Canvas canvas) draw;

  /// Breite, wenn Platz ist. Ohne Angabe die Breite des Felds.
  final double? width;

  /// Für Screenreader. Ohne Angabe ist das Bild Schmuck.
  final String? label;

  @override
  Widget build(BuildContext context) {
    final width = this.width ?? box.width;
    final picture = FittedBox(
      fit: BoxFit.scaleDown,
      child: SizedBox(
        width: width,
        height: width * box.height / box.width,
        child: CustomPaint(painter: _SketchPainter(box, draw)),
      ),
    );
    return label == null
        ? ExcludeSemantics(child: picture)
        : Semantics(label: label, image: true, child: picture);
  }
}

class _SketchPainter extends CustomPainter {
  const _SketchPainter(this.box, this.draw);

  final Size box;
  final void Function(Canvas canvas) draw;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(size.width / box.width, size.height / box.height);
    draw(canvas);
  }

  @override
  bool shouldRepaint(_SketchPainter old) => true;
}

/// Gestrichelter Rand mit runden Ecken. Flutter kennt nur durchgezogene Ränder.
class DashedBorder extends StatelessWidget {
  const DashedBorder({
    super.key,
    required this.color,
    required this.width,
    required this.radius,
    this.fill,
    this.child,
  });

  final Color color;
  final double width;
  final double radius;
  final Color? fill;
  final Widget? child;

  @override
  Widget build(BuildContext context) =>
      CustomPaint(painter: _DashedPainter(color, width, radius, fill), child: child);
}

class _DashedPainter extends CustomPainter {
  const _DashedPainter(this.color, this.width, this.radius, this.fill);

  final Color color;
  final double width;
  final double radius;
  final Color? fill;

  @override
  void paint(Canvas canvas, Size size) {
    final shape = RRect.fromRectAndRadius(
      (Offset.zero & size).deflate(width / 2),
      Radius.circular(math.max(0, radius - width / 2)),
    );
    final fill = this.fill;
    if (fill != null) canvas.drawRRect(shape, Paint()..color = fill);
    canvas.drawPath(
      dashed(Path()..addRRect(shape), width * 2.4, width * 1.6),
      _line(color, width, false),
    );
  }

  @override
  bool shouldRepaint(_DashedPainter old) =>
      old.color != color || old.width != width || old.radius != radius || old.fill != fill;
}
