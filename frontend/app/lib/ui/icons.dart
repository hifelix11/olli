import 'package:flutter/widgets.dart';

import 'sketch.dart';
import 'tokens.dart';

/// Symbole statt Wörter: Ein Kind in der ersten Jahrgangsstufe liest noch nicht.
enum IconName { home, next, check, play, erase, lock }

const _play = 'M8 5.2v13.6a1 1 0 0 0 1.5.9l10.6-6.8a1 1 0 0 0 0-1.8L9.5 4.3A1 1 0 0 0 8 5.2z';

const _strokes = <IconName, List<String>>{
  IconName.home: ['M3.5 11L12 4l8.5 7M6 9.5V19a1 1 0 0 0 1 1h3.5v-5h3v5H17a1 1 0 0 0 1-1V9.5'],
  IconName.next: ['M4.5 12h14M13 6l6 6-6 6'],
  IconName.check: ['M4.5 12.5l5 5L19.5 7'],
  IconName.play: [_play],
  // Radiergummi: Kinder korrigieren mit dem Radierer, nicht mit "Rückgängig".
  IconName.erase: [
    'M14.2 4.6l5.2 5.2a1.5 1.5 0 0 1 0 2.1L12 19.3H8.3l-3.7-3.7a1.5 1.5 0 0 1 0-2.1l7.5-7.5a1.5 1.5 0 0 1 2.1 0z',
    'M8.6 9l6.4 6.4M12 19.3h8',
  ],
  IconName.lock: [
    'M7.5 10.5h9a2.5 2.5 0 0 1 2.5 2.5v5a2.5 2.5 0 0 1-2.5 2.5h-9a2.5 2.5 0 0 1-2.5-2.5v-5a2.5 2.5 0 0 1 2.5-2.5z',
    'M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5',
  ],
};

/// Ein Symbol in der Farbe des Textes drumherum.
class OlliIcon extends StatelessWidget {
  const OlliIcon(this.name, {super.key, this.size = 28, this.color});

  final IconName name;
  final double size;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final color = this.color ?? DefaultTextStyle.of(context).style.color ?? Tokens.ink;
    return Sketch(const Size(24, 24), width: size, (canvas) {
      if (name == IconName.play) canvas.fill(_play, color);
      for (final path in _strokes[name]!) {
        canvas.stroke(path, color, 2.6);
      }
    });
  }
}
