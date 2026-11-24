import 'package:flutter/widgets.dart';

import '../olli/olli_view.dart';
import '../ui/controls.dart';
import '../ui/tokens.dart';

/// Rahmen für Anmelden und Onboarding: Olli auf Rosa, daneben das Formular.
class Entry extends StatelessWidget {
  const Entry({super.key, required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final wide = MediaQuery.sizeOf(context).width >= 900;
    final titleSize = fluid(context, 32, 4.4, 60);
    final hello = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      spacing: 12,
      children: [
        ConstrainedBox(
          constraints: BoxConstraints(maxWidth: titleSize * 5),
          child: Text('Hallo, ich bin Olli.', style: heading(titleSize)),
        ),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 290),
          child: Text(
            'Ich übe Mathe mit Kindern der ersten Jahrgangsstufe.',
            style: jost(20, FontWeight.w500),
          ),
        ),
      ],
    );
    final form = Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 36, 24, 64),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            spacing: 20,
            children: children,
          ),
        ),
      ),
    );

    if (!wide) {
      return SafeArea(
        child: ListView(
          children: [
            Container(
              color: Tokens.pink,
              padding: const EdgeInsets.fromLTRB(24, 24, 24, 28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                spacing: 20,
                children: [
                  const Wordmark(),
                  Row(
                    spacing: 16,
                    children: [
                      const OlliView(mood: Mood.happy, size: 96),
                      Expanded(child: hello),
                    ],
                  ),
                ],
              ),
            ),
            form,
          ],
        ),
      );
    }
    return SafeArea(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            flex: 5,
            child: Container(
              color: Tokens.pink,
              padding: const EdgeInsets.fromLTRB(48, 40, 48, 56),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Wordmark(),
                  const Spacer(),
                  const OlliView(mood: Mood.happy, size: 168),
                  const SizedBox(height: 28),
                  hello,
                  const Spacer(),
                ],
              ),
            ),
          ),
          Expanded(flex: 6, child: CenterScroll(child: form)),
        ],
      ),
    );
  }
}

/// Ein Schritt im Formular: Überschrift, dann der Inhalt.
class EntrySection extends StatelessWidget {
  const EntrySection(this.title, {super.key, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    mainAxisSize: MainAxisSize.min,
    spacing: 18,
    children: [
      Text(title, style: heading(32)),
      ...children,
    ],
  );
}
