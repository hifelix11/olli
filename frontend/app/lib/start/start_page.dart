import 'package:flutter/widgets.dart';

import '../api/models.dart';
import '../child/sign.dart';
import '../olli/olli_view.dart';
import '../ui/controls.dart';
import '../ui/icons.dart';
import '../ui/tokens.dart';

const _maxWidth = 960.0;
const _gap = 16.0;

/// Start: Wer übt heute? Jedes Kind findet sich an seinem Zeichen.
class StartPage extends StatelessWidget {
  const StartPage({
    super.key,
    required this.kids,
    required this.onPractice,
    required this.onParent,
  });

  final List<Child> kids;
  final ValueChanged<Child> onPractice;
  final VoidCallback onParent;

  @override
  Widget build(BuildContext context) {
    final width = (MediaQuery.sizeOf(context).width - 48).clamp(0.0, _maxWidth);
    // So viele Kacheln, wie mit mindestens 160 Breite in die Zeile passen.
    final columns = ((width + _gap) / (160 + _gap)).floor().clamp(1, 99);
    final tile = (width - (columns - 1) * _gap) / columns;
    return ColoredBox(
      color: Tokens.pink,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [const Wordmark(), _parentButton()],
              ),
              Expanded(
                child: CenterScroll(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 28, bottom: 40),
                    child: SizedBox(
                      width: width,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        spacing: 28,
                        children: [
                          Row(
                            spacing: 20,
                            children: [
                              const OlliView(mood: Mood.happy, size: 112),
                              Flexible(
                                child: Text(
                                  'Wer übt heute?',
                                  style: heading(fluid(context, 36, 6, 64)),
                                ),
                              ),
                            ],
                          ),
                          Wrap(
                            spacing: _gap,
                            runSpacing: _gap,
                            children: [
                              for (final child in kids) SizedBox(width: tile, child: _tile(child)),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _parentButton() => Tap(
    onTap: onParent,
    builder: (_) => Container(
      height: 48,
      padding: const EdgeInsets.fromLTRB(16, 0, 20, 0),
      decoration: BoxDecoration(
        color: Tokens.white.withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        spacing: 10,
        children: [
          const OlliIcon(IconName.lock, size: 20),
          Text('Eltern', style: jost(17, FontWeight.w600)),
        ],
      ),
    ),
  );

  Widget _tile(Child child) => Tap(
    onTap: () => onPractice(child),
    radius: 32,
    builder: (_) => Container(
      padding: const EdgeInsets.fromLTRB(12, 20, 12, 18),
      decoration: BoxDecoration(color: Tokens.board, borderRadius: BorderRadius.circular(32)),
      child: Column(
        spacing: 12,
        children: [
          SignIcon(child.sign, size: 112),
          Text(child.name, textAlign: TextAlign.center, style: jost(26, FontWeight.w700)),
        ],
      ),
    ),
  );
}
