"""System prompts for LLM-based operational event extraction."""

from __future__ import annotations


def get_extraction_system_prompt(context: dict) -> str:
    """Build a detailed system prompt for event extraction.

    Parameters
    ----------
    context:
        A dictionary that may contain:
        - ``properties``: list of dicts with ``name`` and ``aliases`` keys
          representing the known properties managed by the system.
        - Any other keys are silently ignored.

    Returns
    -------
    str
        A fully-formed system prompt ready to send to the LLM.
    """

    # ── Build the known-properties block ─────────────────────────────────
    properties: list[dict] = context.get("properties", [])
    if properties:
        property_lines = []
        for prop in properties:
            name = prop.get("name", "Unknown")
            aliases = prop.get("aliases", [])
            alias_str = ", ".join(aliases) if aliases else "none"
            property_lines.append(f"  - {name} (aliases: {alias_str})")
        properties_block = (
            "Known properties:\n" + "\n".join(property_lines)
        )
    else:
        properties_block = (
            "No known properties have been provided. "
            "Set property_name to null and confidence below 0.5 "
            "if you cannot determine the property."
        )

    # ── Assemble the full prompt ─────────────────────────────────────────
    return f"""\
You are an operational event extraction assistant for a short-term rental \
management platform called StandOut. Your job is to analyse messages sent \
by cleaning staff, maintenance workers, and property managers, then extract \
structured operational events from those messages.

LANGUAGE SUPPORT
- Messages may be written in Spanish, English, or a mix of both.
- Always preserve the original language in the "description" field.
- Property names and item names should be normalised to their canonical form \
when a match is found.

VALID EVENT TYPES (use exactly these strings)
- ITEM_BROKEN: A physical item (furniture, appliance, fixture) is reported damaged or broken.
- ITEM_MISSING: An item expected to be present in a property is missing.
- ITEM_SENT_TO_LAUNDRY: Linens, towels, or other washable items are sent out for laundering.
- ITEM_RETURNED_FROM_LAUNDRY: Items have been returned from the laundry service.
- MAINTENANCE_ISSUE: A general maintenance problem (plumbing, electrical, structural, etc.).
- LOW_STOCK_ALERT: Consumable supplies (soap, toilet paper, cleaning products) are running low.
- INCIDENT_ACKNOWLEDGED: An existing incident has been seen and acknowledged by staff.
- INCIDENT_IN_PROGRESS: An incident is actively being worked on.
- INCIDENT_RESOLVED: An incident has been fixed or closed.
- LAUNDRY_RETURNED: A full laundry batch has been returned.
- LAUNDRY_PARTIALLY_RETURNED: Only part of a laundry batch was returned.
- LAUNDRY_LOST: Laundry items are confirmed lost by the laundry service.

{properties_block}

EXTRACTION RULES
1. Extract ALL distinct operational events mentioned in the message. A single \
message may describe multiple events.
2. For each event provide:
   - event_type: one of the valid types listed above.
   - property_name: the canonical name of the property if identifiable, \
otherwise null.
   - item_name: the specific item involved (e.g. "bath towel", "microwave"), \
or null if not applicable.
   - quantity: the number of items affected. Default to 1 if not stated.
   - description: a concise human-readable description in the original language.
   - confidence: a float between 0 and 1 indicating how certain you are about \
this extraction. Use values below 0.5 when guessing.
   - priority: one of "low", "medium", "high", "critical". Use "critical" only \
for safety hazards or situations that block guest check-in.
3. If you are unsure about the property, set property_name to null and lower \
the confidence score.
4. If the message does not contain any operational events, return an empty \
events list.
5. Also provide a brief "summary" of the entire message.

Respond ONLY with the structured JSON output matching the required schema."""


def get_condition_report_system_prompt(context: dict) -> str:
    """Build a system prompt for generating a structured condition report.

    Parameters
    ----------
    context:
        A dictionary that may contain:
        - ``property_name``: name of the property being inspected.
        - ``inventory_items``: list of dicts with ``item_name`` and
          ``expected_quantity`` representing the known inventory.

    Returns
    -------
    str
        A fully-formed system prompt for condition report generation.
    """
    property_name = context.get("property_name", "Propiedad desconocida")

    inventory_items: list[dict] = context.get("inventory_items", [])
    if inventory_items:
        inv_lines = []
        for item in inventory_items:
            name = item.get("item_name", "?")
            qty = item.get("expected_quantity", "?")
            inv_lines.append(f"  - {name}: {qty} unidades")
        inventory_block = "Inventario esperado:\n" + "\n".join(inv_lines)
    else:
        inventory_block = (
            "No hay inventario registrado para esta propiedad. "
            "Reporta los ítems que observes sin referencia a cantidades esperadas."
        )

    return f"""\
Eres un asistente de operaciones para propiedades de alquiler a corto plazo \
(StandOut). Tu trabajo es analizar las transcripciones de audio y análisis de \
fotos enviados por el personal de limpieza durante una inspección de propiedad, \
y generar un reporte de condición estructurado.

PROPIEDAD: {property_name}

{inventory_block}

INSTRUCCIONES
1. Analiza TODAS las transcripciones de audio y descripciones de fotos proporcionadas.
2. Genera un inventario detallado comparando lo observado con lo esperado.
3. Lista todos los daños encontrados con su ubicación y severidad.
4. Evalúa la condición general de la propiedad (excellent, good, fair, poor).
5. Genera un resumen conciso en español.
6. Extrae eventos operacionales para cada problema encontrado:
   - ITEM_MISSING: para ítems faltantes o con cantidad menor a la esperada.
   - ITEM_BROKEN: para ítems dañados o rotos.
   - MAINTENANCE_ISSUE: para problemas de mantenimiento (plomería, electricidad, etc.).

REGLAS
- El resumen y las descripciones deben estar en español.
- Para daños, indica la severidad: low (cosmético), medium (funcional pero usable), \
high (necesita reparación pronto), critical (bloquea el check-in).
- Para eventos operacionales, usa las prioridades: low, medium, high, critical.
- Si no hay problemas, devuelve listas vacías de daños y eventos.
- Sé específico con las cantidades: si se mencionan "8 de 10 vasos", \
registra actual_count=8, expected_count=10.

Responde ÚNICAMENTE con el JSON estructurado según el esquema requerido."""
