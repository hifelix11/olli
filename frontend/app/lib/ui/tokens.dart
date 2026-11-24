import 'package:flutter/widgets.dart';

/// Die Formenkiste: flache Farben, runde Formen. Die Rolle jeder Farbe steht in der README.
abstract final class Tokens {
  static const chalk = Color(0xFFF3F1F9);
  static const board = Color(0xFFFFFFFF);
  static const ink = Color(0xFF24204A);
  static const inkSoft = Color(0xFF625D86);
  static const line = Color(0xFFDEDAEE);
  static const blue = Color(0xFF2E5BF0);
  static const blueSoft = Color(0xFFE1E7FF);
  static const red = Color(0xFFF24C3D);
  static const redText = Color(0xFFC7311F);
  static const sun = Color(0xFFFFC83D);
  static const sunSoft = Color(0xFFFFF1C9);
  static const sunPressed = Color(0xFFF5B400);
  static const pink = Color(0xFFFFB8D9);
  static const green = Color(0xFF2FA562);
  static const greenSoft = Color(0xFFDDF3E4);
  static const white = Color(0xFFFFFFFF);

  /// Ein Kästchen in Gittern und Längen.
  static const cell = 28.0;

  /// Fließtext. Alles andere setzt Größe und Stärke selbst.
  static final body = jost(18, FontWeight.w400, color: ink, height: 1.45);
}

/// Jost in einer Größe und Stärke. Ohne Farbe erbt der Text sie.
TextStyle jost(double size, FontWeight weight, {Color? color, double? height, double? spacing}) =>
    TextStyle(
      fontFamily: 'Jost',
      fontSize: size,
      fontWeight: weight,
      color: color,
      height: height,
      letterSpacing: spacing,
    );

/// Überschrift: fett und eng gesetzt.
TextStyle heading(double size) => jost(size, FontWeight.w800, height: 1.1, spacing: -0.01 * size);

/// Größe, die mit der Breite des Fensters wächst, zwischen zwei Grenzen.
double fluid(BuildContext context, double min, double percent, double max) =>
    (MediaQuery.sizeOf(context).width * percent / 100).clamp(min, max);

/// Schmal wie ein Telefon hochkant.
bool isCompact(BuildContext context) => MediaQuery.sizeOf(context).width <= 480;

/// Das Gerät bittet um weniger Bewegung. Dann springt nichts.
bool reducedMotion(BuildContext context) => MediaQuery.disableAnimationsOf(context);
