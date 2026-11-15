class BowtieAnalyzer:
    def __init__(self):
        # Bowtie templates mapped to major hazards
        self.bowtie_templates = {
            "Working at Height": {
                "hazard": "Gravitational Potential Energy (Personnel working above 1.8m ground level)",
                "threat": "Loss of footing, slippery grating, unsecured positioning, or lack of 100% tie-off",
                "preventative_barriers": [
                    {"barrier": "Engineered Guardrails & Toe-boards", "type": "Physical / Engineered"},
                    {"barrier": "Scaffold Green Tag Inspection", "type": "Administrative / Audit"},
                    {"barrier": "Working at Height Permit & JHA", "type": "Administrative / PTW"}
                ],
                "top_event": "Fall of Person from Elevation or Dropped Object",
                "mitigative_barriers": [
                    {"barrier": "Full Body Harness with Shock Absorber / Inertia Reel", "type": "PPE / Arrest"},
                    {"barrier": "Secondary Tool Lanyard / Tethering", "type": "Physical Barrier"},
                    {"barrier": "Rig Floor Exclusion Zone & Hardhat", "type": "Administrative / PPE"}
                ],
                "consequence": "Fatal blunt impact trauma / Catastrophic derrick floor fatality"
            },
            "Energy Isolation": {
                "hazard": "Stored Energy (High Pressure Hydrocarbons / 415V-11kV Electrical / Residual Hydraulics)",
                "threat": "Flange unbolting or maintenance started without positive mechanical lockout or depressurization",
                "preventative_barriers": [
                    {"barrier": "Standard LOTO Application & Lock Box", "type": "Physical Lockout"},
                    {"barrier": "Zero Energy Verification (Bleed & Gauge / Multimeter Test)", "type": "Procedural Verification"},
                    {"barrier": "Isolation Certificate & Double Block and Bleed", "type": "Engineered Isolation"}
                ],
                "top_event": "Uncontrolled Release of Stored Energy / Hydrocarbon Jet / Arc Flash",
                "mitigative_barriers": [
                    {"barrier": "Blast Shield / Flange Deflector", "type": "Engineered Barrier"},
                    {"barrier": "Emergency Remote Shutdown (ESDV)", "type": "Automated Trip"},
                    {"barrier": "Arc-Rated PPE & Face Shield", "type": "PPE Protection"}
                ],
                "consequence": "Fatal high-pressure injection, catastrophic electrocution, or hydrocarbon flash fire"
            },
            "Toxic Gas & Hazardous Atmosphere": {
                "hazard": "Chemical Energy (Lethal Hydrogen Sulfide H2S / Toxic Volatiles)",
                "threat": "Flange leak, seal blowout, or stagnant gas pocket in cellar pit or tank",
                "preventative_barriers": [
                    {"barrier": "Fixed Gas Detection System & Area Alarms", "type": "Engineered Detection"},
                    {"barrier": "Pre-entry Multi-gas Atmospheric Sniff Test", "type": "Procedural Test"},
                    {"barrier": "Closed Drain & Degassing System", "type": "Engineered Containment"}
                ],
                "top_event": "Toxic Gas Plume Release / Hydrocarbon Vapor Dispersion",
                "mitigative_barriers": [
                    {"barrier": "Personal Multi-gas Monitor (H2S / LEL)", "type": "Detection Alert"},
                    {"barrier": "30-min SCBA / Emergency Escape Breathing Apparatus (EEBA)", "type": "Life Support PPE"},
                    {"barrier": "Muster Point Evacuation & Windsock Protocol", "type": "Emergency Response"}
                ],
                "consequence": "Instant lethal toxic asphyxiation ($H_2S$ toxicity) or vapor cloud explosion"
            },
            "Safe Mechanical Lifting": {
                "hazard": "Suspended Heavy Load (Drill Collars / BOP Stacks / Machinery up to 15 tons)",
                "threat": "Rigging failure, damaged synthetic sling, crane overload, or improper slings",
                "preventative_barriers": [
                    {"barrier": "Pre-use Rigging Gear Inspection (Color Code)", "type": "Visual Inspection"},
                    {"barrier": "Crane Safe Working Load (SWL) / Load Indicator", "type": "Engineered Limit"},
                    {"barrier": "Lifting Plan & Dedicated Certified Banksman", "type": "Procedural Control"}
                ],
                "top_event": "Loss of Load Integrity / Dropped Heavy Load / Crane Overturn",
                "mitigative_barriers": [
                    {"barrier": "Clear Exclusion Drop Zone Enforcement", "type": "Physical Barricade"},
                    {"barrier": "Tag Lines for Non-touch Load Guidance", "type": "Procedural Separation"},
                    {"barrier": "High-Impact Industrial Head & Foot Protection", "type": "PPE Barrier"}
                ],
                "consequence": "Catastrophic crushing fatality / Structural impact destruction"
            },
            "Confined Space": {
                "hazard": "Asphyxiating / Toxic / Flammable Enclosed Atmosphere (Vessel / Mud Tank / Sump)",
                "threat": "Unauthorized entry, inadequate purging, lack of forced ventilation, or inert gas",
                "preventative_barriers": [
                    {"barrier": "Confined Space Entry Permit & Risk Assessment", "type": "Administrative Authorization"},
                    {"barrier": "Positive Mechanical Isolation (Spading / Blinding)", "type": "Physical Barrier"},
                    {"barrier": "Pre-entry & Continuous Gas Testing (O2, LEL, H2S)", "type": "Atmospheric Verification"}
                ],
                "top_event": "Atmospheric Deterioration Inside Enclosed Space / Personnel Incapacitation",
                "mitigative_barriers": [
                    {"barrier": "Dedicated Standby Attendant at Manway Opening", "type": "Personnel Watch"},
                    {"barrier": "Rescue Tripod, Winch, & Retrieval Harness Rigged", "type": "Emergency Extraction"},
                    {"barrier": "Continuous Forced Mechanical Air Blower", "type": "Engineered Ventilation"}
                ],
                "consequence": "Hypoxic brain damage / Multiple entrant fatalities during unassisted rescue"
            },
            "Hot Work": {
                "hazard": "Thermal Ignition Energy (Open flame, welding arc, grinding sparks > 1000°C)",
                "threat": "Presence of flammable hydrocarbon gas, oil film, or unpurged pipework",
                "preventative_barriers": [
                    {"barrier": "Hot Work Permit & 15-meter Combustible Clearance", "type": "Administrative Boundary"},
                    {"barrier": "Calibrated Explosimeter LEL Sniff Testing", "type": "Atmospheric Verification"},
                    {"barrier": "Pressurized Welding Habitat / Fire Blankets", "type": "Engineered Containment"}
                ],
                "top_event": "Ignition of Hydrocarbon Atmosphere / Flash Fire / Tank Explosion",
                "mitigative_barriers": [
                    {"barrier": "Dedicated Fire Watch with Charged Foam Extinguisher", "type": "First-line Suppression"},
                    {"barrier": "Deluge System / Automated Fire Monitors", "type": "Engineered Extinguishing"},
                    {"barrier": "Flame-Retardant Nomex Workwear (FRC)", "type": "Thermal PPE"}
                ],
                "consequence": "Fatal burn trauma / Explosion-induced structural collapse"
            },
            "Line of Fire": {
                "hazard": "Kinetic Energy (Rotating shafts, pressurized hoses, iron roughneck, cathead)",
                "threat": "Worker positioning inside swing radius, lack of safety whip checks, or unguarded belts",
                "preventative_barriers": [
                    {"barrier": "Physical Machine Guards & Safety Interlocks", "type": "Physical Guard"},
                    {"barrier": "Pressure Hose Safety Whip-Checks & Clamps", "type": "Mechanical Restraint"},
                    {"barrier": "No-Go Red Zone Markings on Drill Floor", "type": "Visual Demarcation"}
                ],
                "top_event": "Body Part Struck By, Caught Between, or Whipped by Pressurized Line",
                "mitigative_barriers": [
                    {"barrier": "Emergency Stop Pull-Cords / Palm Buttons", "type": "Instant Shutdown"},
                    {"barrier": "Impact-resistant Metatarsal Boots & Heavy Gloves", "type": "PPE Shield"},
                    {"barrier": "Rapid First Aid & Trauma Stabilization", "type": "Medical Response"}
                ],
                "consequence": "Fatal crushing, traumatic amputation, or blunt force lethality"
            },
            "Bypassing Safety Controls": {
                "hazard": "Defeated Plant Safeguard (High pressure / Level / Blowout Protection)",
                "threat": "Interlocks jumpered, safety alarms disabled, or relief valves isolated",
                "preventative_barriers": [
                    {"barrier": "Formal Management of Change (MOC) Authorization", "type": "Procedural Gate"},
                    {"barrier": "Independent Safety Instrumented System (SIS)", "type": "Automated Safety Loop"},
                    {"barrier": "Shift Handover Critical Bypass Register", "type": "Administrative Verification"}
                ],
                "top_event": "Catastrophic Overpressure / Tank Overflow / Uncontrolled Blowout",
                "mitigative_barriers": [
                    {"barrier": "Secondary Mechanical Rupture Disc / PSV", "type": "Passive Relief"},
                    {"barrier": "High Integrity Pressure Protection System (HIPPS)", "type": "Engineered Shutdown"},
                    {"barrier": "Facility Emergency Blowdown & Evacuation Alarm", "type": "Emergency Procedure"}
                ],
                "consequence": "Catastrophic well blowout, asset loss, and multiple worker fatalities"
            }
        }

    def generate_bowtie(self, rule_name: str, text: str, is_sif: bool = True) -> dict:
        """
        Synthesizes a structured Bowtie risk model tailored to the incident's specific hazard profile.
        """
        # Match template or use general default
        template = self.bowtie_templates.get(rule_name)
        if not template:
            # Default to Working at Height or Line of Fire if rule not recognized
            template = self.bowtie_templates.get("Line of Fire")
            
        text_lower = text.lower()
        
        # Assess status of preventative barriers
        preventative_barriers = []
        for b in template["preventative_barriers"]:
            b_name = b["barrier"]
            # Check if mentioned as compromised in the text
            status = "Compromised / Failed" if any(w in text_lower for w in ["without", "missing", "bypassed", "damaged", "no", "unhooked", "unlatched", "overridden", "expired", "failed"]) else "Intact / Required"
            preventative_barriers.append({
                "name": b_name,
                "type": b["type"],
                "status": status,
                "is_failed": status == "Compromised / Failed"
            })
            
        # Mitigative barriers
        mitigative_barriers = []
        for b in template["mitigative_barriers"]:
            status = "Compromised / Absent" if any(w in text_lower for w in ["no", "without", "absent", "dead", "unserviceable", "not attached"]) else "Active Defense"
            mitigative_barriers.append({
                "name": b["barrier"],
                "type": b["type"],
                "status": status,
                "is_failed": status == "Compromised / Absent"
            })

        return {
            "hazard": template["hazard"],
            "threat": template["threat"],
            "preventative_barriers": preventative_barriers,
            "top_event": template["top_event"],
            "mitigative_barriers": mitigative_barriers,
            "consequence": template["consequence"],
            "is_sif": is_sif
        }
