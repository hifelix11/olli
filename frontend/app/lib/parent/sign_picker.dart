import 'package:flutter/widgets.dart';

import '../api/models.dart';
import '../child/sign.dart';
import '../ui/controls.dart';
import '../ui/tokens.dart';

const _size = 60.0;
const _radius = _size * 7 / 24; // wie das Farbfeld: Der Rand liegt genau am Bild.

/// Zeichen für ein neues Kind wählen. Im Elternbereich und im Onboarding.
class SignPicker extends StatelessWidget {
  const SignPicker({super.key, required this.value, required this.onChange});

  final Sign value;
  final ValueChanged<Sign> onChange;

  @override
  Widget build(BuildContext context) => Wrap(
    spacing: 10,
    runSpacing: 10,
    children: [
      for (final sign in Sign.values)
        Semantics(
          inMutuallyExclusiveGroup: true,
          checked: sign == value,
          child: Tap(
            onTap: () => onChange(sign),
            radius: _radius,
            builder: (_) => DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(_radius),
                boxShadow: [if (sign == value) const BoxShadow(color: Tokens.ink, spreadRadius: 4)],
              ),
              child: SignIcon(sign, size: _size),
            ),
          ),
        ),
    ],
  );
}
