import 'package:flutter/widgets.dart';

import '../ui/sketch.dart';
import '../ui/tokens.dart';
import 'counters.dart';

enum _Slot { red, blue, removed, empty, none }

/// Zwei Reihen à zehn, mit Lücke nach fünf (Kraft der Fünf).
/// Wird die Antwort geprüft, füllen sich die leeren Plättchen.
class TwentyField extends StatelessWidget {
  const TwentyField(this.counters, {super.key, required this.revealed});

  final Counters counters;
  final bool revealed;

  @override
  Widget build(BuildContext context) {
    final compact = isCompact(context);
    final size = compact ? 24.0 : 40.0;
    final all = [
      ...List.filled(counters.red, _Slot.red),
      ...List.filled(counters.blue, _Slot.blue),
      ...List.filled(counters.removed, _Slot.removed),
      ...List.filled(counters.empty, revealed ? _Slot.blue : _Slot.empty),
    ];
    final (top, bottom) = switch (counters.layout) {
      CounterLayout.pairs => (
        [for (var i = 0; i < all.length; i += 2) all[i]],
        [for (var i = 1; i < all.length; i += 2) all[i]],
      ),
      CounterLayout.mirror => (all.take(counters.red).toList(), all.skip(counters.red).toList()),
      CounterLayout.rows => (all.take(10).toList(), all.skip(10).toList()),
    };

    Widget counter(_Slot slot, int i) => AnimatedContainer(
      duration: reducedMotion(context) ? Duration.zero : const Duration(milliseconds: 350),
      width: size,
      height: size,
      margin: EdgeInsets.only(left: i == 5 ? (compact ? 8 : 18) : 0),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: switch (slot) {
          _Slot.red => Tokens.red,
          _Slot.blue => Tokens.blue,
          _Slot.removed => Tokens.red.withValues(alpha: 0.22),
          _Slot.empty || _Slot.none => Tokens.board,
        },
      ),
      child: slot == _Slot.empty
          ? DashedBorder(color: Tokens.blue, width: compact ? 2 : 3, radius: size / 2)
          : null,
    );

    Widget row(List<_Slot> slots) => Row(
      mainAxisSize: MainAxisSize.min,
      spacing: compact ? 4 : 8,
      children: [for (var i = 0; i < 10; i++) counter(i < slots.length ? slots[i] : _Slot.none, i)],
    );

    return Semantics(
      label: '${counters.red} rote und ${counters.blue} blaue Plättchen',
      image: true,
      child: FittedBox(
        fit: BoxFit.scaleDown,
        child: Container(
          padding: compact
              ? const EdgeInsets.all(12)
              : const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
          decoration: BoxDecoration(color: Tokens.chalk, borderRadius: BorderRadius.circular(24)),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            spacing: compact ? 8 : 12,
            children: [row(top), row(bottom)],
          ),
        ),
      ),
    );
  }
}
