import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'icons.dart';
import 'tokens.dart';

/// Alles, was man tippen kann, gibt beim Drücken nach. Kinder erwarten auf jeden Tipp eine Antwort.
/// `onTap` null: aus und blass.
class Tap extends StatefulWidget {
  const Tap({super.key, required this.onTap, required this.builder, this.label, this.radius = 999});

  final VoidCallback? onTap;
  final Widget Function(bool pressed) builder;

  /// Für Screenreader, wenn der Knopf nur ein Symbol zeigt.
  final String? label;

  /// Rundung für den Fokusrahmen.
  final double radius;

  @override
  State<Tap> createState() => _TapState();
}

class _TapState extends State<Tap> {
  bool _down = false;
  bool _focused = false;

  void _press(bool down) {
    if (mounted) setState(() => _down = down);
  }

  @override
  Widget build(BuildContext context) {
    final onTap = widget.onTap;
    final enabled = onTap != null;
    final down = _down && enabled;
    return Semantics(
      container: true,
      button: true,
      enabled: enabled,
      label: widget.label,
      child: FocusableActionDetector(
        enabled: enabled,
        mouseCursor: enabled ? SystemMouseCursors.click : MouseCursor.defer,
        actions: {ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => onTap?.call())},
        onShowFocusHighlight: (focused) => setState(() => _focused = focused),
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapDown: enabled ? (_) => _press(true) : null,
          onTapUp: enabled ? (_) => _press(false) : null,
          onTapCancel: enabled ? () => _press(false) : null,
          onTap: onTap,
          child: AnimatedScale(
            scale: down ? 0.93 : 1,
            duration: reducedMotion(context) ? Duration.zero : const Duration(milliseconds: 120),
            child: Opacity(
              opacity: enabled ? 1 : 0.35,
              child: DecoratedBox(
                position: DecorationPosition.foreground,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(widget.radius),
                  border: _focused && enabled ? Border.all(color: Tokens.blue, width: 4) : null,
                ),
                child: widget.builder(down),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

enum BtnKind { plain, primary, quiet }

/// Knopf mit Text, für Eltern. `primary` ist Nacht, `quiet` ein unterstrichener Link.
class Btn extends StatelessWidget {
  const Btn(this.text, {super.key, required this.onTap, this.kind = BtnKind.plain, this.icon});

  final String text;
  final VoidCallback? onTap;
  final BtnKind kind;
  final IconName? icon;

  @override
  Widget build(BuildContext context) {
    final quiet = kind == BtnKind.quiet;
    final color = switch (kind) {
      BtnKind.primary => Tokens.white,
      BtnKind.quiet => Tokens.inkSoft,
      BtnKind.plain => Tokens.ink,
    };
    final icon = this.icon;
    return Tap(
      onTap: onTap,
      builder: (_) => Container(
        constraints: BoxConstraints(minHeight: quiet ? 48 : 60),
        padding: EdgeInsets.symmetric(horizontal: quiet ? 14 : 28),
        decoration: quiet
            ? null
            : BoxDecoration(
                color: kind == BtnKind.primary ? Tokens.ink : Tokens.board,
                borderRadius: BorderRadius.circular(999),
              ),
        foregroundDecoration: kind == BtnKind.plain
            ? BoxDecoration(
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: Tokens.line, width: 2.5),
              )
            : null,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          spacing: 10,
          children: [
            if (icon != null) OlliIcon(icon, color: color),
            Flexible(
              child: Text(
                text,
                textAlign: TextAlign.center,
                style:
                    jost(
                      quiet ? 17 : 20,
                      quiet ? FontWeight.w600 : FontWeight.w700,
                      color: color,
                    ).copyWith(
                      decoration: quiet ? TextDecoration.underline : null,
                      decorationColor: color,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Runder Knopf mit Symbol, für das Kind. Gelb heißt los.
class RoundButton extends StatelessWidget {
  const RoundButton(
    this.icon, {
    super.key,
    required this.onTap,
    required this.label,
    this.size = 92,
    this.iconSize = 44,
    this.color = Tokens.sun,
    this.nudge = 0,
  });

  final IconName icon;
  final VoidCallback? onTap;
  final String label;
  final double size;
  final double iconSize;
  final Color color;

  /// Schiebt das Symbol nach rechts. Das Dreieck von Play wirkt sonst nicht mittig.
  final double nudge;

  @override
  Widget build(BuildContext context) => Tap(
    onTap: onTap,
    label: label,
    builder: (_) => Container(
      width: size,
      height: size,
      padding: EdgeInsets.only(left: nudge),
      alignment: Alignment.center,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      child: OlliIcon(icon, size: iconSize, color: Tokens.ink),
    ),
  );
}

/// Das Haus: zurück zum Start.
class HomeButton extends StatelessWidget {
  const HomeButton(this.onExit, {super.key});

  final VoidCallback onExit;

  @override
  Widget build(BuildContext context) => RoundButton(
    IconName.home,
    onTap: onExit,
    label: 'Zum Start',
    size: 56,
    iconSize: 28,
    color: Tokens.board,
  );
}

/// Eingabefeld für Eltern.
class Field extends StatelessWidget {
  const Field({
    super.key,
    required this.controller,
    required this.hint,
    this.password = false,
    this.autofill,
    this.keyboard,
    this.maxLength,
    this.autofocus = false,
    this.onSubmit,
  });

  final TextEditingController controller;
  final String hint;
  final bool password;
  final String? autofill;
  final TextInputType? keyboard;
  final int? maxLength;
  final bool autofocus;
  final VoidCallback? onSubmit;

  @override
  Widget build(BuildContext context) {
    OutlineInputBorder border(Color color) => OutlineInputBorder(
      borderRadius: BorderRadius.circular(18),
      borderSide: BorderSide(color: color, width: 2.5),
    );
    final autofill = this.autofill;
    final maxLength = this.maxLength;
    return TextField(
      controller: controller,
      obscureText: password,
      autofocus: autofocus,
      keyboardType: keyboard,
      autofillHints: autofill == null ? null : [autofill],
      inputFormatters: [if (maxLength != null) LengthLimitingTextInputFormatter(maxLength)],
      onSubmitted: (_) => onSubmit?.call(),
      style: jost(20, FontWeight.w400, color: Tokens.ink),
      cursorColor: Tokens.blue,
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: jost(20, FontWeight.w400, color: Tokens.inkSoft),
        filled: true,
        fillColor: Tokens.board,
        isDense: true,
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15.5),
        enabledBorder: border(Tokens.line),
        focusedBorder: border(Tokens.blue),
      ),
    );
  }
}

class Wordmark extends StatelessWidget {
  const Wordmark({super.key});

  @override
  Widget build(BuildContext context) =>
      Text('olli', style: jost(40, FontWeight.w800, height: 1, spacing: -1.6));
}

class ErrorText extends StatelessWidget {
  const ErrorText(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) => Text(
    text,
    style: const TextStyle(color: Tokens.redText, fontWeight: FontWeight.w600),
  );
}

/// Stellt den Inhalt in die Mitte der Höhe. Scrollt, wenn er höher ist als der Platz.
class CenterScroll extends StatelessWidget {
  const CenterScroll({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, box) => SingleChildScrollView(
      child: ConstrainedBox(
        constraints: BoxConstraints(minHeight: box.maxHeight),
        child: Center(child: child),
      ),
    ),
  );
}

/// Alles mittig auf einer Farbfläche: Laden, Begrüßung, Ende, PIN. Scrollt, wenn der Platz fehlt.
class CenterPage extends StatelessWidget {
  const CenterPage({
    super.key,
    required this.children,
    this.color = Tokens.chalk,
    this.textColor = Tokens.ink,
    this.onHome,
  });

  final List<Widget> children;
  final Color color;
  final Color textColor;

  /// Mit Haus oben links.
  final VoidCallback? onHome;

  @override
  Widget build(BuildContext context) {
    final onHome = this.onHome;
    return ColoredBox(
      color: color,
      child: SafeArea(
        child: Stack(
          children: [
            Positioned.fill(
              child: CenterScroll(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(24, 88, 24, 48),
                  child: DefaultTextStyle.merge(
                    style: TextStyle(color: textColor),
                    textAlign: TextAlign.center,
                    child: Column(mainAxisSize: MainAxisSize.min, spacing: 24, children: children),
                  ),
                ),
              ),
            ),
            if (onHome != null) Positioned(top: 16, left: 20, child: HomeButton(onHome)),
          ],
        ),
      ),
    );
  }
}

/// Große Überschrift auf einer [CenterPage].
class PageTitle extends StatelessWidget {
  const PageTitle(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) => Text(text, style: heading(fluid(context, 34, 6, 52)));
}
