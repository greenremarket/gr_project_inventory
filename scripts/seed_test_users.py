#!/usr/bin/env python3
"""
seed_test_users.py — Gestion des utilisateurs internes de test (CT202 uniquement)

Ces utilisateurs existent en base mais sont archivés (active=False) pour ne
pas consommer de sièges Odoo Enterprise. Ce script permet de les re-activer
pour des sessions de dev/test, puis de les ré-archiver ensuite.

IMPORTANT : ne JAMAIS exécuter --activate sur CT201 PROD.
Les users de test coûtent des sièges licence Enterprise.

Usage :
    # Activer pour une session de dev (CT202 uniquement)
    python scripts/seed_test_users.py --activate

    # Ré-archiver après la session de dev
    python scripts/seed_test_users.py --archive

    # Status : voir l'état actuel
    python scripts/seed_test_users.py --status

    # Cibler un serveur différent (défaut : CT202)
    python scripts/seed_test_users.py --activate --url http://192.168.21.202:8069
"""

import argparse
import sys
import xmlrpc.client

# ── Config ──────────────────────────────────────────────────────────────────
DEFAULT_URL = "http://192.168.21.202:8069"   # CT202 test — JAMAIS CT201 prod
DB = "greenremarket"
ADMIN_LOGIN = "admin@greenremarket.fr"
ADMIN_PASSWORD = "Payasugo187!odoo"

PROD_URL = "http://192.168.21.201:8069"  # CT201 prod — bloqué dans ce script

TEST_USERS = [
    {
        "login": "operateur@greenremarket.fr",
        "name": "Opérateur GRM",
        "password": "TestGrm2026!",
        "role": "operateur (groupe base.group_user)",
    },
    {
        "login": "superviseur@greenremarket.fr",
        "name": "Superviseur GRM",
        "password": "TestGrm2026!",
        "role": "superviseur (groupe base.group_user)",
    },
]
# ────────────────────────────────────────────────────────────────────────────


def get_rpc(url):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(DB, ADMIN_LOGIN, ADMIN_PASSWORD, {})
    if not uid:
        print(f"ERREUR : authentification échouée sur {url}")
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def x(model, method, *args, **kwargs):
        return models.execute_kw(DB, uid, ADMIN_PASSWORD, model, method, *args, **kwargs)

    return x


def status(x):
    logins = [u["login"] for u in TEST_USERS]
    users = x(
        "res.users",
        "search_read",
        [[["login", "in", logins], ["active", "in", [True, False]]]],
        {"fields": ["login", "name", "active"]},
    )
    print(f"\n{'LOGIN':<40} {'NOM':<25} ÉTAT")
    print("-" * 75)
    for u in users:
        state = "✓ ACTIF" if u["active"] else "✗ archivé"
        print(f"{u['login']:<40} {u['name']:<25} {state}")

    total_internal = x(
        "res.users",
        "search_count",
        [[["active", "=", True], ["share", "=", False]]],
    )
    print(f"\nTotal utilisateurs internes actifs : {total_internal}")


def set_active(x, active: bool):
    logins = [u["login"] for u in TEST_USERS]
    ids = x(
        "res.users",
        "search",
        [[["login", "in", logins], ["active", "in", [True, False]]]],
    )
    if not ids:
        print("ERREUR : aucun des users de test trouvé en base.")
        sys.exit(1)

    x("res.users", "write", [ids, {"active": active}])
    action = "activés" if active else "archivés"
    print(f"{len(ids)} user(s) {action} : {logins}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--activate", action="store_true", help="Re-active les users de test (CT202 uniquement)")
    group.add_argument("--archive", action="store_true", help="Archive les users de test (libère des sièges)")
    group.add_argument("--status", action="store_true", help="Affiche l'état actuel")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"URL Odoo cible (défaut: {DEFAULT_URL})")
    args = parser.parse_args()

    if args.activate and PROD_URL in args.url:
        print("REFUSÉ : impossible d'activer des users de test sur la prod CT201.")
        print("Ces utilisateurs consomment des sièges Odoo Enterprise payants.")
        sys.exit(1)

    print(f"Cible : {args.url}")
    x = get_rpc(args.url)

    if args.status:
        status(x)
    elif args.activate:
        print("\n⚠  Activation des users de test — penser à ré-archiver après la session !")
        set_active(x, True)
        status(x)
    elif args.archive:
        set_active(x, False)
        status(x)


if __name__ == "__main__":
    main()
