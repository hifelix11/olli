import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import 'package:go_router/go_router.dart';

import 'api/client.dart';
import 'api/models.dart';
import 'app_state.dart';
import 'child/practice_page.dart';
import 'olli/olli_view.dart';
import 'parent/parent_area.dart';
import 'start/login_page.dart';
import 'start/onboarding_page.dart';
import 'start/start_page.dart';
import 'ui/controls.dart';
import 'ui/tokens.dart';

/// Adresse des Backends. Ändern mit `--dart-define=API_URL=...`.
const _apiUrl = String.fromEnvironment('API_URL', defaultValue: 'http://127.0.0.1:8000');

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  usePathUrlStrategy(); // Adressen wie /practice/<id>, ohne Raute
  final api = Api(_apiUrl);
  await api.restore();
  runApp(OlliApp(AppState(api)));
}

class OlliApp extends StatefulWidget {
  const OlliApp(this.app, {super.key});

  final AppState app;

  @override
  State<OlliApp> createState() => _OlliAppState();
}

class _OlliAppState extends State<OlliApp> {
  late final _router = _buildRouter(widget.app);

  @override
  void initState() {
    super.initState();
    final app = widget.app;
    // Nach dem Abmelden geht es zum Start.
    app.api.onSignOut = () {
      app.signedOut();
      _router.go('/');
    };
    if (app.signedIn) app.load();
  }

  @override
  Widget build(BuildContext context) => MaterialApp.router(
    title: 'Olli',
    debugShowCheckedModeBanner: false,
    routerConfig: _router,
    locale: const Locale('de'),
    supportedLocales: const [Locale('de')],
    localizationsDelegates: GlobalMaterialLocalizations.delegates,
    theme: ThemeData(
      fontFamily: 'Jost',
      colorScheme: ColorScheme.fromSeed(seedColor: Tokens.blue),
    ),
    builder: (context, child) =>
        Material(color: Tokens.chalk, textStyle: Tokens.body, child: child),
  );
}

/// Drei Adressen: `/` Kind wählen, `/practice/<id>` üben, `/parent` Elternbereich.
/// Die Adresse trägt die ID des Kindes, nie den Namen.
GoRouter _buildRouter(AppState app) {
  Page<void> page(GoRouterState state, Widget Function(BuildContext, List<Child>) builder) =>
      NoTransitionPage(key: state.pageKey, child: _Gate(app, builder));

  return GoRouter(
    refreshListenable: app,
    // Unbekannte Adresse: zurück zum Start.
    onException: (_, _, router) => router.go('/'),
    routes: [
      GoRoute(
        path: '/',
        pageBuilder: (_, state) => page(
          state,
          (context, kids) => StartPage(
            kids: kids,
            onPractice: (child) => context.go('/practice/${child.id}'),
            onParent: () => context.go('/parent'),
          ),
        ),
      ),
      GoRoute(
        path: '/practice/:childId',
        // Fremdes Kind: zurück zum Start.
        redirect: (_, state) {
          final kids = app.kids;
          final known = kids == null || kids.any((k) => k.id == state.pathParameters['childId']);
          return known ? null : '/';
        },
        pageBuilder: (_, state) => page(state, (context, kids) {
          final id = state.pathParameters['childId'];
          final child = kids.where((k) => k.id == id).firstOrNull;
          if (child == null) return const SizedBox();
          return PracticePage(
            key: ValueKey(child.id),
            api: app.api,
            child: child,
            onExit: () => context.go('/'),
          );
        }),
      ),
      GoRoute(
        path: '/parent',
        pageBuilder: (_, state) =>
            page(state, (context, kids) => ParentArea(app: app, onExit: () => context.go('/'))),
      ),
    ],
  );
}

/// Anmelden und Onboarding haben keine eigene Adresse, sie liegen vor jeder Seite.
class _Gate extends StatelessWidget {
  const _Gate(this.app, this.builder);

  final AppState app;
  final Widget Function(BuildContext context, List<Child> kids) builder;

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: app,
    builder: (context, _) {
      if (!app.signedIn) return LoginPage(api: app.api, onDone: app.load);
      final kids = app.kids;
      if (kids == null) {
        final error = app.error;
        return CenterPage(
          children: [
            const OlliView(mood: Mood.thinking, size: 120),
            if (error == null) const Text('Einen Moment.') else ErrorText(error),
            if (error != null) Btn('Nochmal versuchen', kind: BtnKind.quiet, onTap: app.load),
          ],
        );
      }
      final setup = app.setup;
      if (setup != null) {
        return OnboardingPage(
          api: app.api,
          needsChild: setup.child,
          needsPin: setup.pin,
          onAdd: app.addChild,
          // Danach übt das neue Kind sofort.
          onDone: (child) {
            app.finishSetup();
            context.go(child == null ? '/' : '/practice/${child.id}');
          },
        );
      }
      return builder(context, kids);
    },
  );
}
