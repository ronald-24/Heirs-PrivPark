import 'package:flutter/material.dart';

/// 🎨 Couleurs globales de l'application
class AppColors {
  static const Color primary = Color(0xFF1976D2); // Bleu principal
  static const Color secondary = Color(0xFF42A5F5); // Bleu clair
  static const Color background = Color(0xFFF5F5F5); // Gris clair
  static const Color textPrimary = Color(0xFF333333); // Texte principal
  static const Color textSecondary = Color(0xFF777777); // Texte secondaire
  static const Color error = Color(0xFFD32F2F); // Rouge
}

/// 📝 Styles de texte globaux
class AppTextStyles {
  static const TextStyle button = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.bold,
    color: Colors.white,
  );

  static const TextStyle title = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
  );

  static const TextStyle subtitle = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
  );

  static const TextStyle body = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: AppColors.textPrimary,
  );
}
