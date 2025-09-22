import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primaryBlue = Color(0xFF06276C);
  static const Color cyan = Color(0xFF06F1E2);
  static const Color lightBlue = Color(0xFFD2F9F5);
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF1D1D1B);

  static const LinearGradient mainGradient = LinearGradient(
    colors: [primaryBlue, cyan],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static ThemeData get theme {
    final base = ThemeData.light();
    return base.copyWith(
      scaffoldBackgroundColor: white,
      primaryColor: primaryBlue,
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryBlue,
        foregroundColor: white,
        elevation: 0,
      ),
      textTheme: TextTheme(
        displayLarge: GoogleFonts.poppins(fontSize: 28, fontWeight: FontWeight.w700, color: primaryBlue),
        titleLarge: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.w600, color: primaryBlue),
        bodyLarge: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w400, color: black),
        bodyMedium: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w400, color: black),
        labelLarge: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w700, color: white),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ButtonStyle(
          padding: MaterialStateProperty.all(const EdgeInsets.symmetric(horizontal: 20, vertical: 14)),
          shape: MaterialStateProperty.all(RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
          backgroundColor: MaterialStateProperty.all(primaryBlue),
          foregroundColor: MaterialStateProperty.all(white),
          textStyle: MaterialStateProperty.all(GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      ),
    );
  }
}
