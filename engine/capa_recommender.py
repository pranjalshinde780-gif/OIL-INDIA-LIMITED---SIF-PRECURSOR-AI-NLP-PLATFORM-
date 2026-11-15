class CAPARecommender:
    def __init__(self):
        # Structured Hierarchy of Controls recommendations mapped to IOGP Life-Saving Rules
        self.control_library = {
            "Working at Height": {
                "elimination": "Pre-assemble derrick modules and piping at ground level prior to crane lifting where possible.",
                "engineering": "Install permanent engineered anchor points, inertia reel fall arresters, and certified toe-boards/kickplates around elevated platforms.",
                "administrative": "Mandate 100% tie-off verification via dual-lanyard policy. Perform pre-shift scaffolding Green Tag inspection and enforce rig floor drop zones.",
                "ppe": "Inspect and don full-body safety harness with shock-absorbing lanyard, chin-strap helmet, and tethering cords for all hand tools."
            },
            "Energy Isolation": {
                "elimination": "Design piping manifolds with double block and bleed (DBB) isolation valves and positive mechanical spading points.",
                "engineering": "Fit keyed padlock lockout stations, captive key interlock systems, and calibrated bleed-off test points.",
                "administrative": "Enforce strict Energy Isolation Certificate (EIC). Require physical verification of zero energy state (depressurization gauge check & multimeter test) before unbolting.",
                "ppe": "Wear high-pressure blast protection face shields, leather gauntlets, and arc-flash Category 4 PPE when verifying live electrical enclosures."
            },
            "Toxic Gas & Hazardous Atmosphere": {
                "elimination": "Utilize vapor recovery units (VRU) and closed-loop sampling systems to eliminate atmospheric venting of sour hydrocarbons.",
                "engineering": "Install fixed catalytic and infrared H2S/hydrocarbon optical flame detectors tied to automated ESDV isolation and acoustic sirens.",
                "administrative": "Calibrate all portable multi-gas detectors daily (bump test). Enforce sour gas work permits and establish upwind muster points based on prevailing windsock direction.",
                "ppe": "Wear certified personal 4-gas monitor on chest lapel. Require positive-pressure 30-minute SCBA apparatus for entry into cellar pits and red-zone areas."
            },
            "Safe Mechanical Lifting": {
                "elimination": "Utilize automated hydraulic catwalks and pipe handling systems to minimize manual rig floor crane hoisting.",
                "engineering": "Ensure automatic safe load indicators (SLI), anti-two-block limit switches, and mechanical boom stops are functional.",
                "administrative": "Establish certified Lift Plan signed by Rig Superintendent. Enforce 360-degree barricaded exclusion drop zones and require banksman radio communication.",
                "ppe": "Equip all rig crew in drop-zone proximity with high-visibility rigger vests, impact-resistant metatarsal boots, and heavy cut-level-5 impact gloves."
            },
            "Confined Space": {
                "elimination": "Employ automated tank cleaning hydro-blasting heads and external cameras to avoid manned vessel entry.",
                "engineering": "Deploy explosion-proof positive pressure mechanical air blowers ensuring at least 20 air changes per hour.",
                "administrative": "Issue Confined Space Entry Permit (CSEP). Mandate continuous dedicated exterior standby watchman and complete 3-level atmospheric gas sniff log every 30 minutes.",
                "ppe": "Equip entrants with chest rescue harnesses connected to an overhead tripod retrieval winch, personal multi-gas sniffer, and emergency escape breathing set (EEBA)."
            },
            "Hot Work": {
                "elimination": "Substitute welding/cutting with cold cutting pipe beveling tools or bolted mechanical pipe connectors.",
                "engineering": "Erect pressurized certified welding habitat (flame-retardant enclosure) maintained under positive pressure with continuous gas intake shutoff.",
                "administrative": "Issue Hot Work Class A Permit. Perform LEL sniff test before striking arc and maintain continuous gas monitoring throughout operation.",
                "ppe": "Provide welders with Nomex flame-resistant coveralls (FRC), leather welding aprons, auto-darkening face shields, and place charged 50kg ABC foam trolley at site."
            },
            "Line of Fire": {
                "elimination": "Automate iron roughneck drill pipe tripping and eliminate manual spinning chain operations.",
                "engineering": "Install safety whip-check cables and rated safety hose clamps on all pressurized hoses exceeding 50 psi. Fit interlocked safety gates on rotary tables.",
                "administrative": "Mark red high-hazard 'No-Go Zones' on the rig floor. Conduct pre-job JSEA walk-through to map stored kinetic energy trajectories.",
                "ppe": "Wear heavy-duty anti-vibration impact gloves with dorsal metatarsal guards and impact-resistant safety spectacles."
            },
            "Bypassing Safety Controls": {
                "elimination": "Upgrade instrumentation to redundant 2-out-of-3 (2oo3) voting safety logic transmitters to eliminate nuisance false alarms.",
                "engineering": "Implement tamper-proof lockable selector switches and software role-based security passwords on safety instrumented system (SIS) trip overrides.",
                "administrative": "Enforce strict Management of Change (MOC) and formal written authorization from the Offshore Installation Manager (OIM) before any safety override.",
                "ppe": "Standard PPE applicable to operating zone; verify secondary independent alarm annunciator is manned during permitted override window."
            }
        }

    def recommend_actions(self, rule_name: str, is_sif: bool = True) -> dict:
        """
        Returns structured corrective and preventive actions (CAPA)
        aligned with the Hierarchy of Controls.
        """
        controls = self.control_library.get(rule_name)
        if not controls or not is_sif:
            return {
                "hierarchy": [
                    {"level": "Elimination / Substitution", "action": "Identify and remove the root source of the physical hazard or clutter."},
                    {"level": "Engineering Controls", "action": "Implement local guarding, repair surface defects, or fix leaking fittings."},
                    {"level": "Administrative Controls", "action": "Conduct immediate safety briefing / Toolbox Talk (TBT) and record in shift log."},
                    {"level": "Personal Protective Equipment", "action": "Verify all personnel wear mandatory baseline PPE (helmet, boots, safety glasses, high-vis)."}
                ],
                "priority": "Routine / Level-1",
                "target_closure_hours": 72
            }
            
        return {
            "hierarchy": [
                {"level": "1. Elimination / Substitution", "action": controls["elimination"], "tag": "Long-Term Prevention"},
                {"level": "2. Engineered Safeguards", "action": controls["engineering"], "tag": "Critical Barrier"},
                {"level": "3. Administrative & PTW Protocol", "action": controls["administrative"], "tag": "Immediate Procedural Hold"},
                {"level": "4. PPE & Life Support", "action": controls["ppe"], "tag": "Last-Line Defense"}
            ],
            "priority": "IMMEDIATE SIF INTERVENTION / STOP WORK AUTHORITY (SWA)",
            "target_closure_hours": 4
        }
