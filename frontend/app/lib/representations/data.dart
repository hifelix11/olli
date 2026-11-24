import 'dart:math';

import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';

const _bar = 44.0;
const _gap = 24.0;
const _x0 = 44.0;
const _top = 12.0;
const _base = 172.0;

List<String> _words(String text) => text.split(' ').where((w) => w.isNotEmpty).toList();

Widget _titled(String title, Widget child) => Column(
  mainAxisSize: MainAxisSize.min,
  spacing: 6,
  children: [
    Text(title, style: jost(19, FontWeight.w700)),
    child,
  ],
);

/// Säulendiagramm. Die Höhe steht nur an der Achse, nicht an der Säule.
class BarChart extends StatelessWidget {
  const BarChart({super.key, required this.title, required this.categories, required this.values});

  final String title;

  /// Mit Leerzeichen getrennt, etwa "Hund Katze Maus" und "4 2 5".
  final String categories;
  final String values;

  @override
  Widget build(BuildContext context) {
    final cats = _words(categories);
    final vals = _words(values).map(num.parse).toList();
    final top = vals.fold<num>(1, max);
    final unit = (_base - _top) / top;
    final step = top > 10 ? 2 : 1;
    final w = _x0 + cats.length * (_bar + _gap) + 8;
    return _titled(
      title,
      Sketch(Size(w, 200), label: 'Säulendiagramm: $title', (canvas) {
        for (var i = 0; i * step <= top; i++) {
          final y = _base - i * step * unit;
          canvas.seg(_x0, y, w - 4, y, Tokens.line, 1);
          canvas.seg(_x0 - 6, y, _x0, y, Tokens.ink, 2);
          canvas.label('${i * step}', _x0 - 10, y, size: 14, align: TextAlign.end, middle: true);
        }
        canvas.seg(_x0, _top, _x0, _base, Tokens.ink, 2);
        for (var i = 0; i < cats.length; i++) {
          final x = _x0 + _gap / 2 + i * (_bar + _gap);
          final value = i < vals.length ? vals[i] : 0;
          canvas.box(x, _base - value * unit, _bar, value * unit, Tokens.blue);
          canvas.label(cats[i], x + _bar / 2, _base + 20, size: 15);
        }
        canvas.seg(_x0, _base, w - 4, _base, Tokens.ink, 2);
      }),
    );
  }
}

/// Dieselben Daten wie das Säulendiagramm, als Tabelle.
class ValueTable extends StatelessWidget {
  const ValueTable({
    super.key,
    required this.title,
    required this.categories,
    required this.values,
  });

  final String title;
  final String categories;
  final String values;

  @override
  Widget build(BuildContext context) {
    final cats = _words(categories);
    final vals = _words(values);
    return Semantics(
      label: 'Tabelle: $title',
      child: _titled(
        title,
        IntrinsicWidth(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            spacing: 6,
            children: [
              for (var i = 0; i < cats.length; i++)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 8),
                  decoration: BoxDecoration(
                    color: Tokens.chalk,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    spacing: 44,
                    children: [
                      Text(cats[i], style: jost(22, FontWeight.w500)),
                      Text(i < vals.length ? vals[i] : '', style: jost(22, FontWeight.w700)),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
