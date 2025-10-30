import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:traffic_share/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp(isLoggedIn: false));

    // Verify that splash screen or login screen is displayed
    expect(find.byType(MaterialApp), findsOneWidget);
  });

  testWidgets('MyApp creates with isLoggedIn parameter', (WidgetTester tester) async {
    // Test with isLoggedIn = true
    await tester.pumpWidget(const MyApp(isLoggedIn: true));
    await tester.pumpAndSettle();

    expect(find.byType(MaterialApp), findsOneWidget);
  });

  testWidgets('MyApp creates with isLoggedIn = false', (WidgetTester tester) async {
    // Test with isLoggedIn = false
    await tester.pumpWidget(const MyApp(isLoggedIn: false));
    await tester.pumpAndSettle();

    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
