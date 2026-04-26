class UsuarioAuth {
  UsuarioAuth({
    required this.id,
    required this.nombre,
    required this.apellido,
    required this.email,
    required this.telefono,
    required this.rol,
    required this.activo,
  });

  final String id;
  final String nombre;
  final String apellido;
  final String email;
  final String telefono;
  final String rol;
  final bool activo;

  String get nombreCompleto => '$nombre $apellido';

  factory UsuarioAuth.fromJson(Map<String, dynamic> json) {
    return UsuarioAuth(
      id: json['id'] as String? ?? '',
      nombre: json['nombre'] as String? ?? '',
      apellido: json['apellido'] as String? ?? '',
      email: json['email'] as String? ?? '',
      telefono: json['telefono'] as String? ?? '',
      rol: json['rol'] as String? ?? '',
      activo: json['activo'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'apellido': apellido,
      'email': email,
      'telefono': telefono,
      'rol': rol,
      'activo': activo,
    };
  }
}
