/// Bild, an dem ein Kind sich erkennt, wie das Zeichen an der Kita-Garderobe.
enum Sign { sun, moon, star, heart, fish, apple, flower, boat }

class Child {
  const Child({required this.id, required this.name, required this.sign});

  factory Child.fromJson(Map<String, dynamic> json) => Child(
    id: json['id'] as String,
    name: json['name'] as String,
    sign: Sign.values.asNameMap()[json['sign']] ?? Sign.sun,
  );

  final String id;
  final String name;
  final Sign sign;
}

/// Eine Antwort zur Auswahl. Das Kind sieht `label`, zurück geht `value` (Zahl oder ID).
class Option {
  const Option({required this.value, required this.label});

  factory Option.fromJson(Map<String, dynamic> json) =>
      Option(value: json['value'] as Object, label: json['label'] as String);

  final Object value;
  final String label;
}

class Task {
  const Task({
    required this.id,
    required this.competency,
    required this.title,
    required this.kind,
    required this.level,
    required this.prompt,
    required this.operands,
    required this.options,
    required this.representations,
    required this.placement,
  });

  factory Task.fromJson(Map<String, dynamic> json) => Task(
    id: json['id'] as String,
    competency: json['competency'] as String,
    title: json['title'] as String,
    kind: json['kind'] as String,
    level: json['level'] as String,
    prompt: json['prompt'] as String,
    operands: json['operands'] as Map<String, dynamic>,
    options: (json['options'] as List?)
        ?.map((o) => Option.fromJson(o as Map<String, dynamic>))
        .toList(),
    representations: (json['representations'] as List).cast<String>(),
    placement: json['placement'] as bool,
  );

  final String id;
  final String competency;
  final String title;
  final String kind;
  final String level;
  final String prompt;

  /// Zahlen und IDs, die das Bild zur Aufgabe liest.
  final Map<String, dynamic> operands;

  /// null: freie Eingabe per Zahlenblock.
  final List<Option>? options;
  final List<String> representations;

  /// Aufgabe aus dem Standortcheck.
  final bool placement;

  /// Operand als Zahl. Fehlt er, 0.
  num number(String key) => switch (operands[key]) {
    final num n => n,
    final String s => num.tryParse(s) ?? 0,
    _ => 0,
  };

  /// Operand als Text. Fehlt er, leer.
  String text(String key) => '${operands[key] ?? ''}';

  /// Wie das Kind eine Lösung sieht: bei Auswahl das Label, sonst die Zahl.
  String labelOf(Object answer) =>
      options?.where((o) => o.value == answer).firstOrNull?.label ?? '$answer';
}

class AnswerResult {
  const AnswerResult({
    required this.correct,
    required this.answer,
    required this.retry,
    required this.backtrackedTo,
    required this.mastered,
  });

  factory AnswerResult.fromJson(Map<String, dynamic> json) => AnswerResult(
    correct: json['correct'] as bool,
    answer: json['answer'],
    retry: json['retry'] as bool,
    backtrackedTo: json['backtracked_to'] as String?,
    mastered: json['mastered'] as bool,
  );

  final bool correct;

  /// Die Lösung. null, solange ein zweiter Versuch offen ist.
  final Object? answer;

  /// Das Kind darf es noch einmal versuchen.
  final bool retry;
  final String? backtrackedTo;

  /// Mit dieser Antwort sitzt die Kompetenz. Nie im Standortcheck.
  final bool mastered;
}

enum MasteryStatus {
  mastered('sitzt'),
  inProgress('in Arbeit'),
  notStarted('kommt noch');

  const MasteryStatus(this.label);

  final String label;
}

class MasteryRow {
  const MasteryRow({
    required this.competency,
    required this.title,
    required this.area,
    required this.pKnown,
    required this.status,
    required this.practicable,
  });

  factory MasteryRow.fromJson(Map<String, dynamic> json) => MasteryRow(
    competency: json['competency'] as String,
    title: json['title'] as String,
    area: json['area'] as String,
    pKnown: (json['p_known'] as num).toDouble(),
    status: switch (json['status']) {
      'mastered' => MasteryStatus.mastered,
      'in_progress' => MasteryStatus.inProgress,
      _ => MasteryStatus.notStarted,
    },
    practicable: json['practicable'] as bool,
  );

  final String competency;
  final String title;
  final String area;
  final double pKnown;
  final MasteryStatus status;

  /// false: Olli hat dafür noch keine Aufgaben.
  final bool practicable;
}

/// Stand gegenüber dem Lehrplan: Ziel bis Ende der Jahrgangsstufe.
class Progress {
  const Progress({
    required this.curriculum,
    required this.grade,
    required this.goal,
    required this.checkable,
    required this.mastered,
    required this.inProgress,
    required this.placementDone,
  });

  factory Progress.fromJson(Map<String, dynamic> json) => Progress(
    curriculum: json['curriculum'] as String,
    grade: json['grade'] as int,
    goal: json['goal'] as int,
    checkable: json['checkable'] as int,
    mastered: json['mastered'] as int,
    inProgress: json['in_progress'] as int,
    placementDone: json['placement_done'] as bool,
  );

  final String curriculum;
  final int grade;
  final int goal;
  final int checkable;
  final int mastered;
  final int inProgress;
  final bool placementDone;
}
