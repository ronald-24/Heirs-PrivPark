#!/usr/bin/env python3
"""
Script de test pour l'authentification Firebase
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    """Test de l'endpoint de santé"""
    print("🔍 Test de l'endpoint /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_verify_token_invalid():
    """Test avec un token invalide"""
    print("\n🔍 Test de /auth/verify-token avec token invalide...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-token",
            headers={"Authorization": "Bearer invalid_token"}
        )
        print(f"✅ Status attendu (401): {response.status_code}")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_me_endpoint_no_token():
    """Test /me sans token"""
    print("\n🔍 Test de /users/me sans token...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/me")
        print(f"✅ Status attendu (401): {response.status_code}")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_with_real_token(token):
    """Test avec un vrai token Firebase"""
    print(f"\n🔍 Test avec un vrai token Firebase...")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test verify-token
        print("  📝 Test /auth/verify-token...")
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-token",
            headers=headers
        )
        print(f"    ✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ User ID: {data.get('user_id')}")
            print(f"    ✅ Firebase UID: {data.get('firebase_uid')}")
            print(f"    ✅ Email: {data.get('email')}")

        # Test login
        print("  📝 Test /auth/login...")
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            headers=headers
        )
        print(f"    ✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(
                f"    ✅ User: {data.get('display_name', 'N/A')} ({data.get('email', 'N/A')})")

        # Test logout
        print("  📝 Test /auth/logout...")
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        print(f"    ✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    ✅ Message: {response.json().get('message')}")

        # Test /auth/me
        print("  📝 Test /auth/me...")
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=headers
        )
        print(f"    ✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(
                f"    ✅ User: {data.get('display_name', 'N/A')} (ID: {data.get('id')})")

        # Test /users/me (ancien endpoint)
        print("  📝 Test /users/me...")
        response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers=headers
        )
        print(f"    ✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(
                f"    ✅ User: {data.get('display_name', 'N/A')} (ID: {data.get('id')})")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    print("🚀 Test de l'authentification Firebase Backend")
    print("=" * 50)

    # Tests de base
    health_ok = test_health()
    token_invalid_ok = test_verify_token_invalid()
    me_no_token_ok = test_me_endpoint_no_token()

    print(f"\n📊 Résultats des tests de base:")
    print(f"   Health endpoint: {'✅' if health_ok else '❌'}")
    print(f"   Token invalide: {'✅' if token_invalid_ok else '❌'}")
    print(f"   /me sans token: {'✅' if me_no_token_ok else '❌'}")

    # Test avec un vrai token (si fourni)
    print(f"\n🔑 Pour tester avec un vrai token Firebase:")
    print(f"   1. Connectez-vous via l'app Flutter")
    print(f"   2. Récupérez l'idToken depuis Firebase Auth")
    print(f"   3. Lancez: python test_auth.py YOUR_TOKEN_HERE")

    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        real_token_ok = test_with_real_token(token)
        print(f"   Token réel: {'✅' if real_token_ok else '❌'}")


if __name__ == "__main__":
    main()
