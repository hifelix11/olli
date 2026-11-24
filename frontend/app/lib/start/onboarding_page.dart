import 'package:flutter/widgets.dart';

import '../api/client.dart';
import '../api/models.dart';
import '../child/sign.dart';
import '../parent/pin_pad.dart';
import '../parent/sign_picker.dart';
import '../ui/controls.dart';
import 'entry.dart';

enum _Step { child, pin, done }

const _offline = 'Olli erreicht den Server nicht.';

/// Erster Start nach der Anmeldung. Zeigt nur, was noch fehlt: Kind, PIN.
class OnboardingPage extends StatefulWidget {
  const OnboardingPage({
    super.key,
    required this.api,
    required this.needsChild,
    required this.needsPin,
    required this.onAdd,
    required this.onDone,
  });

  final Api api;
  final bool needsChild;
  final bool needsPin;
  final ValueChanged<Child> onAdd;

  /// Mit Kind: Das neue Kind übt gleich. null: zurück zum Start.
  final ValueChanged<Child?> onDone;

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  late final _steps = [
    if (widget.needsChild) _Step.child,
    if (widget.needsPin) _Step.pin,
    if (widget.needsChild) _Step.done,
  ];
  final _name = TextEditingController();
  int _index = 0;
  Child? _child;
  Sign _sign = freeSign(const []);
  String _pin = '';
  String? _first; // erste Eingabe, wartet auf Wiederholung
  String? _error;

  @override
  void initState() {
    super.initState();
    _name.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  void _next() {
    if (_index + 1 < _steps.length) {
      setState(() {
        _error = null;
        _index++;
      });
    } else {
      widget.onDone(_child);
    }
  }

  Future<void> _addChild() async {
    final name = _name.text.trim();
    if (name.isEmpty) return;
    try {
      final created = await widget.api.createChild(name, _sign);
      widget.onAdd(created);
      _child = created;
      _next();
    } catch (_) {
      setState(() => _error = _offline);
    }
  }

  Future<void> _choosePin() async {
    final pin = _pin;
    final first = _first;
    setState(() => _pin = '');
    if (first == null) {
      setState(() {
        _first = pin;
        _error = null;
      });
    } else if (pin != first) {
      setState(() {
        _first = null;
        _error = 'Die beiden PINs sind verschieden. Bitte neu wählen.';
      });
    } else {
      try {
        await widget.api.setPin(pin);
        _next();
      } catch (_) {
        setState(() {
          _first = null;
          _error = _offline;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final error = _error;
    final child = _child;
    return Entry(
      children: [
        switch (_steps[_index]) {
          _Step.child => EntrySection(
            'Wer übt mit mir?',
            children: [
              const Text('Ich merke mir, was sitzt, und gehe zurück, wo es hängt.'),
              const Text(
                'Zuerst ein Zeichen. Daran findet sich das Kind auf der Startseite, '
                'auch ohne lesen zu können.',
              ),
              SignPicker(value: _sign, onChange: (sign) => setState(() => _sign = sign)),
              AddChildForm(name: _name, hint: 'Vorname', submit: 'Weiter', onSubmit: _addChild),
              if (error != null) ErrorText(error),
              const Text(
                'Ein Vorname oder Spitzname reicht. Weitere Kinder kommen im Elternbereich dazu.',
              ),
            ],
          ),
          _Step.pin => EntrySection(
            _first == null ? 'PIN für den Elternbereich' : 'PIN noch einmal',
            children: [
              Text(
                _first == null
                    ? 'Vier Ziffern. Die PIN hält Kinder aus dem Elternbereich. '
                          'Bitte nicht die PIN der Bankkarte.'
                    : 'Zur Sicherheit die gleiche PIN noch einmal.',
              ),
              if (error != null) ErrorText(error),
              Center(
                child: PinPad(
                  value: _pin,
                  onChange: (pin) => setState(() => _pin = pin),
                  onSubmit: _choosePin,
                  submitLabel: 'Weiter',
                ),
              ),
            ],
          ),
          _Step.done => EntrySection(
            'Fertig',
            children: [
              Text(
                'Jetzt ist ${child?.name} dran. Zuerst schaue ich, was ${child?.name} schon kann. '
                'Fehler sind dabei ganz normal.',
              ),
              Btn("Los geht's", kind: BtnKind.primary, onTap: () => widget.onDone(child)),
            ],
          ),
        },
      ],
    );
  }
}

/// Name und Knopf, breit nebeneinander, schmal untereinander.
class AddChildForm extends StatelessWidget {
  const AddChildForm({
    super.key,
    required this.name,
    required this.hint,
    required this.submit,
    required this.onSubmit,
    this.autofocus = true,
  });

  final TextEditingController name;
  final String hint;
  final String submit;
  final VoidCallback onSubmit;
  final bool autofocus;

  @override
  Widget build(BuildContext context) {
    final field = Field(
      controller: name,
      hint: hint,
      maxLength: 30,
      autofocus: autofocus,
      onSubmit: onSubmit,
    );
    final button = Btn(
      submit,
      kind: BtnKind.primary,
      onTap: name.text.trim().isEmpty ? null : onSubmit,
    );
    return MediaQuery.sizeOf(context).width >= 560
        ? Row(
            spacing: 12,
            children: [
              Expanded(child: field),
              button,
            ],
          )
        : Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            spacing: 12,
            children: [field, button],
          );
  }
}
