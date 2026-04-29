import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

class ApiException implements Exception {
  ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

class ApiClient {
  final http.Client _http = http.Client();

  Future<Map<String, dynamic>> get(
    String path, {
    String? token,
  }) async {
    try {
      final response = await _http.get(
        _uri(path),
        headers: _headers(token: token),
      );
      return _decode(response);
    } on SocketException catch (_) {
      throw ApiException(_connectionErrorMessage());
    } on HttpException catch (_) {
      throw ApiException(_connectionErrorMessage());
    }
  }

  Future<Map<String, dynamic>> post(
    String path, {
    required Map<String, dynamic> body,
    String? token,
  }) async {
    try {
      final response = await _http.post(
        _uri(path),
        headers: _headers(token: token),
        body: jsonEncode(body),
      );
      return _decode(response);
    } on SocketException catch (_) {
      throw ApiException(_connectionErrorMessage());
    } on HttpException catch (_) {
      throw ApiException(_connectionErrorMessage());
    }
  }

  Future<Map<String, dynamic>> postMultipart(
    String path, {
    required Map<String, String> fields,
    List<http.MultipartFile> files = const [],
    String? token,
  }) async {
    try {
      final request = http.MultipartRequest('POST', _uri(path));
      request.headers.addAll(_headers(token: token, jsonContentType: false));
      request.fields.addAll(fields);
      request.files.addAll(files);

      final streamedResponse = await _http.send(request);
      final response = await http.Response.fromStream(streamedResponse);
      return _decode(response);
    } on SocketException catch (_) {
      throw ApiException(_connectionErrorMessage());
    } on HttpException catch (_) {
      throw ApiException(_connectionErrorMessage());
    }
  }

  Future<Map<String, dynamic>> put(
    String path, {
    required Map<String, dynamic> body,
    String? token,
  }) async {
    try {
      final response = await _http.put(
        _uri(path),
        headers: _headers(token: token),
        body: jsonEncode(body),
      );
      return _decode(response);
    } on SocketException catch (_) {
      throw ApiException(_connectionErrorMessage());
    } on HttpException catch (_) {
      throw ApiException(_connectionErrorMessage());
    }
  }

  Future<Map<String, dynamic>> delete(
    String path, {
    String? token,
  }) async {
    try {
      final response = await _http.delete(
        _uri(path),
        headers: _headers(token: token),
      );
      return _decode(response);
    } on SocketException catch (_) {
      throw ApiException(_connectionErrorMessage());
    } on HttpException catch (_) {
      throw ApiException(_connectionErrorMessage());
    }
  }

  Uri _uri(String path) {
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse('${AppConfig.apiBaseUrl}$normalizedPath');
  }

  Map<String, String> _headers({
    String? token,
    bool jsonContentType = true,
  }) {
    final headers = <String, String>{
      'Accept': 'application/json',
    };

    if (jsonContentType) {
      headers['Content-Type'] = 'application/json';
    }

    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }

    return headers;
  }

  Map<String, dynamic> _decode(http.Response response) {
    Map<String, dynamic> json = <String, dynamic>{};
    if (response.body.isNotEmpty) {
      final dynamic decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        json = decoded;
      }
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json;
    }

    final detail = json['detail'];
    if (detail is String && detail.isNotEmpty) {
      throw ApiException(detail);
    }
    throw ApiException('Error HTTP ${response.statusCode}');
  }

  String _connectionErrorMessage() {
    return 'No se pudo conectar con el backend en ${AppConfig.apiBaseUrl}. '
        'Verifica la IP y que el celular y la PC estén en la misma red.';
  }
}
