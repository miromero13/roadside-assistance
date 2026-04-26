import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/src/app.dart';

void main() {
  testWidgets('renderiza splash al iniciar', (tester) async {
    await tester.pumpWidget(const AciMobileApp());

    expect(find.text('Inicializando ACI Mobile...'), findsOneWidget);
  });
}
