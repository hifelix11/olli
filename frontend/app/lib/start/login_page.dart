import 'package:flutter/widgets.dart';

import '../api/client.dart';
import '../ui/controls.dart';
import 'entry.dart';

const _messages = {
  'invalid_credentials': 'E-Mail oder Passwort stimmt nicht.',
  'user_already_exists': 'Zu dieser E-Mail gibt es schon ein Konto.',
  'weak_password': 'Das Passwort ist zu kurz oder zu einfach.',
  'email_not_confirmed':
      'Die E-Mail-Adresse ist noch nicht bestätigt. Der Link steht in der E-Mail.',
  'email_address_invalid': 'Die E-Mail-Adresse sieht nicht richtig aus.',
  'validation_failed': 'Die E-Mail-Adresse sieht nicht richtig aus.',
  'over_request_rate_limit': 'Zu viele Versuche. Bitte in ein paar Minuten noch einmal.',
  'over_email_send_rate_limit': 'Zu viele Versuche. Bitte in ein paar Minuten noch einmal.',
};

String _message(Object error) {
  if (error is! ApiError) return 'Olli erreicht den Server nicht.';
  return _messages[error.code] ?? 'Das hat nicht geklappt (${error.code}).';
}

/// Anmelden und Konto anlegen. Das Konto gehört den Eltern.
class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.api, required this.onDone});

  final Api api;
  final VoidCallback onDone;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _signup = false;
  bool _busy = false;
  String? _error;
  String? _info;

  @override
  void initState() {
    super.initState();
    _email.addListener(_refresh);
    _password.addListener(_refresh);
  }

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  void _refresh() => setState(() {});

  bool get _ready => !_busy && _email.text.trim().isNotEmpty && _password.text.isNotEmpty;

  Future<void> _submit() async {
    if (!_ready) return;
    setState(() {
      _busy = true;
      _error = null;
      _info = null;
    });
    final email = _email.text.trim();
    try {
      if (!_signup) {
        await widget.api.login(email, _password.text);
        widget.onDone();
      } else if (await widget.api.signup(email, _password.text)) {
        widget.onDone();
      } else {
        _signup = false;
        _info = 'Fast geschafft. Bitte den Link in der E-Mail öffnen und dann hier anmelden.';
      }
    } catch (error) {
      _error = _message(error);
    }
    if (mounted) setState(() => _busy = false);
  }

  @override
  Widget build(BuildContext context) {
    final title = _signup ? 'Konto anlegen' : 'Anmelden';
    final error = _error;
    final info = _info;
    return Entry(
      children: [
        EntrySection(
          title,
          children: [
            const Text('Das Konto gehört den Eltern. Kinder üben ohne eigenes Konto.'),
            AutofillGroup(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                spacing: 12,
                children: [
                  Field(
                    controller: _email,
                    hint: 'E-Mail',
                    keyboard: TextInputType.emailAddress,
                    autofill: AutofillHints.email,
                    onSubmit: _submit,
                  ),
                  Field(
                    controller: _password,
                    hint: 'Passwort',
                    password: true,
                    autofill: _signup ? AutofillHints.newPassword : AutofillHints.password,
                    onSubmit: _submit,
                  ),
                  Btn(title, kind: BtnKind.primary, onTap: _ready ? _submit : null),
                ],
              ),
            ),
            if (error != null) ErrorText(error),
            if (info != null) Text(info),
          ],
        ),
        Align(
          alignment: Alignment.centerLeft,
          child: Btn(
            _signup ? 'Schon ein Konto? Anmelden' : 'Noch kein Konto? Konto anlegen',
            kind: BtnKind.quiet,
            onTap: () => setState(() {
              _signup = !_signup;
              _error = null;
              _info = null;
            }),
          ),
        ),
      ],
    );
  }
}
