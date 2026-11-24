import 'package:flutter/material.dart' show Tooltip;
import 'package:flutter/widgets.dart';

import '../api/models.dart';
import '../app_state.dart';
import '../child/sign.dart';
import '../start/onboarding_page.dart';
import '../ui/controls.dart';
import '../ui/icons.dart';
import '../ui/sketch.dart';
import '../ui/tokens.dart';
import 'pin_pad.dart';
import 'sign_picker.dart';

const _offline = 'Olli erreicht den Server nicht.';

const _areas = {
  'numbers_operations': 'Zahlen und Rechnen',
  'space_shape': 'Formen und Raum',
  'quantities_measurement': 'Größen und Messen',
  'data_chance': 'Daten und Zufall',
};

final _summary = Tokens.body.copyWith(color: Tokens.inkSoft);

/// Elternbereich hinter der PIN: Kinder anlegen, Jahresziel und Karte des Lernstands.
class ParentArea extends StatefulWidget {
  const ParentArea({super.key, required this.app, required this.onExit});

  final AppState app;
  final VoidCallback onExit;

  @override
  State<ParentArea> createState() => _ParentAreaState();
}

class _ParentAreaState extends State<ParentArea> {
  final _name = TextEditingController();
  String _pin = '';
  bool _open = false;
  bool _wrong = false;
  bool _forgot = false;
  Child? _selected;
  late Sign _sign;
  List<MasteryRow>? _rows;
  Progress? _progress;
  String? _error;

  List<Child> get _kids => widget.app.kids ?? const [];

  @override
  void initState() {
    super.initState();
    _name.addListener(() => setState(() {}));
    _selected = _kids.firstOrNull;
    // Vorschlag: das erste Zeichen, das noch kein Geschwisterkind hat.
    _sign = freeSign(_kids.map((k) => k.sign));
  }

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  Future<void> _check() async {
    final pin = _pin;
    setState(() => _pin = '');
    try {
      final correct = await widget.app.api.checkPin(pin);
      if (!mounted) return;
      setState(() {
        _open = correct;
        _wrong = !correct;
        _error = null;
      });
      if (correct) _load();
    } catch (_) {
      if (mounted) setState(() => _error = _offline);
    }
  }

  /// Neue PIN nur nach Login mit Passwort: PIN löschen, abmelden, das Onboarding fragt danach.
  Future<void> _resetPin() async {
    try {
      await widget.app.api.resetPin();
      widget.app.api.logout();
    } catch (_) {
      if (mounted) setState(() => _error = _offline);
    }
  }

  Future<void> _load() async {
    final child = _selected;
    if (child == null) return;
    try {
      final rows = await widget.app.api.mastery(child.id);
      final progress = await widget.app.api.progress(child.id);
      if (!mounted || _selected?.id != child.id) return;
      setState(() {
        _rows = rows;
        _progress = progress;
      });
    } catch (error) {
      if (mounted) setState(() => _error = '$error');
    }
  }

  void _select(Child child) {
    setState(() {
      _selected = child;
      _rows = null;
      _progress = null;
    });
    _load();
  }

  Future<void> _add() async {
    final name = _name.text.trim();
    if (name.isEmpty) return;
    try {
      final child = await widget.app.api.createChild(name, _sign);
      widget.app.addChild(child);
      if (!mounted) return;
      _name.clear();
      setState(() {
        _sign = freeSign(_kids.map((k) => k.sign));
        _error = null;
      });
      _select(child);
    } catch (error) {
      if (mounted) setState(() => _error = '$_offline $error');
    }
  }

  @override
  Widget build(BuildContext context) => _open ? _area(context) : _lock();

  Widget _lock() {
    final error = _error;
    return CenterPage(
      children: [
        Container(
          width: 88,
          height: 88,
          alignment: Alignment.center,
          decoration: const BoxDecoration(color: Tokens.board, shape: BoxShape.circle),
          child: const OlliIcon(IconName.lock, size: 44),
        ),
        const PageTitle('Elternbereich'),
        const Text('Bitte PIN eingeben.'),
        if (_wrong) const ErrorText('Die PIN stimmt nicht.'),
        if (error != null) ErrorText(error),
        PinPad(
          value: _pin,
          onChange: (pin) => setState(() => _pin = pin),
          onSubmit: _check,
          submitLabel: 'Öffnen',
        ),
        if (_forgot) ...[
          const Text('Für eine neue PIN mit E-Mail und Passwort neu anmelden.'),
          Btn('Abmelden und neue PIN wählen', onTap: _resetPin),
        ] else
          Btn('PIN vergessen?', kind: BtnKind.quiet, onTap: () => setState(() => _forgot = true)),
        Btn('Zurück zum Start', kind: BtnKind.quiet, onTap: widget.onExit),
      ],
    );
  }

  Widget _area(BuildContext context) {
    final compact = isCompact(context);
    final selected = _selected;
    final rows = _rows;
    final progress = _progress;
    final error = _error;
    return SafeArea(
      child: SingleChildScrollView(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1040),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 24, 20, 72),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                spacing: 20,
                children: [
                  Wrap(
                    alignment: WrapAlignment.spaceBetween,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      Text('Elternbereich', style: heading(36)),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Btn('Zurück zum Start', kind: BtnKind.quiet, onTap: widget.onExit),
                          Btn('Abmelden', kind: BtnKind.quiet, onTap: widget.app.api.logout),
                        ],
                      ),
                    ],
                  ),
                  _Panel(
                    compact: compact,
                    children: [
                      Text('Kinder', style: heading(26)),
                      if (_kids.isNotEmpty)
                        Wrap(
                          spacing: 10,
                          runSpacing: 10,
                          children: [for (final child in _kids) _tab(child)],
                        ),
                      Text(
                        'Jedes Kind bekommt ein Zeichen. Daran findet es sich auf der Startseite, '
                        'auch ohne lesen zu können.',
                        style: _summary,
                      ),
                      SignPicker(value: _sign, onChange: (sign) => setState(() => _sign = sign)),
                      AddChildForm(
                        name: _name,
                        hint: 'Name',
                        submit: 'Kind anlegen',
                        onSubmit: _add,
                        autofocus: false,
                      ),
                    ],
                  ),
                  if (error != null) ErrorText(error),
                  if (selected != null && rows != null && progress != null)
                    _Panel(compact: compact, children: _mastery(context, selected, rows, progress)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _tab(Child child) {
    final on = child.id == _selected?.id;
    return Tap(
      onTap: () => _select(child),
      builder: (_) => Container(
        height: 56,
        padding: const EdgeInsets.fromLTRB(8, 0, 22, 0),
        decoration: BoxDecoration(
          color: on ? Tokens.ink : Tokens.chalk,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          spacing: 10,
          children: [
            SignIcon(child.sign, size: 40),
            Text(
              child.name,
              style: jost(19, FontWeight.w700, color: on ? Tokens.white : Tokens.ink),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _mastery(
    BuildContext context,
    Child child,
    List<MasteryRow> rows,
    Progress progress,
  ) {
    final compact = isCompact(context);
    // Breite der Karte: Seite minus Ränder der Seite und des Kastens.
    final width = MediaQuery.sizeOf(context).width.clamp(0.0, 1040.0) - 40 - (compact ? 36 : 56);
    final columns = compact ? 2 : ((width + 10) / 170).floor().clamp(1, 99);
    final share = progress.checkable == 0 ? 0.0 : progress.mastered / progress.checkable;
    return [
      Text('Lernstand von ${child.name}', style: heading(26)),
      _h3('Ziel bis Ende der Jahrgangsstufe ${progress.grade}'),
      Semantics(
        label: '${progress.mastered} von ${progress.checkable} Fähigkeiten sitzen',
        child: Align(
          alignment: Alignment.centerLeft,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 560),
            child: _Bar(share, height: 20, color: Tokens.green, track: Tokens.chalk),
          ),
        ),
      ),
      Text(
        'Zum Ziel gehören ${progress.goal} Fähigkeiten, ${progress.checkable} davon kann Olli '
        'prüfen. Davon sitzen ${progress.mastered}, ${progress.inProgress} sind in Arbeit. '
        'Quelle: ${progress.curriculum}.',
        style: _summary,
      ),
      if (!progress.placementDone)
        Text(
          'Olli schaut noch, was ${child.name} schon kann. Nach den ersten Aufgaben zeigt '
          'die Karte mehr.',
          style: _summary,
        ),
      _h3('Karte'),
      Text('Blass gezeichnete Fähigkeiten kann Olli noch nicht üben.', style: _summary),
      Wrap(
        spacing: 20,
        runSpacing: 8,
        children: [for (final status in MasteryStatus.values) _legend(status)],
      ),
      for (final MapEntry(key: area, value: title) in _areas.entries) ...[
        _h3(title),
        _grid(columns, [
          for (final row in rows)
            if (row.area == area) _cell(row, compact),
        ]),
      ],
    ];
  }

  Widget _h3(String text) => Padding(
    padding: const EdgeInsets.only(top: 12),
    child: Text(text, style: heading(19)),
  );

  Widget _legend(MasteryStatus status) => Row(
    mainAxisSize: MainAxisSize.min,
    spacing: 6,
    children: [
      Container(
        width: 14,
        height: 14,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: switch (status) {
            MasteryStatus.mastered => Tokens.green,
            MasteryStatus.inProgress => Tokens.sun,
            MasteryStatus.notStarted => null,
          },
          border: status == MasteryStatus.notStarted
              ? Border.all(color: Tokens.line, width: 2)
              : null,
        ),
      ),
      Text(status.label, style: jost(15, FontWeight.w400, color: Tokens.inkSoft)),
    ],
  );

  /// Zeilen mit gleich hohen Zellen.
  Widget _grid(int columns, List<Widget> cells) => Column(
    spacing: 10,
    children: [
      for (var i = 0; i < cells.length; i += columns)
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            spacing: 10,
            children: [
              for (var j = i; j < i + columns; j++)
                Expanded(child: j < cells.length ? cells[j] : const SizedBox()),
            ],
          ),
        ),
    ],
  );

  Widget _cell(MasteryRow row, bool compact) {
    final (background, bar) = switch (row.status) {
      MasteryStatus.mastered => (Tokens.greenSoft, Tokens.green),
      MasteryStatus.inProgress => (Tokens.sunSoft, const Color(0xFFE0A200)),
      MasteryStatus.notStarted => (Tokens.chalk, Tokens.ink),
    };
    final percent = (row.pKnown * 100).round();
    final content = Container(
      constraints: BoxConstraints(minHeight: compact ? 80 : 92),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        spacing: 10,
        children: [
          Text(
            row.title,
            style: jost(
              15,
              FontWeight.w400,
              height: 1.3,
              color: row.status == MasteryStatus.notStarted ? Tokens.inkSoft : Tokens.ink,
            ),
          ),
          _Bar(row.pKnown, height: 6, color: bar, track: Tokens.ink.withValues(alpha: 0.1)),
        ],
      ),
    );
    return Tooltip(
      message: row.practicable ? '${row.status.label}, $percent %' : 'Kann Olli noch nicht üben',
      child: row.practicable
          ? DecoratedBox(
              decoration: BoxDecoration(color: background, borderRadius: BorderRadius.circular(18)),
              child: content,
            )
          : Opacity(
              opacity: 0.5,
              child: DashedBorder(color: Tokens.line, width: 2, radius: 18, child: content),
            ),
    );
  }
}

/// Weißer Kasten im Elternbereich.
class _Panel extends StatelessWidget {
  const _Panel({required this.children, required this.compact});

  final List<Widget> children;
  final bool compact;

  @override
  Widget build(BuildContext context) => Container(
    padding: compact
        ? const EdgeInsets.symmetric(horizontal: 18, vertical: 22)
        : const EdgeInsets.all(28),
    decoration: BoxDecoration(color: Tokens.board, borderRadius: BorderRadius.circular(28)),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, spacing: 16, children: children),
  );
}

/// Balken, gefüllt bis zu einem Anteil zwischen 0 und 1.
class _Bar extends StatelessWidget {
  const _Bar(this.share, {required this.height, required this.color, required this.track});

  final double share;
  final double height;
  final Color color;
  final Color track;

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(999),
    child: Container(
      height: height,
      color: track,
      alignment: Alignment.centerLeft,
      child: FractionallySizedBox(
        widthFactor: share.clamp(0, 1),
        child: DecoratedBox(
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(999)),
          child: const SizedBox.expand(),
        ),
      ),
    ),
  );
}
