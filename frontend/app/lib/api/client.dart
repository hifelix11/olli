import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'models.dart';

/// Fehler vom Backend. `code` ist der Fehlercode, etwa `invalid_credentials`.
class ApiError implements Exception {
  const ApiError(this.status, this.code);

  final int status;
  final String code;

  @override
  String toString() => '$status: $code';
}

/// Tokens des Elternkontos. Nur das Backend prüft sie.
typedef Session = ({String access, String refresh});

const _sessionKey = 'olli.session';

/// Alle Aufrufe ans Backend. Das Frontend spricht nie direkt mit Supabase.
class Api {
  Api(this.base, {http.Client? client, FlutterSecureStorage? storage})
    : _client = client ?? http.Client(),
      _storage = storage ?? const FlutterSecureStorage();

  final String base;
  final http.Client _client;
  final FlutterSecureStorage _storage;

  Session? _session;
  Future<bool>? _refreshing;

  /// Meldet, wenn die Anmeldung endet: abgemeldet oder abgelaufen.
  void Function() onSignOut = () {};

  bool get signedIn => _session != null;

  /// Lädt die gespeicherte Anmeldung. Einmal beim Start.
  Future<void> restore() async {
    try {
      final saved = await _storage.read(key: _sessionKey);
      if (saved != null) _session = _sessionFrom(jsonDecode(saved));
    } catch (_) {
      // Kein Speicher: Die Anmeldung gilt dann nur, bis die App schließt.
    }
  }

  Future<void> _setSession(Session? next) async {
    _session = next;
    try {
      if (next == null) {
        await _storage.delete(key: _sessionKey);
      } else {
        final saved = {'access_token': next.access, 'refresh_token': next.refresh};
        await _storage.write(key: _sessionKey, value: jsonEncode(saved));
      }
    } catch (_) {
      // Siehe restore.
    }
  }

  Session _sessionFrom(Object? json) {
    final map = json as Map<String, dynamic>;
    return (access: map['access_token'] as String, refresh: map['refresh_token'] as String);
  }

  Future<http.Response> _send(String method, String path, Object? body) async {
    final request = http.Request(method, Uri.parse(base + path));
    request.headers['content-type'] = 'application/json';
    final session = _session;
    if (session != null) request.headers['authorization'] = 'Bearer ${session.access}';
    if (body != null) request.body = jsonEncode(body);
    return http.Response.fromStream(await _client.send(request));
  }

  bool _ok(http.Response response) => response.statusCode >= 200 && response.statusCode < 300;

  /// Neue Tokens holen. Parallele Aufrufe teilen sich eine Anfrage.
  Future<bool> _refresh(String token) => _refreshing ??= () async {
    try {
      final response = await _send('POST', '/auth/refresh', {'refresh_token': token});
      if (_ok(response)) {
        await _setSession(_sessionFrom(_json(response)));
      } else if (response.statusCode == 401) {
        logout();
      }
      return _ok(response);
    } finally {
      _refreshing = null;
    }
  }();

  Object? _json(http.Response response) => jsonDecode(utf8.decode(response.bodyBytes));

  Future<Object?> _request(String method, String path, [Object? body]) async {
    var response = await _send(method, path, body);
    final session = _session;
    if (response.statusCode == 401 && session != null && await _refresh(session.refresh)) {
      response = await _send(method, path, body);
    }
    if (_ok(response)) return _json(response);
    Object? detail;
    try {
      detail = (_json(response) as Map<String, dynamic>)['detail'];
    } catch (_) {
      // Antwort ohne JSON.
    }
    throw ApiError(
      response.statusCode,
      detail is String ? detail : response.reasonPhrase ?? 'error',
    );
  }

  // ---------- Elternkonto ----------

  Future<void> login(String email, String password) async {
    final body = {'email': email, 'password': password};
    await _setSession(_sessionFrom(await _request('POST', '/auth/login', body)));
  }

  /// false: Das Konto muss erst per E-Mail bestätigt werden.
  Future<bool> signup(String email, String password) async {
    final body = {'email': email, 'password': password};
    final next = await _request('POST', '/auth/signup', body);
    if (next != null) await _setSession(_sessionFrom(next));
    return next != null;
  }

  void logout() {
    _setSession(null);
    onSignOut();
  }

  bool _pinSet(Object? account) => (account as Map<String, dynamic>)['pin_set'] as bool;

  /// Hat das Konto eine PIN für den Elternbereich?
  Future<bool> pinSet() async => _pinSet(await _request('GET', '/account'));

  Future<void> setPin(String pin) => _request('PUT', '/account/pin', {'pin': pin});

  Future<bool> checkPin(String pin) async {
    final result = await _request('POST', '/account/pin/check', {'pin': pin});
    return (result as Map<String, dynamic>)['correct'] as bool;
  }

  /// PIN vergessen. Danach abmelden, nach dem Login kommt eine neue PIN.
  Future<void> resetPin() => _request('DELETE', '/account/pin');

  // ---------- Kinder ----------

  Future<List<Child>> children() async {
    final list = await _request('GET', '/children') as List;
    return [for (final child in list) Child.fromJson(child as Map<String, dynamic>)];
  }

  Future<Child> createChild(String name, Sign sign) async {
    final body = {'name': name, 'sign': sign.name};
    return Child.fromJson(await _request('POST', '/children', body) as Map<String, dynamic>);
  }

  /// null: Das Kind kann alles, was Olli üben kann.
  Future<Task?> nextTask(String childId) async {
    final task = await _request('GET', '/children/$childId/next-task');
    return task == null ? null : Task.fromJson(task as Map<String, dynamic>);
  }

  /// `answer` null: "Weiß ich noch nicht".
  Future<AnswerResult> answer(String childId, String taskId, Object? answer) async {
    final body = {'task_id': taskId, 'answer': answer};
    final result = await _request('POST', '/children/$childId/answers', body);
    return AnswerResult.fromJson(result as Map<String, dynamic>);
  }

  Future<List<MasteryRow>> mastery(String childId) async {
    final list = await _request('GET', '/children/$childId/mastery') as List;
    return [for (final row in list) MasteryRow.fromJson(row as Map<String, dynamic>)];
  }

  Future<Progress> progress(String childId) async {
    final result = await _request('GET', '/children/$childId/progress');
    return Progress.fromJson(result as Map<String, dynamic>);
  }
}
