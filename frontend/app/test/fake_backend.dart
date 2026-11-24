import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:olli/api/client.dart';

/// Eine Aufgabe, wie das Backend sie schickt.
Map<String, dynamic> taskJson(
  String id, {
  String kind = 'addition',
  String title = 'Plus bis 20',
  String prompt = '8 + 5 = ?',
  Map<String, dynamic> operands = const {'a': 8, 'b': 5},
  List<Map<String, dynamic>>? options,
  List<String> representations = const ['plain'],
  bool placement = false,
}) => {
  'id': id,
  'competency': 'c_$kind',
  'title': title,
  'kind': kind,
  'level': 'medium',
  'prompt': prompt,
  'operands': operands,
  'options': options,
  'representations': representations,
  'placement': placement,
};

Map<String, dynamic> resultJson({
  bool correct = true,
  Object? answer = 13,
  bool retry = false,
  String? backtrackedTo,
  bool mastered = false,
}) => {
  'correct': correct,
  'answer': answer,
  'retry': retry,
  'p_known': 0.5,
  'backtracked_to': backtrackedTo,
  'mastered': mastered,
};

/// Backend im Test: Aufgaben und Ergebnisse der Reihe nach, feste Kinder.
class FakeBackend {
  FakeBackend({
    this.tasks = const [],
    this.results = const [],
    this.kids = const [],
    this.pinSet = true,
  });

  /// null: nichts mehr zu üben.
  final List<Map<String, dynamic>?> tasks;
  final List<Map<String, dynamic>> results;
  final List<Map<String, dynamic>> kids;
  final bool pinSet;

  int _task = 0;
  int _result = 0;

  /// Was die App geschickt hat: "POST /children/k1/answers {...}".
  final sent = <String>[];

  /// Angemeldeter Client. Die Tokens liegen im Speicher des Tests.
  Future<Api> api({bool signedIn = true}) async {
    FlutterSecureStorage.setMockInitialValues({
      if (signedIn) 'olli.session': jsonEncode({'access_token': 'a', 'refresh_token': 'r'}),
    });
    final api = Api('http://test', client: MockClient(_handle));
    await api.restore();
    return api;
  }

  Future<http.Response> _handle(http.Request request) async {
    final path = request.url.path;
    sent.add('${request.method} $path ${request.body}'.trim());
    Object? body;
    if (path == '/children') {
      body = kids;
    } else if (path == '/account') {
      body = {'pin_set': pinSet};
    } else if (path == '/account/pin/check') {
      body = {'correct': jsonDecode(request.body)['pin'] == '1234'};
    } else if (path.endsWith('/next-task')) {
      body = _task < tasks.length ? tasks[_task++] : null;
    } else if (path.endsWith('/answers')) {
      body = results[_result++];
    } else if (path.endsWith('/mastery')) {
      body = masteryJson;
    } else if (path.endsWith('/progress')) {
      body = {
        'curriculum': 'de-by/math-1',
        'grade': 1,
        'goal': 68,
        'checkable': 66,
        'mastered': 12,
        'in_progress': 5,
        'placement_done': true,
      };
    } else {
      return http.Response('{"detail":"not_found"}', 404);
    }
    return http.Response.bytes(
      utf8.encode(jsonEncode(body)),
      200,
      headers: {'content-type': 'application/json'},
    );
  }
}

Map<String, dynamic> _row(
  String title,
  String area,
  double p,
  String status, [
  bool practicable = true,
]) => {
  'competency': title,
  'title': title,
  'area': area,
  'p_known': p,
  'status': status,
  'practicable': practicable,
};

final masteryJson = [
  _row('Zahlwortreihe bis 10', 'numbers_operations', 0.98, 'mastered'),
  _row('Mengen bis 10 zählen', 'numbers_operations', 0.97, 'mastered'),
  _row('Plus bis 10', 'numbers_operations', 0.62, 'in_progress'),
  _row('Minus bis 10', 'numbers_operations', 0.3, 'in_progress'),
  _row('Plus mit Zehnerübergang', 'numbers_operations', 0.1, 'not_started'),
  _row('Sachaufgaben lösen', 'numbers_operations', 0.1, 'not_started', false),
  _row('Formen benennen', 'space_shape', 0.96, 'mastered'),
  _row('Muster fortsetzen', 'space_shape', 0.2, 'not_started'),
  _row('Uhrzeit: volle Stunden', 'quantities_measurement', 0.5, 'in_progress'),
  _row('Säulendiagramm lesen', 'data_chance', 0.1, 'not_started'),
];
