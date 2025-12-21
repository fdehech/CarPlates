import re
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Path
from typing import Dict, Literal, Optional, Tuple
from scalar_fastapi import get_scalar_api_reference, Theme, Layout


SOURCE_URL = "https://www.automobile.tn/fr/guide/dernieres-immatriculations.html"

C1 = "mx-1 flex justify-around rounded-[7px] border-2 border-white py-3 text-[30px] text-white"
C2 = C1 + " flex-row-reverse"

PlateType = Literal["TUN", "RS", "IT", "TRAC", "MC", "REM", "AA", "ES"]

PLATE_META: Dict[PlateType, Dict[str, str]] = {
    "TUN": {"label": "Immatriculation Normale", "prefix": "TU"},
    "RS": {"label": "Régime Suspensif", "prefix": "RS"},
    "IT": {"label": "Immatriculation Temporaire", "prefix": "IT"},
    "TRAC": {"label": "Tracteur", "prefix": "TRAC"},
    "MC": {"label": "Motocyclette", "prefix": "MOTO"},
    "REM": {"label": "Véhicule Remorqué", "prefix": "REM"},
    "AA": {"label": "Appareil Agricole", "prefix": "AA"},
    "ES": {"label": "Engins Spéciaux", "prefix": "ES"},
}


class PlateItem(BaseModel):
    label: str
    prefix: str
    series: Optional[int] = Field(None, description="Series number (only for TUN)")
    number: int
    full: str


class PlatesResponse(BaseModel):
    updated_at: str
    source: str = "automobile.tn"
    data: Dict[PlateType, PlateItem]


class PlateResponse(BaseModel):
    type: PlateType
    plate: PlateItem
    updated_at: str
    source: str = "automobile.tn"


def extract_numbers(raw: str) -> Tuple[Optional[int], Optional[int]]:
    nums = [int(n) for n in re.findall(r"\d+", raw)]

    if len(nums) >= 2:
        return nums[0], nums[-1]
    if len(nums) == 1:
        return None, nums[0]
    return None, None


def format_plate(code: PlateType, raw: str) -> PlateItem:
    series, number = extract_numbers(raw)

    if number is None:
        raise ValueError("Invalid plate format")

    meta = PLATE_META[code]
    prefix = meta["prefix"]

    full = (
        f"{prefix} {series}/{number}"
        if code == "TUN" and series is not None
        else f"{prefix} {number}"
    )

    return PlateItem(
        label=meta["label"],
        prefix=prefix,
        series=series if code == "TUN" else None,
        number=number,
        full=full,
    )


async def fetch_latest_raw() -> Dict[PlateType, str]:
    headers = {"User-Agent": "Mozilla/5.0 (TunisiaPlatesAPI/1.0)"}

    try:
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            r = await client.get(SOURCE_URL)
            r.raise_for_status()
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Upstream source unavailable")

    soup = BeautifulSoup(r.text, "html.parser")
    container = soup.find("div", class_="cms-prose")

    if not container:
        raise HTTPException(status_code=500, detail="Parsing failed")

    tun_el = container.find("span", class_=C1)
    spans = container.find_all("span", class_=C2)

    if not tun_el or len(spans) < 7:
        raise HTTPException(status_code=500, detail="Unexpected page structure")

    return {
        "TUN": tun_el.get_text(strip=True),
        "RS": spans[0].get_text(strip=True),
        "IT": spans[1].get_text(strip=True),
        "TRAC": spans[2].get_text(strip=True),
        "MC": spans[3].get_text(strip=True),
        "REM": spans[4].get_text(strip=True),
        "AA": spans[5].get_text(strip=True),
        "ES": spans[6].get_text(strip=True),
    }


app = FastAPI(
    title="Tunisia Vehicle Plates API",
    description="Clean REST API providing latest Tunisian vehicle registration numbers",
    version="1.1.0",
    docs_url=None,
    redoc_url=None,
)


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="API Documentation",
        layout=Layout.CLASSIC,
        theme=Theme.DEEP_SPACE,
        hide_models=True,
        hide_client_button=False,
        show_sidebar=True,
        hide_search=False,
        hide_dark_mode_toggle=False,
        with_default_fonts=True,
        expand_all_model_sections=False,
        expand_all_responses=False,
        integration="fastapi"
    )


@app.get("/api/v1/plates", response_model=PlatesResponse, tags=["plates"])
async def get_all_plates():
    raw = await fetch_latest_raw()
    now = datetime.now(timezone.utc).isoformat()

    data = {
        code: format_plate(code, raw[code])
        for code in PLATE_META
    }

    return PlatesResponse(
        updated_at=now,
        data=data,
    )


@app.get(
    "/api/v1/plates/{plate_type}",
    response_model=PlateResponse,
    tags=["plates"],
)
async def get_plate(
    plate_type: str = Path(..., description="TUN, RS, IT, TRAC, MC, REM, AA, ES")
):
    plate_type = plate_type.upper()

    if plate_type not in PLATE_META:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plate type. Allowed: {', '.join(PLATE_META.keys())}",
        )

    raw = await fetch_latest_raw()
    now = datetime.now(timezone.utc).isoformat()

    return PlateResponse(
        type=plate_type,
        plate=format_plate(plate_type, raw[plate_type]),
        updated_at=now,
    )
