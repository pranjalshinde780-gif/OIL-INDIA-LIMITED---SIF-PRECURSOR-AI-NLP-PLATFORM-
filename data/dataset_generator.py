import random
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# Seed for reproducibility
random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
LEXICON_PATH = os.path.join(DATA_DIR, "oil_lexicon.json")

with open(LEXICON_PATH, "r", encoding="utf-8") as f:
    LEXICON = json.load(f)

OIL_SITES = LEXICON["oil_sites"]

# Detailed incident archetypes for high-fidelity OIL field reports
SIF_PRECURSOR_TEMPLATES = [
    # Working at Height
    {
        "category": "Working at Height",
        "energy_type": "Gravitational",
        "texts": [
            "Floorman observed climbing the derrick ladder at {height}m elevation without engaging fall arrest slider or safety harness lanyard.",
            "Monkey board operator working at {height}m on rig mast with harness unlatched while latching drill pipe stands into fingers.",
            "Contract worker dismantling scaffolding at {height}m over mud tanks without 100% tie-off; scaffold boards were loose and unpinned.",
            "Near miss: dropped 14-inch heavy crescent wrench ({weight} kg) from derrick monkey board ({height}m), landed 1.5m away from roustabout on drill floor. No tether line attached.",
            "Workover crew working on elevated work platform at {height}m with missing mid-rail and unsecured kickboard above high pressure manifold."
        ],
        "barrier_status": "Missing / Bypassed",
        "severity": 4,
        "precursor_mechanism": "Unanchored personnel in high fall zone / Dropped object from height"
    },
    # Energy Isolation (LOTO)
    {
        "category": "Energy Isolation",
        "energy_type": "High Pressure / Electrical",
        "texts": [
            "Maintenance fitter cracked flange bolts on crude discharge manifold under {pressure} psi residual pressure without verifying LOTO or bleed down.",
            "Electrician started troubleshooting 415V motor control center for main mud pump #2 without applying padlock or verifying zero energy state with multimeter.",
            "Near miss: technician opened valve on high pressure injection line ({pressure} bar); line was not depressurized and expelled oil jet across gangway.",
            "Contractor broke line joint on separator gas outlet without blind flange installation or double block and bleed confirmation.",
            "Crew began pump seal replacement while upstream pneumatic ESDV was in manual bypass without physical mechanical lock."
        ],
        "barrier_status": "Failed / Missing",
        "severity": 5,
        "precursor_mechanism": "Work on energized/pressurized hydrocarbon circuit without positive isolation"
    },
    # Toxic Gas & Hazardous Atmosphere
    {
        "category": "Toxic Gas & Hazardous Atmosphere",
        "energy_type": "Toxic / Chemical",
        "texts": [
            "Operator entered cellar pit at wellhead #4 where H2S gas detector alarm was beeping at 25 ppm without wearing SCBA escape set.",
            "Sour gas release detected at separator sample point; area gas detector beacon was unserviceable and personal monitor battery was dead.",
            "Roustabout instructed to inspect flare pit perimeter downwind; portable multi-gas detector was left behind in doghouse.",
            "Near miss: sudden condensate vapor cloud engulfed pig receiver trap during opening; LEL level was 85% with nearby running diesel compressor.",
            "Crude oil transfer line pinhole leak spraying sour hydrocarbons near control room air intake; emergency ventilation trip did not engage."
        ],
        "barrier_status": "Missing / Compromised",
        "severity": 5,
        "precursor_mechanism": "Exposure to lethal H2S/flammable vapor without atmospheric barrier or respiratory protection"
    },
    # Safe Mechanical Lifting
    {
        "category": "Safe Mechanical Lifting",
        "energy_type": "Gravitational / Kinetic",
        "texts": [
            "Mobile crane lifting {weight} ton BOP stack; crane wire rope showed crushed strands and kink, and rigger stood directly beneath suspended load.",
            "Near miss: synthetic web sling sheared on sharp edge while hoisting 3.5-ton casing pipe; load swung violently into drill floor rotary barrier.",
            "Crane operator blind-hoisting heavy mud motor into catwalk without banksman/signalman; load caught on handrail and tilted dangerously.",
            "Overhead crane in workshop lifting {weight} ton engine block using uncertified homemade shackle without safety pin cotter.",
            "Drill crew lifted heavy drill collar bundle without guide tag lines during high crosswinds exceeding safe operational threshold of 28 knots."
        ],
        "barrier_status": "Failed / Compromised",
        "severity": 4,
        "precursor_mechanism": "Rigging failure / Personnel positioned in drop zone of heavy suspended mass"
    },
    # Confined Space
    {
        "category": "Confined Space",
        "energy_type": "Asphyxiation / Toxic",
        "texts": [
            "Two cleaners entered crude storage tank sump #3 for sludge removal without continuous forced mechanical ventilation or standby watchman at manhole.",
            "Contract worker stepped inside mud suction tank to clear suction strainer without confined space entry permit (CSEP) or pre-entry gas test.",
            "Confined space entry into vessel V-101 underway with expired gas test certificate; exhaust hose from nearby welding generator blowing into tank opening.",
            "Near miss: cleaner collapsed momentarily inside dirty oil sump due to oxygen depletion (16.2% O2); rescue harness and tripod winch were not rigged."
        ],
        "barrier_status": "Missing / Bypassed",
        "severity": 5,
        "precursor_mechanism": "Unauthorized entry into oxygen-deficient or toxic enclosure without life support"
    },
    # Hot Work
    {
        "category": "Hot Work",
        "energy_type": "Thermal / Explosion",
        "texts": [
            "Welder striking arc on pipe support bracket within 3 meters of crude oil degassing separator without fire blanket or continuous LEL monitoring.",
            "Gas cutting torch operation ongoing on rig cellar deck while crude skimming pit directly underneath had oil film emitting hydrocarbon fumes.",
            "Hot work permit expired 2 hours prior; welding crew continued fabrication on live gas manifold header without re-testing atmosphere.",
            "Grinding sparks from structural repair flying directly toward open vent valve of condensate drain drum; fire watch was absent."
        ],
        "barrier_status": "Missing / Bypassed",
        "severity": 5,
        "precursor_mechanism": "Ignition source introduced in classified hazardous flammable zone"
    },
    # Line of Fire
    {
        "category": "Line of Fire",
        "energy_type": "Mechanical / Kinetic",
        "texts": [
            "Floorman placed hands directly on drill pipe body while iron roughneck was engaging spinning wrench in automatic cycle.",
            "High pressure mud discharge hose operating at {pressure} psi lacked secondary safety whip-check cable at vibrating connection.",
            "Technician stood in line of fire of high-pressure test plug during hydrostatic pressure test at {pressure} psi with no safety barrier.",
            "Worker standing in bight of wireline while winch drum was pulling stuck logging tool under 6,000 lbs tension.",
            "Mechanic attempting to adjust belt tension on operational mud pump motor with rotating guard removed."
        ],
        "barrier_status": "Compromised / Missing",
        "severity": 4,
        "precursor_mechanism": "Body part positioned in crushing/stored energy release trajectory"
    },
    # Bypassing Safety Controls
    {
        "category": "Bypassing Safety Controls",
        "energy_type": "Pressure / Explosion",
        "texts": [
            "High-high level ESD trip sensor on production separator bypassed using jumper wire on terminal block without management of change (MOC).",
            "Emergency Blowout Preventer (BOP) accumulator pressure safety interlock found wedged open with wooden wedge to silence intermittent alarm.",
            "Main gas compressor high discharge temperature trip overridden by technician to prevent frequent nuisance shutdowns.",
            "Fire and gas deluge system water main isolation valve left locked in CLOSED position following maintenance test."
        ],
        "barrier_status": "Bypassed / Overridden",
        "severity": 5,
        "precursor_mechanism": "Deliberate defeat of critical safety shutdown or well barrier system"
    }
]

NON_SIF_TEMPLATES = [
    {
        "category": "Housekeeping & Facilities",
        "energy_type": "Low / Minimal",
        "texts": [
            "Empty plastic drinking water bottles left on table in contractor rest shelter.",
            "Cardboard packaging boxes from spare parts delivery stacked unflattened behind store room.",
            "Minor water spillage from drinking water cooler observed on floor of administrative corridor.",
            "Safety poster at main security entrance gate faded due to monsoon weather exposure.",
            "Discarded cotton waste and oily rags found inside open metal drum instead of designated hazardous waste bin.",
            "Grass and weeds overgrown along security boundary fence behind electrical substation.",
            "Dusty safety goggles stored on open rack in tool crib instead of sealed pouch.",
            "Notice board glass cracked at muster point area; notice papers damp.",
            "Hand washing soap dispenser empty in rest room near canteen.",
            "Tea cup left on generator room acoustic enclosure shelf by visiting staff."
        ],
        "barrier_status": "Not Applicable",
        "severity": 1,
        "precursor_mechanism": "None - Low severity routine housekeeping"
    },
    {
        "category": "Minor Ergonomics & Slips",
        "energy_type": "Low Kinetic",
        "texts": [
            "Worker tripped over uneven gravel footpath near parking shed; minor knee scrape, applied first aid antiseptic.",
            "Office swivel chair height adjustment lever loose in production planning office.",
            "Mud on sole of work boots caused slight slip on walkway grating at ground level; no injury, cleaned boots.",
            "Computer monitor placed too low on desk causing neck strain reported by documentation clerk.",
            "Slight oil smear on handrail of office staircase; wiped clean immediately with rag."
        ],
        "barrier_status": "Intact / Minor",
        "severity": 1,
        "precursor_mechanism": "None - Minor first aid level concern"
    },
    {
        "category": "Administrative & Minor PPE",
        "energy_type": "Low / None",
        "texts": [
            "Visitor observed walking across vehicle parking zone without high-visibility reflective vest; escorted to security for vest issuance.",
            "Contractor gate pass expired yesterday; worker stopped at security barrier pending renewal approval.",
            "Fire extinguisher monthly inspection tag due for update; physical gauge needle was in green zone.",
            "Noise level warning sign faded near air conditioning chiller unit.",
            "Spare hardhat stored in vehicle boot had scratched outer shell; replaced with new stock.",
            "Visitor logbook pen not functioning at main terminal gate.",
            "Daily safety briefing sign-in sheet signed with blue ink instead of standard black ink.",
            "Flashlight battery weak in emergency kit; replaced with fresh AAA cells."
        ],
        "barrier_status": "Intact",
        "severity": 1,
        "precursor_mechanism": "None - Administrative non-conformance"
    },
    {
        "category": "Minor Equipment Wear",
        "energy_type": "Low",
        "texts": [
            "Small surface rust spotted on structural support beam of bicycle parking shed.",
            "Paint peeling on external casing of domestic water storage tank.",
            "Rubber gasket on portable water hose connection slightly worn, minor water droplet drip.",
            "Air conditioner air filter dusty in drillers cabin; scheduled for routine cleaning.",
            "Pedestrian crosswalk paint faded on asphalt road inside facility compound."
        ],
        "barrier_status": "Intact",
        "severity": 1,
        "precursor_mechanism": "None - Cosmetic or non-critical asset wear"
    }
]

REPORT_TYPES = ["Unsafe Act", "Unsafe Condition", "Near Miss"]

def generate_report_text(template, site):
    raw_text = random.choice(template["texts"])
    height = random.choice([6, 12, 18, 22, 28, 35])
    pressure = random.choice([350, 600, 1200, 2500, 3200, 5000])
    weight = random.choice([1.5, 2.8, 4.0, 6.5, 12.0])
    
    filled = raw_text.format(height=height, pressure=pressure, weight=weight)
    
    # 25% chance to append field-specific prefix or reporter observation
    prefixes = [
        f"During morning rounds at {site['name']}, ",
        f"Observation reported by Shift In-Charge at {site['id']}: ",
        f"Safety audit finding: ",
        f"HSE patrol observation: ",
        f"Near-miss incident report from {site['type']}: ",
        ""
    ]
    return random.choice(prefixes) + filled

def generate_dataset(n_samples=1350):
    rows = []
    base_date = datetime(2026, 1, 1)
    
    # Target distribution: ~23% SIF Precursor, ~77% Non-SIF
    n_sif = int(n_samples * 0.235)
    n_non_sif = n_samples - n_sif
    
    report_id = 10001
    
    # Generate SIF Precursors
    for _ in range(n_sif):
        site = random.choice(OIL_SITES)
        template = random.choice(SIF_PRECURSOR_TEMPLATES)
        text = generate_report_text(template, site)
        
        # High-potential SIF characteristics
        report_type = random.choice(["Unsafe Act", "Unsafe Condition", "Near Miss"])
        date = base_date + timedelta(days=random.randint(0, 260), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        likelihood = random.choice([3, 4, 5])
        severity = template["severity"]
        risk_score = likelihood * severity # Risk matrix
        
        rows.append({
            "report_id": f"OIL-HSE-{report_id}",
            "date": date.strftime("%Y-%m-%d %H:%M"),
            "site_id": site["id"],
            "site_name": site["name"],
            "facility_type": site["type"],
            "basin": site["basin"],
            "latitude": site["lat"],
            "longitude": site["lng"],
            "report_type": report_type,
            "description": text,
            "is_sif_precursor": 1,
            "sif_category": "SIF Precursor",
            "iogp_rule": template["category"],
            "energy_hazard_type": template["energy_type"],
            "barrier_status": template["barrier_status"],
            "potential_severity": severity,
            "likelihood": likelihood,
            "risk_score": risk_score,
            "precursor_mechanism": template["precursor_mechanism"],
            "status": random.choice(["Investigating", "Escalated to OIM", "CAPA Required", "Action Pending"])
        })
        report_id += 1
        
    # Generate Non-SIF Reports
    for _ in range(n_non_sif):
        site = random.choice(OIL_SITES)
        template = random.choice(NON_SIF_TEMPLATES)
        text = generate_report_text(template, site)
        
        report_type = random.choice(["Unsafe Act", "Unsafe Condition", "Observation"])
        date = base_date + timedelta(days=random.randint(0, 260), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        likelihood = random.choice([1, 2])
        severity = template["severity"]
        risk_score = likelihood * severity
        
        rows.append({
            "report_id": f"OIL-HSE-{report_id}",
            "date": date.strftime("%Y-%m-%d %H:%M"),
            "site_id": site["id"],
            "site_name": site["name"],
            "facility_type": site["type"],
            "basin": site["basin"],
            "latitude": site["lat"],
            "longitude": site["lng"],
            "report_type": report_type,
            "description": text,
            "is_sif_precursor": 0,
            "sif_category": "Non-SIF Routine",
            "iogp_rule": "Non-Critical / General HSE",
            "energy_hazard_type": template["energy_type"],
            "barrier_status": template["barrier_status"],
            "potential_severity": severity,
            "likelihood": likelihood,
            "risk_score": risk_score,
            "precursor_mechanism": template["precursor_mechanism"],
            "status": random.choice(["Closed", "Resolved", "Logged", "Routine Fix"])
        })
        report_id += 1
        
    # Shuffle dataset
    random.shuffle(rows)
    df = pd.DataFrame(rows)
    
    out_file = os.path.join(DATA_DIR, "oil_safety_reports.csv")
    df.to_csv(out_file, index=False, encoding="utf-8")
    print(f"Generated {len(df)} authentic OIL safety reports.")
    print(f"SIF Precursors: {df['is_sif_precursor'].sum()} ({df['is_sif_precursor'].mean():.1%})")
    print(f"Non-SIF Reports: {(df['is_sif_precursor'] == 0).sum()} ({(df['is_sif_precursor'] == 0).mean():.1%})")
    print(f"Saved to: {out_file}")
    return df

if __name__ == "__main__":
    generate_dataset()
