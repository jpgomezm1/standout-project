"""Seed script for StandOut demo data.

Usage:
    cd backend && python -m scripts.seed          # insert seed data
    cd backend && python -m scripts.seed --clean   # truncate all tables first
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.infrastructure.db.session import init_engine

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NOW = datetime.now(timezone.utc)
TODAY = date(2026, 2, 24)

PROPERTIES = [
    {"name": "Penthouse Poblado 1201", "city": "Medellín", "type": "penthouse", "max_guests": 8},
    {"name": "Suite Laureles 304", "city": "Medellín", "type": "suite", "max_guests": 4},
    {"name": "Loft Provenza 802", "city": "Medellín", "type": "loft", "max_guests": 3},
    {"name": "Apartamento Envigado 501", "city": "Medellín", "type": "apartment", "max_guests": 5},
    {"name": "Penthouse Manila 1501", "city": "Medellín", "type": "penthouse", "max_guests": 10},
    {"name": "Studio Laureles 210", "city": "Medellín", "type": "studio", "max_guests": 2},
    {"name": "Casa La Estrella Premium", "city": "Medellín", "type": "house", "max_guests": 12},
    {"name": "Suite Astorga 607", "city": "Medellín", "type": "suite", "max_guests": 4},
    {"name": "Penthouse Tesoro 2001", "city": "Medellín", "type": "penthouse", "max_guests": 8},
    {"name": "Apartamento Patio Bonito 403", "city": "Medellín", "type": "apartment", "max_guests": 6},
    {"name": "Casa Colonial Cartagena", "city": "Cartagena", "type": "house", "max_guests": 10},
    {"name": "Suite Bocagrande 1102", "city": "Cartagena", "type": "suite", "max_guests": 4},
    {"name": "Penthouse Castillogrande 901", "city": "Cartagena", "type": "penthouse", "max_guests": 8},
    {"name": "Apartamento Old City 305", "city": "Cartagena", "type": "apartment", "max_guests": 4},
    {"name": "Loft Manga 408", "city": "Cartagena", "type": "loft", "max_guests": 3},
    {"name": "Suite Usaquén 701", "city": "Bogotá", "type": "suite", "max_guests": 4},
    {"name": "Penthouse Chapinero 1801", "city": "Bogotá", "type": "penthouse", "max_guests": 6},
    {"name": "Apartamento Rosales 502", "city": "Bogotá", "type": "apartment", "max_guests": 4},
    {"name": "Suite Rodadero 603", "city": "Santa Marta", "type": "suite", "max_guests": 5},
    {"name": "Casa Bello Horizonte", "city": "Santa Marta", "type": "house", "max_guests": 8},
]

# housekeepers_needed by property type
HOUSEKEEPERS_NEEDED = {
    "penthouse": 2,
    "house": 2,
    "suite": 1,
    "apartment": 1,
    "studio": 1,
    "loft": 1,
}

# Inventory templates per property type
INVENTORY_TEMPLATES: dict[str, list[dict]] = {
    "penthouse": [
        # LINEN
        {"item_name": "Sábanas King", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Sábanas Queen", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Almohadas", "category": "LINEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Fundas Almohada", "category": "LINEN", "expected_quantity": 16, "low_stock_threshold": 4},
        {"item_name": "Cobija Premium", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Protector Colchón", "category": "LINEN", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Plumones", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        # TOWEL
        {"item_name": "Toallas Baño", "category": "TOWEL", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Toallas Mano", "category": "TOWEL", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Toallas Piso", "category": "TOWEL", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Batas de Baño", "category": "TOWEL", "expected_quantity": 4, "low_stock_threshold": 1},
        # KITCHEN
        {"item_name": "Vasos", "category": "KITCHEN", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Copas Vino", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Platos Grandes", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Platos Pequeños", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Tenedores", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Cuchillos", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Cucharas", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Ollas", "category": "KITCHEN", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Sartenes", "category": "KITCHEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Tazas Espresso", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        # BATHROOM
        {"item_name": "Set Amenities", "category": "BATHROOM", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Jabón Líquido", "category": "BATHROOM", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Shampoo", "category": "BATHROOM", "expected_quantity": 4, "low_stock_threshold": 1},
        # ELECTRONIC
        {"item_name": "Control TV", "category": "ELECTRONIC", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Control A/C", "category": "ELECTRONIC", "expected_quantity": 2, "low_stock_threshold": 1},
        # OTHER
        {"item_name": "Juego Llaves", "category": "OTHER", "expected_quantity": 3, "low_stock_threshold": 1},
    ],
    "suite": [
        {"item_name": "Sábanas Queen", "category": "LINEN", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Almohadas", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Fundas Almohada", "category": "LINEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Cobija Premium", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Protector Colchón", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Toallas Baño", "category": "TOWEL", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Toallas Mano", "category": "TOWEL", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Toallas Piso", "category": "TOWEL", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Vasos", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Platos Grandes", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Platos Pequeños", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Tenedores", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Cuchillos", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Cucharas", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Ollas", "category": "KITCHEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Sartenes", "category": "KITCHEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Set Amenities", "category": "BATHROOM", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Jabón Líquido", "category": "BATHROOM", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Control TV", "category": "ELECTRONIC", "expected_quantity": 1, "low_stock_threshold": 1},
        {"item_name": "Control A/C", "category": "ELECTRONIC", "expected_quantity": 1, "low_stock_threshold": 1},
        {"item_name": "Juego Llaves", "category": "OTHER", "expected_quantity": 2, "low_stock_threshold": 1},
    ],
    "apartment": [
        {"item_name": "Sábanas Queen", "category": "LINEN", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Almohadas", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Fundas Almohada", "category": "LINEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Cobija Premium", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Protector Colchón", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Toallas Baño", "category": "TOWEL", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Toallas Mano", "category": "TOWEL", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Toallas Piso", "category": "TOWEL", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Vasos", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Platos Grandes", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Platos Pequeños", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Tenedores", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Cuchillos", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Cucharas", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Ollas", "category": "KITCHEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Sartenes", "category": "KITCHEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Set Amenities", "category": "BATHROOM", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Jabón Líquido", "category": "BATHROOM", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Control TV", "category": "ELECTRONIC", "expected_quantity": 1, "low_stock_threshold": 1},
        {"item_name": "Control A/C", "category": "ELECTRONIC", "expected_quantity": 1, "low_stock_threshold": 1},
        {"item_name": "Juego Llaves", "category": "OTHER", "expected_quantity": 2, "low_stock_threshold": 1},
    ],
    "studio": [
        {"item_name": "Sábanas Queen", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Almohadas", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Fundas Almohada", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Cobija Premium", "category": "LINEN", "expected_quantity": 1, "low_stock_threshold": 1},
        {"item_name": "Toallas Baño", "category": "TOWEL", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Toallas Mano", "category": "TOWEL", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Toallas Piso", "category": "TOWEL", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Vasos", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Platos Grandes", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Tenedores", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Cucharas", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Set Amenities", "category": "BATHROOM", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Control TV", "category": "ELECTRONIC", "expected_quantity": 1, "low_stock_threshold": 1},
        {"item_name": "Juego Llaves", "category": "OTHER", "expected_quantity": 2, "low_stock_threshold": 1},
    ],
    "house": [
        {"item_name": "Sábanas King", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Sábanas Queen", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Almohadas", "category": "LINEN", "expected_quantity": 10, "low_stock_threshold": 3},
        {"item_name": "Fundas Almohada", "category": "LINEN", "expected_quantity": 20, "low_stock_threshold": 5},
        {"item_name": "Cobija Premium", "category": "LINEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Protector Colchón", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Plumones", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Toallas Baño", "category": "TOWEL", "expected_quantity": 16, "low_stock_threshold": 4},
        {"item_name": "Toallas Mano", "category": "TOWEL", "expected_quantity": 16, "low_stock_threshold": 4},
        {"item_name": "Toallas Piso", "category": "TOWEL", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Batas de Baño", "category": "TOWEL", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Vasos", "category": "KITCHEN", "expected_quantity": 16, "low_stock_threshold": 4},
        {"item_name": "Copas Vino", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Platos Grandes", "category": "KITCHEN", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Platos Pequeños", "category": "KITCHEN", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Tenedores", "category": "KITCHEN", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Cuchillos", "category": "KITCHEN", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Cucharas", "category": "KITCHEN", "expected_quantity": 12, "low_stock_threshold": 3},
        {"item_name": "Ollas", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Sartenes", "category": "KITCHEN", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Tazas Espresso", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Set Amenities", "category": "BATHROOM", "expected_quantity": 10, "low_stock_threshold": 3},
        {"item_name": "Jabón Líquido", "category": "BATHROOM", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Shampoo", "category": "BATHROOM", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Control TV", "category": "ELECTRONIC", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Control A/C", "category": "ELECTRONIC", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Juego Llaves", "category": "OTHER", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Sillas Comedor", "category": "FURNITURE", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Mesas Auxiliares", "category": "FURNITURE", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Lámparas", "category": "FURNITURE", "expected_quantity": 6, "low_stock_threshold": 2},
    ],
    "loft": [
        {"item_name": "Sábanas Queen", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Almohadas", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Fundas Almohada", "category": "LINEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Cobija Premium", "category": "LINEN", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Toallas Baño", "category": "TOWEL", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Toallas Mano", "category": "TOWEL", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Toallas Piso", "category": "TOWEL", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Vasos", "category": "KITCHEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Platos Grandes", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Platos Pequeños", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Tenedores", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Cuchillos", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Cucharas", "category": "KITCHEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Set Amenities", "category": "BATHROOM", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Control TV", "category": "ELECTRONIC", "expected_quantity": 1, "low_stock_threshold": 1},
        {"item_name": "Juego Llaves", "category": "OTHER", "expected_quantity": 2, "low_stock_threshold": 1},
    ],
}

GUEST_NAMES = [
    # Colombian names
    "Santiago Restrepo", "Valentina Gómez", "Sebastián Londoño", "Mariana Ospina",
    "Andrés Cardona", "Camila Herrera", "Felipe Aristizábal", "Isabella Mejía",
    "Juan David Ramírez", "Laura Sánchez", "Carlos Muñoz", "Daniela Pérez",
    "Alejandro Torres", "Sofía Giraldo", "Nicolás Vélez", "Carolina Duque",
    "Mateo Jaramillo", "Gabriela Ríos", "Miguel Ángel Botero", "Ana María Cano",
    # International names
    "James Wilson", "Emily Thompson", "Michael Brown", "Sarah Johnson",
    "Pierre Dubois", "Marie Laurent", "Hans Mueller", "Anna Schmidt",
    "Lucas Fernández", "María García", "Roberto Rossi", "Elena Bianchi",
    "João Silva", "Beatriz Santos", "David Kim", "Yuki Tanaka",
    "Alexander Petrov", "Olga Ivanova", "Ahmed Hassan", "Fatima Al-Said",
]

INCIDENTS = [
    {"title": "Fuga de agua en baño principal", "type": "plumbing", "priority": "high", "status": "open", "description": "Se reporta fuga constante debajo del lavamanos del baño principal. El huésped notó humedad en el piso."},
    {"title": "A/C no enfría correctamente", "type": "hvac", "priority": "high", "status": "in_progress", "description": "El aire acondicionado enciende pero no baja la temperatura. Técnico programado para mañana."},
    {"title": "Cerradura smart no responde", "type": "security", "priority": "critical", "status": "acknowledged", "description": "La cerradura electrónica no reconoce el código. Se proporcionó llave física de respaldo."},
    {"title": "Bombillo fundido en sala", "type": "electrical", "priority": "low", "status": "resolved", "description": "Bombillo LED de la lámpara principal de la sala no funciona. Reemplazado por mantenimiento."},
    {"title": "Wifi intermitente", "type": "connectivity", "priority": "medium", "status": "open", "description": "Los huéspedes reportan desconexiones frecuentes del wifi. Router reiniciado sin mejora."},
    {"title": "Puerta del balcón no cierra bien", "type": "maintenance", "priority": "medium", "status": "in_progress", "description": "La puerta corrediza del balcón no sella completamente. Entra aire."},
    {"title": "Mancha en alfombra de sala", "type": "cleaning", "priority": "low", "status": "acknowledged", "description": "Mancha de vino tinto en la alfombra principal. Se necesita limpieza profesional."},
    {"title": "Ruido excesivo de vecinos", "type": "noise", "priority": "medium", "status": "open", "description": "Quejas de ruido proveniente del apartamento de arriba. Contactar administración."},
    {"title": "Calentador de agua no funciona", "type": "plumbing", "priority": "high", "status": "in_progress", "description": "No hay agua caliente en ningún baño. Técnico en camino."},
    {"title": "Control remoto TV perdido", "type": "amenity", "priority": "low", "status": "resolved", "description": "Huésped anterior se llevó el control remoto. Reemplazado con control universal."},
    {"title": "Refrigerador hace ruido extraño", "type": "appliance", "priority": "medium", "status": "acknowledged", "description": "El refrigerador produce un zumbido constante. Funciona pero el ruido es molesto."},
    {"title": "Goteo en techo de cocina", "type": "plumbing", "priority": "critical", "status": "open", "description": "Se detectó goteo activo en el techo de la cocina, posible filtración del piso superior."},
]

INTERNAL_NOTES = [
    "Late check-in 11pm",
    "Necesita cuna para bebé",
    "VIP - cliente frecuente",
    "Requiere parking cubierto",
    "Alérgico a mascotas - limpieza profunda",
    "Celebra aniversario - dejar botella de vino",
    "Check-out tardío confirmado 2pm",
    "Grupo familiar con niños pequeños",
    "Solicita toallas extra",
    "Trabaja remoto - necesita buena conexión wifi",
]

# Amount ranges by property type (COP)
AMOUNT_RANGES: dict[str, tuple[int, int]] = {
    "penthouse": (800_000, 1_500_000),
    "suite": (400_000, 800_000),
    "apartment": (350_000, 700_000),
    "studio": (250_000, 450_000),
    "house": (900_000, 1_500_000),
    "loft": (300_000, 600_000),
}


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

async def _clean(session: AsyncSession) -> None:
    """TRUNCATE all tables with CASCADE."""
    tables = [
        "housekeeping_assignments",
        "property_staff_assignments", "staff_members",
        "reservations", "events", "incidents", "laundry_flows",
        "inventory_items", "pending_clarifications", "raw_messages",
        "idempotency_keys", "telegram_users", "properties",
    ]
    for table in tables:
        await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    await session.commit()
    print("  Cleaned all tables.")


async def _seed_properties(session: AsyncSession) -> list[dict]:
    """Insert 20 properties and return them with their generated IDs."""
    results = []
    for prop in PROPERTIES:
        prop_id = uuid4()
        hk_needed = HOUSEKEEPERS_NEEDED.get(prop["type"], 1)
        await session.execute(
            text("""
                INSERT INTO properties (id, name, address, timezone, aliases, metadata, is_active, housekeepers_needed)
                VALUES (:id, :name, :address, 'America/Bogota', :aliases, :metadata, true, :housekeepers_needed)
            """),
            {
                "id": str(prop_id),
                "name": prop["name"],
                "address": f'{prop["city"]}, Colombia',
                "aliases": "[]",
                "metadata": f'{{"property_type": "{prop["type"]}", "city": "{prop["city"]}", "max_guests": {prop["max_guests"]}}}',
                "housekeepers_needed": hk_needed,
            },
        )
        results.append({**prop, "id": prop_id})
    await session.commit()
    print(f"  Inserted {len(results)} properties.")
    return results


async def _seed_inventory(session: AsyncSession, properties: list[dict]) -> None:
    """Insert inventory items for each property based on its type."""
    count = 0
    for prop in properties:
        template = INVENTORY_TEMPLATES.get(prop["type"], INVENTORY_TEMPLATES["apartment"])
        for item in template:
            await session.execute(
                text("""
                    INSERT INTO inventory_items (id, property_id, item_name, category, expected_quantity, low_stock_threshold)
                    VALUES (:id, :property_id, :item_name, :category, :expected_quantity, :low_stock_threshold)
                """),
                {
                    "id": str(uuid4()),
                    "property_id": str(prop["id"]),
                    "item_name": item["item_name"],
                    "category": item["category"],
                    "expected_quantity": item["expected_quantity"],
                    "low_stock_threshold": item["low_stock_threshold"],
                },
            )
            count += 1
    await session.commit()
    print(f"  Inserted {count} inventory items.")


async def _seed_events(session: AsyncSession, properties: list[dict]) -> None:
    """Insert operational events for ~10 properties."""
    count = 0
    target_properties = properties[:10]

    for prop in target_properties:
        template = INVENTORY_TEMPLATES.get(prop["type"], INVENTORY_TEMPLATES["apartment"])
        # Find towel/linen items for laundry events
        linen_towel_items = [i for i in template if i["category"] in ("LINEN", "TOWEL")]

        # 2–3 laundry send events per property
        for item in random.sample(linen_towel_items, min(3, len(linen_towel_items))):
            qty = random.randint(1, max(1, item["expected_quantity"] // 2))
            created_at = NOW - timedelta(days=random.randint(1, 14), hours=random.randint(0, 12))

            await session.execute(
                text("""
                    INSERT INTO events (id, property_id, event_type, payload, idempotency_key, created_at)
                    VALUES (:id, :property_id, 'ITEM_SENT_TO_LAUNDRY', :payload, :idem_key, :created_at)
                """),
                {
                    "id": str(uuid4()),
                    "property_id": str(prop["id"]),
                    "payload": f'{{"item_name": "{item["item_name"]}", "quantity": {qty}}}',
                    "idem_key": f"seed-{uuid4()}",
                    "created_at": created_at,
                },
            )
            count += 1

            # 50% chance of return event
            if random.random() > 0.5:
                return_at = created_at + timedelta(days=random.randint(1, 3))
                await session.execute(
                    text("""
                        INSERT INTO events (id, property_id, event_type, payload, idempotency_key, created_at)
                        VALUES (:id, :property_id, 'ITEM_RETURNED_FROM_LAUNDRY', :payload, :idem_key, :created_at)
                    """),
                    {
                        "id": str(uuid4()),
                        "property_id": str(prop["id"]),
                        "payload": f'{{"item_name": "{item["item_name"]}", "quantity": {qty}}}',
                        "idem_key": f"seed-{uuid4()}",
                        "created_at": return_at,
                    },
                )
                count += 1

        # 1–2 broken/missing events per property
        kitchen_items = [i for i in template if i["category"] == "KITCHEN"]
        if kitchen_items:
            for item in random.sample(kitchen_items, min(2, len(kitchen_items))):
                event_type = random.choice(["ITEM_BROKEN", "ITEM_MISSING"])
                qty = random.randint(1, 2)
                created_at = NOW - timedelta(days=random.randint(1, 10))

                await session.execute(
                    text("""
                        INSERT INTO events (id, property_id, event_type, payload, idempotency_key, created_at)
                        VALUES (:id, :property_id, :event_type, :payload, :idem_key, :created_at)
                    """),
                    {
                        "id": str(uuid4()),
                        "property_id": str(prop["id"]),
                        "event_type": event_type,
                        "payload": f'{{"item_name": "{item["item_name"]}", "quantity": {qty}}}',
                        "idem_key": f"seed-{uuid4()}",
                        "created_at": created_at,
                    },
                )
                count += 1

    await session.commit()
    print(f"  Inserted {count} events.")


async def _seed_incidents(session: AsyncSession, properties: list[dict]) -> None:
    """Insert ~12 incidents distributed across properties."""
    count = 0
    for i, inc in enumerate(INCIDENTS):
        prop = properties[i % len(properties)]
        resolved_at = NOW - timedelta(days=random.randint(1, 3)) if inc["status"] == "resolved" else None

        await session.execute(
            text("""
                INSERT INTO incidents (id, property_id, incident_type, title, description, status, priority, resolved_at)
                VALUES (:id, :property_id, :incident_type, :title, :description, :status, :priority, :resolved_at)
            """),
            {
                "id": str(uuid4()),
                "property_id": str(prop["id"]),
                "incident_type": inc["type"],
                "title": inc["title"],
                "description": inc["description"],
                "status": inc["status"],
                "priority": inc["priority"],
                "resolved_at": resolved_at,
            },
        )
        count += 1

    await session.commit()
    print(f"  Inserted {count} incidents.")


async def _seed_laundry_flows(session: AsyncSession, properties: list[dict]) -> None:
    """Insert ~10 laundry flows across properties."""
    count = 0
    statuses = ["sent", "sent", "sent", "returned", "returned", "returned",
                "partially_returned", "partially_returned", "sent", "returned"]

    for i, status in enumerate(statuses):
        prop = properties[i % len(properties)]
        template = INVENTORY_TEMPLATES.get(prop["type"], INVENTORY_TEMPLATES["apartment"])
        towel_items = [it for it in template if it["category"] in ("TOWEL", "LINEN")]

        # Pick 1–3 items for the flow
        flow_items = []
        total = 0
        for item in random.sample(towel_items, min(random.randint(1, 3), len(towel_items))):
            qty = random.randint(2, max(2, item["expected_quantity"]))
            flow_items.append({"item_name": item["item_name"], "quantity": qty})
            total += qty

        sent_at = NOW - timedelta(days=random.randint(1, 10))
        expected_return = sent_at + timedelta(days=2)
        returned_at = sent_at + timedelta(days=random.randint(1, 3)) if status in ("returned", "partially_returned") else None

        import json
        await session.execute(
            text("""
                INSERT INTO laundry_flows (id, property_id, status, items, total_pieces, sent_at, expected_return_at, returned_at)
                VALUES (:id, :property_id, :status, :items, :total_pieces, :sent_at, :expected_return_at, :returned_at)
            """),
            {
                "id": str(uuid4()),
                "property_id": str(prop["id"]),
                "status": status,
                "items": json.dumps(flow_items),
                "total_pieces": total,
                "sent_at": sent_at,
                "expected_return_at": expected_return,
                "returned_at": returned_at,
            },
        )
        count += 1

    await session.commit()
    print(f"  Inserted {count} laundry flows.")


async def _seed_reservations(session: AsyncSession, properties: list[dict]) -> list[dict]:
    """Insert 5–10 reservations per property over Jan–Mar 2026. Returns all reservations."""
    count = 0
    channels = ["airbnb"] * 50 + ["booking"] * 30 + ["direct"] * 15 + ["other"] * 5
    all_reservations: list[dict] = []

    for prop in properties:
        # Generate reservations filling Jan 1 – Mar 31
        window_start = date(2026, 1, 1)
        window_end = date(2026, 3, 31)
        amount_min, amount_max = AMOUNT_RANGES.get(prop["type"], (300_000, 700_000))
        max_guests = prop["max_guests"]

        current = window_start
        prop_reservations = 0

        while current < window_end and prop_reservations < 10:
            # Stay duration: 2–7 nights
            stay = random.randint(2, 7)
            check_in = current
            check_out = check_in + timedelta(days=stay)

            if check_out > window_end:
                break

            # Determine status based on date
            if check_out < TODAY:
                status = "completed"
            elif check_in <= TODAY <= check_out:
                status = "in_progress"
            else:
                status = "confirmed"

            # ~8% chance of cancellation for future reservations
            if status == "confirmed" and random.random() < 0.08:
                status = "cancelled"

            channel = random.choice(channels)
            guest = random.choice(GUEST_NAMES)
            num_guests = random.randint(1, max_guests)

            # Per-night rate x nights
            nightly_rate = random.randint(amount_min, amount_max)
            amount = Decimal(str(nightly_rate * stay))

            # Optional internal notes (~25% chance)
            notes = random.choice(INTERNAL_NOTES) if random.random() < 0.25 else None

            res_id = uuid4()
            await session.execute(
                text("""
                    INSERT INTO reservations (id, property_id, guest_name, check_in, check_out, status, num_guests, channel, internal_notes, amount)
                    VALUES (:id, :property_id, :guest_name, :check_in, :check_out, :status, :num_guests, :channel, :internal_notes, :amount)
                """),
                {
                    "id": str(res_id),
                    "property_id": str(prop["id"]),
                    "guest_name": guest,
                    "check_in": check_in,
                    "check_out": check_out,
                    "status": status,
                    "num_guests": num_guests,
                    "channel": channel,
                    "internal_notes": notes,
                    "amount": amount,
                },
            )
            all_reservations.append({
                "id": res_id,
                "property_id": prop["id"],
                "property_type": prop["type"],
                "check_in": check_in,
                "check_out": check_out,
                "status": status,
            })
            count += 1
            prop_reservations += 1

            # Gap for cleaning: 1–3 days
            gap = random.randint(1, 3)
            current = check_out + timedelta(days=gap)

    await session.commit()
    print(f"  Inserted {count} reservations.")
    return all_reservations


STAFF_MEMBERS = [
    # Property Managers (assigned to specific properties)
    {
        "first_name": "Carolina", "last_name": "Restrepo",
        "email": "carolina.restrepo@standout.co", "phone": "+57 310 555 0001",
        "role": "property_manager",
        "property_indices": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # Props 1–10 (Medellín)
    },
    {
        "first_name": "Andrés", "last_name": "Mejía",
        "email": "andres.mejia@standout.co", "phone": "+57 310 555 0002",
        "role": "property_manager",
        "property_indices": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],  # Props 11–20
    },
    # Housekeepers (pool — NO property assignments)
    {
        "first_name": "María Fernanda", "last_name": "López",
        "email": "maria.lopez@standout.co", "phone": "+57 312 555 0001",
        "role": "housekeeper",
    },
    {
        "first_name": "Luz Dary", "last_name": "Gómez",
        "email": "luz.gomez@standout.co", "phone": "+57 312 555 0002",
        "role": "housekeeper",
    },
    {
        "first_name": "Sandra Milena", "last_name": "Ríos",
        "email": "sandra.rios@standout.co", "phone": "+57 312 555 0003",
        "role": "housekeeper",
    },
    {
        "first_name": "Gloria Patricia", "last_name": "Henao",
        "email": "gloria.henao@standout.co", "phone": "+57 312 555 0004",
        "role": "housekeeper",
    },
    {
        "first_name": "Carmen Elena", "last_name": "Zuluaga",
        "email": "carmen.zuluaga@standout.co", "phone": "+57 312 555 0005",
        "role": "housekeeper",
    },
    {
        "first_name": "Doris Amparo", "last_name": "Cardona",
        "email": "doris.cardona@standout.co", "phone": "+57 312 555 0006",
        "role": "housekeeper",
    },
    {
        "first_name": "Nubia Stella", "last_name": "Arango",
        "email": "nubia.arango@standout.co", "phone": "+57 312 555 0007",
        "role": "housekeeper",
    },
    {
        "first_name": "Fanny Rocío", "last_name": "Bedoya",
        "email": "fanny.bedoya@standout.co", "phone": "+57 312 555 0008",
        "role": "housekeeper",
    },
]


async def _seed_staff(session: AsyncSession, properties: list[dict]) -> list[dict]:
    """Insert 10 staff members (2 PMs with property assignments + 8 housekeepers pool).

    Returns list of housekeeper dicts with their IDs.
    """
    staff_count = 0
    assignment_count = 0
    housekeepers: list[dict] = []

    for member in STAFF_MEMBERS:
        staff_id = uuid4()
        await session.execute(
            text("""
                INSERT INTO staff_members (id, first_name, last_name, email, phone, role)
                VALUES (:id, :first_name, :last_name, :email, :phone, :role)
            """),
            {
                "id": str(staff_id),
                "first_name": member["first_name"],
                "last_name": member["last_name"],
                "email": member["email"],
                "phone": member["phone"],
                "role": member["role"],
            },
        )
        staff_count += 1

        # Only PMs get property assignments
        if member["role"] == "property_manager":
            for idx in member["property_indices"]:
                prop = properties[idx]
                await session.execute(
                    text("""
                        INSERT INTO property_staff_assignments (property_id, staff_id)
                        VALUES (:property_id, :staff_id)
                    """),
                    {
                        "property_id": str(prop["id"]),
                        "staff_id": str(staff_id),
                    },
                )
                assignment_count += 1
        else:
            housekeepers.append({**member, "id": staff_id})

    await session.commit()
    print(f"  Inserted {staff_count} staff members with {assignment_count} PM assignments. Housekeepers are a pool (no property assignments).")
    return housekeepers


async def _seed_housekeeping_assignments(
    session: AsyncSession,
    reservations: list[dict],
    housekeepers: list[dict],
) -> None:
    """Create housekeeping assignments for in_progress and confirmed reservations."""
    count = 0
    # Include in_progress + upcoming confirmed + some completed
    target = [r for r in reservations if r["status"] in ("in_progress", "confirmed", "completed")]
    # Take up to 60 reservations for variety
    target = target[:60]

    note_options = [
        "Limpieza post-checkout",
        "Preparación pre-checkin",
        "Limpieza profunda programada",
        "Limpieza mid-stay",
        "Cambio de sábanas",
        "Sanitización completa",
    ]

    for res in target:
        needed = HOUSEKEEPERS_NEEDED.get(res["property_type"], 1)
        # Assign for check-out (post-checkout cleaning)
        assigned = random.sample(housekeepers, min(needed, len(housekeepers)))
        for hk in assigned:
            note = random.choice(["Limpieza post-checkout", "Limpieza profunda programada"])
            await session.execute(
                text("""
                    INSERT INTO housekeeping_assignments (id, reservation_id, staff_id, scheduled_date, notes, status)
                    VALUES (:id, :reservation_id, :staff_id, :scheduled_date, :notes, :status)
                """),
                {
                    "id": str(uuid4()),
                    "reservation_id": str(res["id"]),
                    "staff_id": str(hk["id"]),
                    "scheduled_date": res["check_out"],
                    "notes": note,
                    "status": "completed" if res["check_out"] < TODAY else "scheduled",
                },
            )
            count += 1

        # Also assign for check-in (pre-checkin prep) with different housekeepers if possible
        prep_assigned = random.sample(housekeepers, min(needed, len(housekeepers)))
        for hk in prep_assigned:
            note = random.choice(["Preparación pre-checkin", "Sanitización completa"])
            await session.execute(
                text("""
                    INSERT INTO housekeeping_assignments (id, reservation_id, staff_id, scheduled_date, notes, status)
                    VALUES (:id, :reservation_id, :staff_id, :scheduled_date, :notes, :status)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid4()),
                    "reservation_id": str(res["id"]),
                    "staff_id": str(hk["id"]),
                    "scheduled_date": res["check_in"],
                    "notes": note,
                    "status": "completed" if res["check_in"] < TODAY else "scheduled",
                },
            )
            count += 1

        # 20% chance of a mid-stay cleaning
        if random.random() < 0.2 and (res["check_out"] - res["check_in"]).days > 3:
            mid_date = res["check_in"] + timedelta(days=random.randint(2, (res["check_out"] - res["check_in"]).days - 1))
            mid_hk = random.choice(housekeepers)
            await session.execute(
                text("""
                    INSERT INTO housekeeping_assignments (id, reservation_id, staff_id, scheduled_date, notes, status)
                    VALUES (:id, :reservation_id, :staff_id, :scheduled_date, :notes, :status)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid4()),
                    "reservation_id": str(res["id"]),
                    "staff_id": str(mid_hk["id"]),
                    "scheduled_date": mid_date,
                    "notes": random.choice(["Limpieza mid-stay", "Cambio de sábanas"]),
                    "status": "completed" if mid_date < TODAY else "scheduled",
                },
            )
            count += 1

    await session.commit()
    print(f"  Inserted {count} housekeeping assignments for {len(target)} reservations.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def _clean_all(session: AsyncSession) -> None:
    """TRUNCATE all tables including condition reports with CASCADE.

    Skips tables that don't exist yet (migration may not have run).
    """
    tables = [
        "condition_reports", "condition_report_sessions",
        "housekeeping_assignments",
        "property_staff_assignments", "staff_members",
        "reservations", "events", "incidents", "laundry_flows",
        "inventory_items", "pending_clarifications", "raw_messages",
        "idempotency_keys", "telegram_users", "properties",
    ]
    for table in tables:
        try:
            await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
        except Exception:
            await session.rollback()
    await session.commit()
    print("  Cleaned all tables.")


async def _seed_test_data(session: AsyncSession) -> None:
    """Seed minimal test data: 1 property + 1 reservation ending tomorrow + inventory."""
    import json

    tomorrow = TODAY + timedelta(days=1)

    # 1. Property
    prop_id = uuid4()
    await session.execute(
        text("""
            INSERT INTO properties (id, name, address, timezone, aliases, metadata, is_active, housekeepers_needed)
            VALUES (:id, :name, :address, 'America/Bogota', :aliases, :metadata, true, 1)
        """),
        {
            "id": str(prop_id),
            "name": "Penthouse Test 101",
            "address": "Medellín, Colombia",
            "aliases": json.dumps(["test 101", "penthouse test"]),
            "metadata": json.dumps({"property_type": "penthouse", "city": "Medellín", "max_guests": 6}),
            "housekeepers_needed": 1,
        },
    )
    print(f"  Inserted test property: Penthouse Test 101 (id={prop_id})")

    # 2. Staff member (housekeeper)
    staff_id = uuid4()
    await session.execute(
        text("""
            INSERT INTO staff_members (id, first_name, last_name, email, phone, role)
            VALUES (:id, :first_name, :last_name, :email, :phone, :role)
        """),
        {
            "id": str(staff_id),
            "first_name": "María",
            "last_name": "Test",
            "email": "maria.test@standout.co",
            "phone": "+57 312 000 0001",
            "role": "housekeeper",
        },
    )
    print(f"  Inserted test housekeeper: María Test (id={staff_id})")

    # 3. Telegram user linked to staff
    tg_user_id = uuid4()
    telegram_id = 123456789  # Default test telegram_id
    await session.execute(
        text("""
            INSERT INTO telegram_users (id, telegram_id, first_name, last_name, role)
            VALUES (:id, :telegram_id, :first_name, :last_name, 'operator')
        """),
        {
            "id": str(tg_user_id),
            "telegram_id": telegram_id,
            "first_name": "María",
            "last_name": "Test",
        },
    )
    print(f"  Inserted test telegram_user (telegram_id={telegram_id})")

    # 4. Reservation ending tomorrow
    res_id = uuid4()
    check_in = TODAY - timedelta(days=3)
    check_out = tomorrow
    await session.execute(
        text("""
            INSERT INTO reservations (id, property_id, guest_name, check_in, check_out, status, num_guests, channel, amount)
            VALUES (:id, :property_id, :guest_name, :check_in, :check_out, 'in_progress', :num_guests, 'airbnb', :amount)
        """),
        {
            "id": str(res_id),
            "property_id": str(prop_id),
            "guest_name": "Santiago Restrepo",
            "check_in": check_in,
            "check_out": check_out,
            "num_guests": 2,
            "amount": 3_200_000,
        },
    )
    print(f"  Inserted test reservation: check_out={check_out} (id={res_id})")

    # 5. Housekeeping assignment for tomorrow
    hk_id = uuid4()
    await session.execute(
        text("""
            INSERT INTO housekeeping_assignments (id, reservation_id, staff_id, scheduled_date, notes, status)
            VALUES (:id, :reservation_id, :staff_id, :scheduled_date, :notes, 'scheduled')
        """),
        {
            "id": str(hk_id),
            "reservation_id": str(res_id),
            "staff_id": str(staff_id),
            "scheduled_date": tomorrow,
            "notes": "Limpieza post-checkout + reporte de condición",
        },
    )
    print(f"  Inserted test housekeeping assignment for {tomorrow}")

    # 6. Basic inventory items
    test_inventory = [
        {"item_name": "Vasos", "category": "KITCHEN", "expected_quantity": 10, "low_stock_threshold": 3},
        {"item_name": "Toallas Baño", "category": "TOWEL", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Sábanas Queen", "category": "LINEN", "expected_quantity": 4, "low_stock_threshold": 1},
        {"item_name": "Almohadas", "category": "LINEN", "expected_quantity": 6, "low_stock_threshold": 2},
        {"item_name": "Platos Grandes", "category": "KITCHEN", "expected_quantity": 8, "low_stock_threshold": 2},
        {"item_name": "Control TV", "category": "ELECTRONIC", "expected_quantity": 2, "low_stock_threshold": 1},
        {"item_name": "Juego Llaves", "category": "OTHER", "expected_quantity": 3, "low_stock_threshold": 1},
        {"item_name": "Set Amenities", "category": "BATHROOM", "expected_quantity": 4, "low_stock_threshold": 1},
    ]
    for item in test_inventory:
        await session.execute(
            text("""
                INSERT INTO inventory_items (id, property_id, item_name, category, expected_quantity, low_stock_threshold)
                VALUES (:id, :property_id, :item_name, :category, :expected_quantity, :low_stock_threshold)
            """),
            {
                "id": str(uuid4()),
                "property_id": str(prop_id),
                "item_name": item["item_name"],
                "category": item["category"],
                "expected_quantity": item["expected_quantity"],
                "low_stock_threshold": item["low_stock_threshold"],
            },
        )
    print(f"  Inserted {len(test_inventory)} test inventory items.")

    await session.commit()


async def main(clean: bool = False, test: bool = False) -> None:
    settings = get_settings()
    _, session_factory = init_engine(settings.DATABASE_URL)

    async with session_factory() as session:
        if test:
            print("Seeding minimal test data...")
            await _clean_all(session)
            await _seed_test_data(session)
            print("\nDone! Test data inserted successfully.")
            return

        if clean:
            print("Cleaning existing data...")
            await _clean(session)

        print("Seeding data...")
        properties = await _seed_properties(session)
        await _seed_inventory(session, properties)
        await _seed_events(session, properties)
        await _seed_incidents(session, properties)
        await _seed_laundry_flows(session, properties)
        reservations = await _seed_reservations(session, properties)
        housekeepers = await _seed_staff(session, properties)
        await _seed_housekeeping_assignments(session, reservations, housekeepers)

    print("\nDone! Seed data inserted successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed StandOut demo data")
    parser.add_argument("--clean", action="store_true", help="Truncate all tables before seeding")
    parser.add_argument("--test", action="store_true", help="Minimal test data: 1 property + 1 reservation ending tomorrow")
    args = parser.parse_args()

    asyncio.run(main(clean=args.clean, test=args.test))
