import 'dart:convert';

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
    final response = await _http.get(
      _uri(path),
      headers: _headers(token: token),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> post(
    String path, {
    required Map<String, dynamic> body,
    String? token,
  }) async {
    final response = await _http.post(
      _uri(path),
      headers: _headers(token: token),
      body: jsonEncode(body),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> put(
    String path, {
    required Map<String, dynamic> body,
    String? token,
  }) async {
    final response = await _http.put(
      _uri(path),
      headers: _headers(token: token),
      body: jsonEncode(body),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> delete(
    String path, {
    String? token,
  }) async {
    final response = await _http.delete(
      _uri(path),
      headers: _headers(token: token),
    );
    return _decode(response);
  }

  Uri _uri(String path) {
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse('${AppConfig.apiBaseUrl}$normalizedPath');
  }

  Map<String, String> _headers({String? token}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

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
}
