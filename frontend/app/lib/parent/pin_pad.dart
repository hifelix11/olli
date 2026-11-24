import 'package:flutter/widgets.dart';

import '../child/keypad.dart';
import '../ui/tokens.dart';

const _length = 4;

/// Vier Punkte und der Zahlenblock. Abschicken geht erst mit vier Ziffern.
class PinPad extends StatelessWidget {
  const PinPad({
    super.key,
    required this.value,
    required this.onChange,
    required this.onSubmit,
    required this.submitLabel,
  });

  final String value;
  final ValueChanged<String> onChange;
  final VoidCallback onSubmit;
  final String submitLabel;

  @override
  Widget build(BuildContext context) => Column(
    mainAxisSize: MainAxisSize.min,
    spacing: 24,
    children: [
      Semantics(
        label: '${value.length} von $_length Ziffern',
        child: Row(
          mainAxisSize: MainAxisSize.min,
          spacing: 16,
          children: [
            for (var i = 0; i < _length; i++)
              Container(
                width: 22,
                height: 22,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: i < value.length ? Tokens.ink : null,
                  border: Border.all(color: Tokens.ink, width: 3),
                ),
              ),
          ],
        ),
      ),
      Keypad(
        value: value,
        onChange: onChange,
        onSubmit: onSubmit,
        minLength: _length,
        maxLength: _length,
        submitLabel: submitLabel,
      ),
    ],
  );
}
