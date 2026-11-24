import 'package:flutter/widgets.dart';

import '../ui/controls.dart';
import '../ui/icons.dart';
import '../ui/tokens.dart';

/// `block`: drei mal drei, für die PIN. `row`: die Ziffern 1 bis 0 in einer Reihe unter der Tafel,
/// schmal in zwei Reihen, Löschen und Haken darunter. So bleibt der Block beim Üben flach.
enum KeypadLayout { block, row }

class Keypad extends StatelessWidget {
  const Keypad({
    super.key,
    required this.value,
    required this.onChange,
    required this.onSubmit,
    this.layout = KeypadLayout.block,
    this.minLength = 1,
    this.maxLength = 2,
    this.submitLabel,
    this.disabled = false,
  });

  final String value;
  final ValueChanged<String> onChange;
  final VoidCallback onSubmit;
  final KeypadLayout layout;
  final int minLength;
  final int maxLength;

  /// Ohne Text zeigt der Knopf einen Haken.
  final String? submitLabel;
  final bool disabled;

  @override
  Widget build(BuildContext context) {
    final compact = isCompact(context);
    final height = compact ? 62.0 : 72.0;

    Widget key(
      Widget Function(bool pressed) face,
      VoidCallback? onTap, {
      String? label,
      bool submit = false,
    }) => Tap(
      onTap: disabled ? null : onTap,
      label: label,
      radius: 22,
      builder: (pressed) => Container(
        height: height,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: submit
              ? (pressed ? Tokens.sunPressed : Tokens.sun)
              : (pressed ? Tokens.blue : Tokens.board),
          borderRadius: BorderRadius.circular(22),
        ),
        child: face(pressed && !submit),
      ),
    );

    Widget digit(String d) => key(
      (lit) => Text(d, style: jost(34, FontWeight.w700, color: lit ? Tokens.white : Tokens.ink)),
      value.length < maxLength ? () => onChange(value + d) : () {},
    );

    final erase = key(
      (lit) => OlliIcon(IconName.erase, size: 34, color: lit ? Tokens.white : Tokens.ink),
      value.isEmpty ? null : () => onChange(value.substring(0, value.length - 1)),
      label: 'Letzte Ziffer löschen',
    );
    final submitLabel = this.submitLabel;
    final submit = key(
      (_) => submitLabel == null
          ? const OlliIcon(IconName.check, size: 34, color: Tokens.ink)
          : Text(submitLabel, style: jost(20, FontWeight.w700, color: Tokens.ink)),
      value.length < minLength ? null : onSubmit,
      label: submitLabel == null ? 'Fertig' : null,
      submit: true,
    );

    if (layout == KeypadLayout.block) {
      final width = compact ? 76.0 : 84.0;
      final gap = compact ? 10.0 : 12.0;
      Widget row(List<Widget> keys) => Row(
        mainAxisSize: MainAxisSize.min,
        spacing: gap,
        children: [for (final k in keys) SizedBox(width: width, child: k)],
      );
      return Column(
        mainAxisSize: MainAxisSize.min,
        spacing: gap,
        children: [
          row([digit('1'), digit('2'), digit('3')]),
          row([digit('4'), digit('5'), digit('6')]),
          row([digit('7'), digit('8'), digit('9')]),
          row([erase, digit('0'), submit]),
        ],
      );
    }

    // Schmal: zwei Reihen mit je fünf Ziffern.
    final narrow = MediaQuery.sizeOf(context).width <= 640;
    Widget digits(String keys) =>
        Row(spacing: 10, children: [for (final d in keys.split('')) Expanded(child: digit(d))]);
    const empty = Spacer(flex: 2);
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: narrow ? 420 : 730),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        spacing: 10,
        children: [
          if (narrow) ...[digits('12345'), digits('67890')] else digits('1234567890'),
          Row(
            spacing: 10,
            children: narrow
                ? [Expanded(flex: 2, child: erase), Expanded(flex: 3, child: submit)]
                : [empty, Expanded(flex: 2, child: erase), Expanded(flex: 4, child: submit), empty],
          ),
        ],
      ),
    );
  }
}
