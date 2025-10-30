import 'package:flutter_test/flutter_test.dart';
import 'package:traffic_share/main.dart';

void main() {
  testWidgets('renders splash screen when user is not logged in', (tester) async {
    await tester.pumpWidget(const MyApp(isLoggedIn: false));
    await tester.pump();

    expect(find.text('Traffic Share'), findsWidgets);
  });
}
