"""Map raw ClickUp task data (id, name, status, tags, date_updated(ms), fields[{id,v}]) to one dashboard employer record.
Usage: python3 sync/cu_map.py /tmp/raw.json data/e   (raw.json = JSON array of tasks)"""
import json, sys, os

F = dict(desc="181ddd62-a897-4a4c-8db2-cb2ce34f178a", assessment="e54c9791-dc1e-4d5a-a0a5-02ad288c62a9",
         skills="97b14ab9-21a4-4121-962b-c5fbf7709209", notes="bee75cd2-6ded-4b09-bef8-5840e4bd0031",
         other="13bcbd2d-0e9c-420e-99d1-e3c29db45bf4", link="602e1fde-4bb7-4e89-99c9-20d2ac8604c1",
         wage="d7e577af-72e2-43d4-9bea-cffbf5a8ad12", training="3e245841-39cd-4990-b35e-25cbbd0ef533",
         benefits="968adc95-717e-490b-846e-aa166fea10bc", education="a81edb0f-b501-4a69-be9a-8327310de298",
         education_old="80be7497-a81d-4834-9a72-60665d1542a0", coworking="2c088a08-63c6-4614-8d39-2f2a87dd50ee",
         felony="75640826-3f95-4dd7-ba47-fc4d15886789", tier="21dbe15a-4ac6-4675-8b50-9efd84bd5bde",
         drug="2b3c8f23-8c40-4981-a8a0-af1548e0203f", industry="f7b7e89c-b08d-4c98-a408-6f3bf324c98f")

OPT = {
 # education (a81edb0f, then older 80be7497)
 "a6f1e651-573d-49ec-9887-c4fa210cea04": "Experience in lieu of education", "0df4eaab-8bbc-4ee3-bcf2-a8acd7455d7a": "HS/GED Required",
 "f4243df8-f63c-4e4c-8647-87f3695b28f6": "Special Skills", "9d576abe-3be7-4bbc-aff0-8aa1223d4e8c": "Bachelors",
 "aade392f-f96f-480d-986a-c605b127d920": "Masters", "803cd487-076c-47a6-a4cd-fe1cd28a1fe4": "Education Req Not Listed",
 "72650b42-5f44-4d8d-8910-d17a9be6436d": "Requires License", "3badba28-caa0-4fc3-92b9-b6a7a2c65edf": "No Education Requirements",
 "f4d9c08e-0f3f-4a5b-8781-d294edbf30d1": "Associate Minimum",
 "cad803e5-bbfa-45d7-8489-57ff4dd430cb": "Experience in lieu of education", "90c5949e-92d9-400f-ab19-17eecf8268af": "HS/GED Required",
 "3303f068-1c2a-496b-bb7e-cb1abf453378": "Special Skills", "acf6b451-0ec8-4c4a-a1bd-0aa77b220788": "Higher Education",
 "c875a547-f5df-4e23-9995-d25aaab9346c": "Depending on Positon",
 # co-working
 "e7b5a781-33af-44ea-a564-c650d377ec35": "Yes, if HIPPA compliant", "69e8b256-13e4-4357-b327-dd3b5f2896ef": "No",
 "4ad880ec-ec20-4448-ab0d-88ddb2b1d6b9": "Depends On Client", "3aaff3b7-3a5f-4c9d-97fe-a8a164112ad9": "With Special Permission",
 # felony
 "4820526a-9863-4e13-ad87-d5443655c63a": "Yes (Case by Case)", "e8f42c09-405f-41bd-b12f-aeac3e5c8ab1": "Yes (5-7Yrs.)",
 "059f7dd1-10e4-4b13-af18-d653cfa86adf": "No ( no felony convictions ever)", "80807dd7-d869-402d-a8fb-fc6726a60fbb": "Yes, 7 Years+",
 # tier
 "73dab75e-780e-4e22-8f7b-0c3686b337ed": "TIER 1", "edfd9ad1-642f-4dba-83b1-97c0a43587dd": "TIER 2", "0b5bf384-8214-4295-8126-6e1d773907bf": "TIER 3",
 # drug test
 "993deaa0-dc8a-4c30-a383-67fc8c2d8146": "Required", "d95592bb-46d7-43d0-a4eb-225369fac0f9": "OMMA Friendly",
 "40e829f9-e0c8-4912-9a1c-c94b574aa83c": "Does not test THC", "687a33e4-2a6a-4457-9884-3e5e4ebc5dcb": "Certain Positions",
 "29ae00f6-29b4-4d6a-b7d6-f2c53862a613": "Not Required", "ba263229-84cf-4411-affe-825d70d070c5": "No",
 "3b2115ce-3cc0-4e42-a207-984647af861d": "Required (some are OMMA friendly)",
 "3590811f-6b55-49b2-ae16-694a433534b8": "Not mentioned (recruiter will discuss)",
 # industry
 "1485d773-d5bf-48f1-b242-15c84be55f3b": "Accounting", "3c06b565-6d78-41ba-b04c-9fb14b22eb66": "Admin/HR/Office/Clerical",
 "ddf26d1f-bb93-46e9-b22d-69f342f592b3": "Aerospace and Defense", "78c0d57b-d805-4e4e-9aaf-5b2db14668ef": "Arts | Graphics | Digital",
 "25289914-1b12-4e98-97f8-f60e080466b9": "Automotive | Admin & Data", "132dc1e3-1c0a-4d1e-b406-b0b44e86a11a": "Bilingual",
 "5be93543-0bd6-49a4-a50f-11582947fae0": "Construction/Manual Labor", "a7b32ac5-609d-47a5-aece-fcbceec80280": "Customer Service (Not call center)",
 "be85259b-4047-4ded-9f00-a7ccc3cdc6e0": "Customer Service via chat/no phones", "4effbc7d-f810-4c6b-9d89-bdd59632880d": "Customer Service/Business",
 "531dd16d-fc17-4e63-8219-cc0ebaac5896": "Data Entry", "6fa74e76-efac-4f2a-b713-a12e50a996b9": "Education",
 "91821616-039e-4c16-b241-e3a35fd749ec": "Film Industry", "638acda7-76bd-4ac4-8970-28da20347da6": "Financial | Banking",
 "3d1507dd-8314-4921-9ff7-89921a9b54e3": "Financial | Customer Assistance", "c8ec4e45-5a19-43f9-af69-7b0f07aa3f9b": "Financial | Debt Collection",
 "3440c8cf-7210-4f36-81be-817a6c36a2fc": "Financial | Real Estate", "9df6e423-3819-4028-a875-6533f1dd227e": "FinTech",
 "a4d1778f-9756-4c61-8742-9402d13203b9": "Food Service", "a4c21570-5308-44a3-8f4f-094bfc9c221b": "Gaming",
 "21db3392-4364-4a5f-be52-ccc0977f741b": "Health-Tech", "257b994f-7f7c-4eef-b844-e52400615ab5": "Healthcare | Behavioral Health",
 "fea5c5f9-eac6-4be7-9133-d8bac654f86e": "Healthcare | Billing-Coding-Admin", "20477fa9-3493-4eb0-a2f6-56d30df4424c": "Healthcare | CNA, CMA LPM, Med Assistant",
 "cff0a1d7-6990-4422-9997-bdc67e2b7352": "Healthcare | Dental/Vision Benefits", "d86d9f12-89f1-42e9-b486-3b380b3cebe4": "Healthcare | Equipment or Logistics",
 "e1df2a49-fc2e-4198-8351-fa0bb2ed6061": "Healthcare | HR & Administrative Support", "ad49e524-d7dd-4154-a934-ff7ac456e69d": "Healthcare | Patient Care",
 "4459d6ca-c408-4d90-aebc-25de7f915a6c": "Healthcare| Pharmacy Related", "96c28a46-e751-4022-adaf-c248c2e3e347": "Hospitality | Travel, Hotel, Entertainment",
 "36bd7953-1a4c-42bc-b432-09de82b9a004": "Human Resource | Contact Center", "50e63d73-24f3-4bf7-8c22-b3bffa1060b0": "Hybrid",
 "c2db621b-d8e0-4719-8446-557c61323f2f": "Inbound Sales", "6d03be3d-9ae1-49eb-90ff-6e23fbb135de": "Insurance (no sales) | Life & Health",
 "07acba77-e148-409d-8009-9710223a4b88": "Insurance (Property & Casualty)", "e8ca0ea4-f56d-409c-9b31-46f6b2cd4959": "Insurance | Life & Health Licensed",
 "00cc6db7-bd76-4bf4-ba9a-579421af86a8": "Insurance | P&C License Required", "a1b32636-82b6-4de7-abca-bb9d95d736b8": "Insurance | P&C license rquired",
 "c0f19d9c-2712-4d9e-b645-25b4e2c77bc0": "Insurance | PL or P&C", "03bde7bf-f75f-40dd-8d17-c755f7a3b2cd": "Insurance | Unlicensed",
 "833f2539-9a26-4e43-9509-a59a19d90006": "Legal", "b93ba7b5-797e-4ebc-b430-fc4bc912b31f": "Legal | Proces Server",
 "7ef43c95-5e1b-4224-8f11-39a240d40e0c": "Logistics", "f9fc06ec-d0d7-4e17-b3bf-e7e6b0e20d90": "Manufacturing",
 "72f4ea40-1064-46dc-95d6-ffec7ed43fa4": "Medical Billing", "a7f1ce08-b124-445f-985d-774ea89bf37e": "Mortgage Servicing | Legal/Customer Advocacy Support",
 "a285e7b4-e230-421a-8feb-3d92156d4095": "Mortgage/Financial/Banking", "6f29757e-36db-4ab8-be35-0f7567331485": "Multiple Roles",
 "c7f07464-836c-4103-86f1-00ab46849a04": "No experience required", "37ccbcef-4c92-4c44-abe5-b71043c298e3": "Non Sales Customer Service",
 "4a51f3b7-e0c6-423c-acd2-591ccccb9ded": "Nonprofit | Safety Education & Training", "1d518c11-d83f-4a9b-82ce-7d9ac53db873": "Patient Services",
 "06e1f691-3d3a-4c8e-b337-b6be16e9ae91": "Quality", "d49d0257-0d83-4584-b7d1-70d9c3a7ad1d": "Real estate",
 "2c06372d-c14e-4518-90a7-ee919e1ca3ae": "Remote", "7b465677-92a2-4443-b9b8-bac845ff5dd7": "Resource for employment",
 "b06f69d9-2199-4e0e-8ac5-92bdbc8d0b8e": "Retail", "788bc750-ca0e-4be1-b6ca-8d4e3dee2b72": "Security",
 "63c5dfc6-ae05-4b67-ba25-796901b0813b": "Social media", "82d5e72d-2605-492c-b7ef-a32b67ffe84c": "Sports",
 "32527261-3119-4d65-96fa-b317ac77a4fc": "Staffing Agency", "0e7d41a2-2452-4b5a-a210-7e46094c8c61": "Technical Support",
 "328fc386-b59b-4c7e-b2ba-1218ad9883a2": "Technologies", "e5609b1b-41bd-424b-925a-a7512f5847bd": "Technologies | AI",
 "9b63effc-c060-4956-b555-37e3d207926b": "Technology | IT & Tech", "29c87b18-9e6c-4ef4-82b9-a21fc9a3a5aa": "Telehealth",
 "ea21dace-ecb8-4e4f-913f-3ac79debb257": "Telehealth Admin", "278c3326-c0d8-4008-9f72-18f03fedead9": "Transcription",
 "b099efe6-f184-42f8-bba9-d1d9856cd13b": "Transportation", "5910e7fa-932d-40d7-b67b-77c86318add5": "Travel Industry",
 "7e04a09d-9b38-4c92-8fc0-da0ca2353244": "Veterinarian Services", "6c365df8-4c30-404c-9934-89cb42b58b87": "Virtual Assistant",
 "5d18876b-62b0-4eca-ad38-b569aa3def17": "Virtual Assistant/Variety", "0829a6a9-50f4-4389-ac1f-a2543ee048a2": "Virtual Residential Maintenance",
 "b4cf2fe2-a07a-4cc8-b5d2-0d45b985cc36": "Warehouse/Distribution",
}
UNKNOWN = set()

def opt(v):
    if v is None or v == "":
        return ""
    if v not in OPT:
        UNKNOWN.add(v)
        return ""
    return OPT[v]

def opts(v):
    out = []
    for x in (v or []):
        o = opt(x)
        if o and o.lower() != "remote":
            out.append(o)
    return out

def s(v):
    return "" if v is None else str(v).replace("\r", "").strip()

def updated_str(t):
    """YYYY-MM-DD (America/Chicago) from ClickUp date_updated in ms; falls back to t['updated'] or ''."""
    import datetime
    ms = t.get("date_updated")
    if ms:
        try:
            from zoneinfo import ZoneInfo
            d = datetime.datetime.fromtimestamp(int(ms) / 1000, ZoneInfo("America/Chicago"))
            return d.strftime("%Y-%m-%d")
        except Exception:
            pass
    return s(t.get("updated", ""))

def to_record(t):
    """t = {id, name, status, tags:[str], fields:[{id,v}]}"""
    f = {x["id"]: x.get("v") for x in t.get("fields", [])}
    g = lambda k: f.get(F[k])
    link = s(g("link")).split("\n")[0].strip()
    edu = opt(g("education")) or opt(g("education_old"))
    return dict(
        id=t["id"], name=s(t["name"]), status=s(t["status"]).upper(), link=link, desc=s(g("desc")),
        industry=opts(g("industry")), assessment=s(g("assessment")), benefits=bool(g("benefits")),
        wage=s(g("wage")), skills=s(g("skills")), education=edu, notes=s(g("notes")), other=s(g("other")),
        training=s(g("training")), coworking=opt(g("coworking")), drug=opts(g("drug")), felony=opt(g("felony")),
        tier=opt(g("tier")), tags=[s(x) for x in t.get("tags", []) if s(x)],
        updated=updated_str(t),
    )

if __name__ == "__main__":
    # usage: cu_map.py raw.json outdir  -> writes outdir/<id>.json per task; prints unknown option ids
    raw = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for t in raw:
        r = to_record(t)
        json.dump(r, open(os.path.join(out, r["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("wrote", len(raw), "records; unknown option ids:", sorted(UNKNOWN))
