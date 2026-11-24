import 'package:flutter/foundation.dart';

import 'api/client.dart';
import 'api/models.dart';

/// Was die ganze App teilt: die Anmeldung, die Kinder und was dem Konto noch fehlt.
class AppState extends ChangeNotifier {
  AppState(this.api);

  final Api api;

  /// null: noch nicht geladen.
  List<Child>? kids;

  /// Was dem Konto noch fehlt. null: alles da, kein Onboarding. Abgeleitet aus den Daten.
  ({bool child, bool pin})? setup;
  String? error;

  bool get signedIn => api.signedIn;

  /// Lädt Kinder und PIN-Stand. Nach der Anmeldung und beim Start.
  Future<void> load() async {
    kids = null;
    setup = null;
    error = null;
    notifyListeners();
    try {
      final list = await api.children();
      final pinSet = await api.pinSet();
      final child = list.isEmpty;
      setup = child || !pinSet ? (child: child, pin: !pinSet) : null;
      kids = list;
    } catch (e) {
      // Ist die Anmeldung dabei abgelaufen, zeigt die App den Login, keinen Fehler.
      if (api.signedIn) error = 'Olli erreicht den Server nicht. $e';
    }
    notifyListeners();
  }

  void addChild(Child child) {
    kids = [...?kids, child];
    notifyListeners();
  }

  void finishSetup() {
    setup = null;
    notifyListeners();
  }

  void signedOut() {
    kids = null;
    setup = null;
    error = null;
    notifyListeners();
  }
}
