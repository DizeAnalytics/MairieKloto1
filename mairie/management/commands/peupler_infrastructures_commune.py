"""
Commande Django pour peupler la base avec des infrastructures géolocalisées
(`InfrastructureCommune`) rattachées à la cartographie de la commune active.

Deux modes :
- import depuis un fichier JSON (avec lat/lng réels)
- génération automatique à partir des listes texte de `CartographieCommune`

Usage :
  python manage.py peupler_infrastructures_commune
  python manage.py peupler_infrastructures_commune --from-json infrastructures.json
  python manage.py peupler_infrastructures_commune --clear --force
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

from django.core.management.base import BaseCommand

from mairie.models import ConfigurationMairie, InfrastructureCommune


SIX_DP = Decimal("0.000001")


@dataclass(frozen=True)
class _InfraItem:
    type_infrastructure: str
    nom: str
    latitude: Decimal
    longitude: Decimal
    description: str = ""
    adresse: str = ""
    est_active: bool = True


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"Valeur décimale invalide: {value!r}") from exc


def _quantize_6dp(d: Decimal) -> Decimal:
    return d.quantize(SIX_DP)


def _valid_types() -> set[str]:
    return {choice[0] for choice in InfrastructureCommune.TYPE_INFRASTRUCTURE_CHOICES}


def _spiral_offset(idx: int, base_radius: float) -> tuple[float, float]:
    """
    Produit un léger offset pseudo-régulier autour du centre.
    idx démarre à 0.
    """
    # Spirale (angle d'or) pour éviter les points alignés.
    golden_angle_deg = 137.50776405003785
    angle = math.radians(idx * golden_angle_deg)
    radius = base_radius * (1.0 + (idx * 0.15))
    return (radius * math.cos(angle), radius * math.sin(angle))


def _from_cartographie_text(config: ConfigurationMairie) -> list[_InfraItem]:
    cartographie = getattr(config, "cartographie", None)
    if cartographie is None:
        raise ValueError(
            "Aucune fiche de cartographie rattachée à la configuration active. "
            "Lancez d'abord: python manage.py ajouter_cartographie_commune"
        )

    center_lat = float(cartographie.centre_latitude)
    center_lng = float(cartographie.centre_longitude)

    # Chaque type a un rayon de base différent pour éviter les superpositions.
    type_to_base_radius = {
        "sante": 0.0030,
        "education": 0.0040,
        "voirie": 0.0050,
        "administration": 0.0060,
    }

    # Récupère des listes existantes (TextField) si elles sont renseignées.
    type_to_names: dict[str, list[str]] = {
        "sante": list(cartographie.infrastructures_sante_list),
        "education": list(cartographie.infrastructures_education_list),
        "voirie": list(cartographie.infrastructures_routes_list),
        "administration": list(cartographie.infrastructures_administration_list),
    }

    items: list[_InfraItem] = []
    for infra_type, names in type_to_names.items():
        base_radius = type_to_base_radius.get(infra_type, 0.0045)
        for idx, nom in enumerate(names):
            dlat, dlng = _spiral_offset(idx, base_radius)
            lat = _quantize_6dp(_to_decimal(center_lat + dlat))
            lng = _quantize_6dp(_to_decimal(center_lng + dlng))
            items.append(
                _InfraItem(
                    type_infrastructure=infra_type,
                    nom=nom,
                    latitude=lat,
                    longitude=lng,
                    description="Importé depuis la fiche de cartographie (à compléter).",
                    adresse=config.adresse or "",
                    est_active=True,
                )
            )

    # Si la cartographie est vide, créer un minimum d’entrées “squelette”.
    if not items:
        base_items = [
            ("sante", "Infrastructure de santé (à renseigner)"),
            ("education", "Infrastructure éducative (à renseigner)"),
            ("voirie", "Point voirie (rond-point / carrefour / gare) (à renseigner)"),
            ("administration", "Administration / service public (à renseigner)"),
        ]
        for idx, (infra_type, nom) in enumerate(base_items):
            dlat, dlng = _spiral_offset(idx, type_to_base_radius.get(infra_type, 0.0045))
            lat = _quantize_6dp(_to_decimal(center_lat + dlat))
            lng = _quantize_6dp(_to_decimal(center_lng + dlng))
            items.append(
                _InfraItem(
                    type_infrastructure=infra_type,
                    nom=nom,
                    latitude=lat,
                    longitude=lng,
                    description="Entrée de base générée automatiquement (à compléter).",
                    adresse=config.adresse or "",
                    est_active=True,
                )
            )

    return items


def _from_json(path: Path) -> list[_InfraItem]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Le fichier JSON doit contenir une liste d'objets.")

    valid_types = _valid_types()
    items: list[_InfraItem] = []
    for idx, obj in enumerate(raw):
        if not isinstance(obj, dict):
            raise ValueError(f"Entrée #{idx} invalide: attendu un objet JSON.")

        infra_type = str(obj.get("type_infrastructure", "")).strip()
        if infra_type not in valid_types:
            raise ValueError(
                f"Entrée #{idx}: type_infrastructure invalide {infra_type!r}. "
                f"Valeurs autorisées: {sorted(valid_types)}"
            )

        nom = str(obj.get("nom", "")).strip()
        if not nom:
            raise ValueError(f"Entrée #{idx}: 'nom' est obligatoire.")

        lat = _quantize_6dp(_to_decimal(obj.get("latitude")))
        lng = _quantize_6dp(_to_decimal(obj.get("longitude")))

        description = str(obj.get("description", "") or "").strip()
        adresse = str(obj.get("adresse", "") or "").strip()
        est_active = bool(obj.get("est_active", True))

        items.append(
            _InfraItem(
                type_infrastructure=infra_type,
                nom=nom,
                latitude=lat,
                longitude=lng,
                description=description,
                adresse=adresse,
                est_active=est_active,
            )
        )

    return items


class Command(BaseCommand):
    help = (
        "Peuple la base avec des infrastructures géolocalisées (santé/éducation/voirie/administration) "
        "pour la commune active."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-json",
            dest="from_json",
            default="",
            help="Chemin vers un fichier JSON (liste d'infrastructures) à importer.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Mettre à jour les enregistrements existants (même nom + type + cartographie).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprimer toutes les infrastructures de la cartographie active avant import.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Ne rien écrire en base, affiche uniquement ce qui serait fait.",
        )

    def handle(self, *args, **options):
        config = ConfigurationMairie.objects.filter(est_active=True).first()
        if not config:
            self.stdout.write(
                self.style.ERROR(
                    "Aucune ConfigurationMairie active trouvée. "
                    "Créez d'abord une configuration dans l'admin."
                )
            )
            return

        try:
            cartographie = config.cartographie
        except Exception:
            cartographie = None

        if cartographie is None:
            self.stdout.write(
                self.style.ERROR(
                    "Aucune CartographieCommune rattachée à la configuration active. "
                    "Lancez: python manage.py ajouter_cartographie_commune"
                )
            )
            return

        force = bool(options.get("force"))
        clear = bool(options.get("clear"))
        dry_run = bool(options.get("dry_run"))
        from_json_opt = str(options.get("from_json") or "").strip()

        self.stdout.write(self.style.SUCCESS(f"Commune active : {config.nom_commune}"))
        self.stdout.write(self.style.SUCCESS(f"Cartographie : {cartographie}"))

        if clear:
            qs = InfrastructureCommune.objects.filter(cartographie=cartographie)
            count = qs.count()
            if dry_run:
                self.stdout.write(self.style.WARNING(f"[dry-run] Suppression de {count} infrastructures."))
            else:
                qs.delete()
                self.stdout.write(self.style.WARNING(f"{count} infrastructures supprimées."))

        if from_json_opt:
            path = Path(from_json_opt)
            if not path.exists():
                self.stdout.write(self.style.ERROR(f"Fichier introuvable: {path}"))
                return
            items = _from_json(path)
            source_label = f"JSON ({path})"
        else:
            items = _from_cartographie_text(config)
            source_label = "CartographieCommune (listes texte)"

        valid_types = _valid_types()
        for item in items:
            if item.type_infrastructure not in valid_types:
                self.stdout.write(
                    self.style.ERROR(
                        f"Type invalide détecté: {item.type_infrastructure!r}. "
                        f"Attendu: {sorted(valid_types)}"
                    )
                )
                return

        created = 0
        updated = 0
        skipped = 0

        for item in items:
            lookup = {
                "cartographie": cartographie,
                "type_infrastructure": item.type_infrastructure,
                "nom": item.nom,
            }
            defaults = {
                "latitude": item.latitude,
                "longitude": item.longitude,
                "description": item.description,
                "adresse": item.adresse,
                "est_active": item.est_active,
            }

            existing = InfrastructureCommune.objects.filter(**lookup).first()
            if existing:
                if not force:
                    skipped += 1
                    continue
                if dry_run:
                    updated += 1
                    continue
                for k, v in defaults.items():
                    setattr(existing, k, v)
                existing.save()
                updated += 1
                continue

            if dry_run:
                created += 1
                continue
            InfrastructureCommune.objects.create(**lookup, **defaults)
            created += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Source : {source_label}"))
        self.stdout.write(self.style.SUCCESS("Résumé des infrastructures :"))
        self.stdout.write(f"  - Créées : {created}")
        self.stdout.write(f"  - Mises à jour : {updated}")
        self.stdout.write(f"  - Ignorées (déjà existantes) : {skipped}")
        self.stdout.write(
            self.style.SUCCESS(
                "Terminé. Consultez l'admin (InfrastructureCommune) et la page /cartographie/."
            )
        )
