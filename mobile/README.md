# Mobile

Aplicacion mobile del proyecto Roadside Assistance, creada con Flutter y gestionada con FVM.

## Requisitos

- Flutter via FVM
- Xcode (iOS) y/o Android Studio (Android)

## Entrar al proyecto

```bash
cd mobile
```

## Instalar dependencias

```bash
fvm flutter pub get
```

## Ejecutar en desarrollo

```bash
fvm flutter run
```

Para probar en un celular físico, arranca Flutter apuntando a la IP real de tu PC en la misma red:

```bash
fvm flutter run --dart-define=API_BASE_URL=http://<IP-DE-TU-PC>:8000/api
```

Si cambias de red o de computadora, vuelve a pasar ese valor. El login usa esa URL para hablar con FastAPI.

## Comandos utiles

```bash
fvm flutter devices
fvm flutter doctor
fvm flutter test
fvm flutter build apk
fvm flutter build ios
```

## Notas

- El proyecto usa la version configurada en `.fvmrc`.
- La carpeta `.fvm/` queda ignorada por git.
- En Android emulator, `10.0.2.2` apunta a la PC anfitriona; en celular físico necesitas la IP LAN real.
