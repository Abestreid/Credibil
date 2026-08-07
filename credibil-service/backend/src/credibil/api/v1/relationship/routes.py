from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from credibil.core.database import get_session_dependency

router = APIRouter(prefix="/relationship", tags=["relationship"])


@router.get("/company/{idno}")
async def company_relationships(idno: str):
    """Get all persons and their connected companies for a company.

    For each person connected to the company, returns their roles and ALL
    companies they are connected to (not just the current one).
    """
    if len(idno) != 13 or not idno.isdigit():
        raise HTTPException(status_code=400, detail="IDNO must be exactly 13 digits")

    async for session in get_session_dependency():
        # Get company info
        result = await session.execute(
            text("SELECT id, idno, name_ro, status FROM companies WHERE idno = :idno"),
            {"idno": idno},
        )
        company_row = result.fetchone()
        if not company_row:
            raise HTTPException(status_code=404, detail="Company not found")

        company_id, company_idno, company_name, company_status = company_row

        # Get all persons directly connected to this company with their roles
        result = await session.execute(
            text("""
                SELECT DISTINCT
                    p.id as person_id,
                    p.full_name,
                    p.idnp,
                    array_agg(DISTINCT cr.relationship_type) as roles_in_current
                FROM company_relationships cr
                JOIN persons p ON cr.person_id = p.id
                WHERE cr.company_idno = :idno
                GROUP BY p.id, p.full_name, p.idnp
                ORDER BY p.full_name
            """),
            {"idno": idno},
        )
        person_rows = result.fetchall()

        if not person_rows:
            return {
                "success": True,
                "data": {
                    "company": {
                        "id": str(company_id),
                        "idno": company_idno,
                        "name_ro": company_name,
                        "status": company_status,
                    },
                    "persons": [],
                    "total_persons": 0,
                    "total_relationships": 0,
                },
            }

        person_ids = [row[0] for row in person_rows]

        # Batch query: get ALL relationships for these persons across ALL companies
        result = await session.execute(
            text("""
                SELECT
                    cr.person_id,
                    cr.company_idno,
                    cr.relationship_type,
                    cr.ownership_percentage,
                    cr.metadata->>'role' as director_role,
                    c.name_ro as company_name,
                    c.status as company_status,
                    c.id as company_uuid
                FROM company_relationships cr
                LEFT JOIN companies c ON c.idno = cr.company_idno
                WHERE cr.person_id = ANY(:person_ids)
                ORDER BY cr.person_id, cr.company_idno, cr.relationship_type
            """),
            {"person_ids": person_ids},
        )
        all_rel_rows = result.fetchall()

        # Group by person
        person_rels: dict = defaultdict(list)
        for row in all_rel_rows:
            person_rels[row[0]].append({
                "company_idno": row[1],
                "relationship_type": row[2],
                "ownership_percentage": row[3],
                "director_role": row[4],
                "company_name": row[5],
                "company_status": row[6],
                "company_uuid": str(row[7]) if row[7] else None,
            })

        persons = []
        for person_id, full_name, idnp, roles_in_current in person_rows:
            rels = person_rels.get(person_id, [])
            companies_map: dict[str, dict] = {}
            for rel in rels:
                cidno = rel["company_idno"]
                if cidno not in companies_map:
                    companies_map[cidno] = {
                        "company_idno": cidno,
                        "company_name": rel["company_name"],
                        "company_status": rel["company_status"],
                        "company_id": rel["company_uuid"],
                        "roles": [],
                        "ownership_percentage": rel["ownership_percentage"],
                        "director_role": rel["director_role"],
                        "is_current": cidno == idno,
                    }
                companies_map[cidno]["roles"].append(rel["relationship_type"])
                # Update ownership if this relationship has one
                if rel["ownership_percentage"] is not None:
                    companies_map[cidno]["ownership_percentage"] = rel["ownership_percentage"]
                # Update director role if this relationship has one
                if rel["director_role"]:
                    companies_map[cidno]["director_role"] = rel["director_role"]

            connected = sorted(
                companies_map.values(),
                key=lambda c: (not c["is_current"], c["company_name"] or ""),
            )
            active = sum(1 for c in connected if c["company_status"] == "active")
            liquidated = sum(1 for c in connected if c["company_status"] == "liquidated")

            persons.append({
                "person_id": str(person_id),
                "person_name": full_name,
                "person_idnp": idnp,
                "roles_in_current": sorted(roles_in_current),
                "connected_companies": connected,
                "total_companies": len(connected),
                "active_companies": active,
                "liquidated_companies": liquidated,
            })

        return {
            "success": True,
            "data": {
                "company": {
                    "id": str(company_id),
                    "idno": company_idno,
                    "name_ro": company_name,
                    "status": company_status,
                },
                "persons": persons,
                "total_persons": len(persons),
                "total_relationships": sum(p["total_companies"] for p in persons),
            },
        }


@router.get("/person/{person_id}")
async def person_detail(person_id: str):
    """Get person details with all connected companies."""
    try:
        pid = UUID(person_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid person ID") from err

    async for session in get_session_dependency():
        result = await session.execute(
            text("SELECT id, full_name, idnp, person_type, nationality FROM persons WHERE id = :id"),
            {"id": pid},
        )
        person_row = result.fetchone()
        if not person_row:
            raise HTTPException(status_code=404, detail="Person not found")

        person_id_db, full_name, idnp, person_type, nationality = person_row

        result = await session.execute(
            text("""
                SELECT
                    cr.company_idno,
                    cr.relationship_type,
                    cr.ownership_percentage,
                    cr.metadata->>'role' as director_role,
                    c.name_ro,
                    c.status,
                    c.id as company_uuid
                FROM company_relationships cr
                LEFT JOIN companies c ON c.idno = cr.company_idno
                WHERE cr.person_id = :person_id
                ORDER BY c.name_ro, cr.relationship_type
            """),
            {"person_id": person_id_db},
        )
        rel_rows = result.fetchall()

        companies_map: dict[str, dict] = {}
        for cidno, rel_type, ownership_pct, director_role, cname, cstatus, cuuid in rel_rows:
            if cidno not in companies_map:
                companies_map[cidno] = {
                    "company_idno": cidno,
                    "company_name": cname,
                    "company_status": cstatus,
                    "company_id": str(cuuid) if cuuid else None,
                    "roles": [],
                    "ownership_percentage": ownership_pct,
                    "director_role": director_role,
                }
            companies_map[cidno]["roles"].append(rel_type)
            if ownership_pct is not None:
                companies_map[cidno]["ownership_percentage"] = ownership_pct
            if director_role:
                companies_map[cidno]["director_role"] = director_role

        connected = sorted(companies_map.values(), key=lambda c: c["company_name"] or "")
        active = sum(1 for c in connected if c["company_status"] == "active")
        liquidated = sum(1 for c in connected if c["company_status"] == "liquidated")

        return {
            "success": True,
            "data": {
                "person": {
                    "id": str(person_id_db),
                    "full_name": full_name,
                    "idnp": idnp,
                    "person_type": person_type,
                    "nationality": nationality,
                },
                "connected_companies": connected,
                "total_companies": len(connected),
                "active_companies": active,
                "liquidated_companies": liquidated,
            },
        }
