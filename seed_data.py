"""
Seed TGM Finance with real university data.
Clears existing university/student data and inserts fresh records.
Run: python seed_data.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, University, Student, CommissionDocument

CANADIAN = [
    {
        "name": "Brock University",
        "country": "Canada", "city": "St. Catharines, Ontario", "region": "Canada",
        "commission_rate": 0.0, "contract_status": "Active", "agreement_signed": False,
        "commission_type": "Not Specified",
    },
    {
        "name": "Braemar College",
        "country": "Canada", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": "20% of tuition fees.",
        "contract_start": "01/02/2020", "contract_end": "31/12/2021",
        "target_students": "8 students", "territory": "Global",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Flat Rate",
        "notes": "No longer in partnership. Contract expired.",
    },
    {
        "name": "Carleton University",
        "country": "Canada", "city": "Ottawa, Ontario", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": "15% of tuition fees on undergraduate programs.",
        "contract_start": "01/09/2023", "contract_end": "01/09/2025",
        "review_date": "01/09/2025 – 01/09/2027",
        "territory": "Nigeria, Ghana, Uganda, Kenya",
        "contract_status": "Active", "agreement_signed": False,
        "commission_type": "Flat Rate",
        "commission_rules": '{"type":"flat_pct","rate":15}',
        "notes": "Contract uploaded upon receiving counter-signed copy.",
    },
    {
        "name": "TAIE International Institute",
        "country": "Canada", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% of tuition fees paid by the student in the initial year and 10% in the "
            "subsequent academic years. 10% of tuition fees for each student in a Summer Camp."
        ),
        "contract_start": "October 2023", "contract_end": "October 2026",
        "territory": "Global", "contract_status": "Active", "agreement_signed": False,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"tiered_by_year","tiers":[{"year":1,"rate":15},{"year":2,"rate":10},{"year":3,"rate":10},{"year":4,"rate":10}],"default_rate":10}',
        "notes": "Contract uploaded upon receiving counter-signed copy.",
    },
    {
        "name": "University of Guelph",
        "country": "Canada", "city": "Guelph, Ontario", "region": "Canada",
        "commission_rate": 16.0,
        "commission_notes": (
            "16% of tuition fees on undergraduate programs. "
            "18% of tuition fees on engineering undergraduate programs."
        ),
        "contract_start": "01/11/2022", "contract_end": "15/07/2025",
        "territory": "Nigeria (primary); to represent globally",
        "contract_status": "Active", "agreement_signed": True, "expansion_requested": True,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"by_programme","rules":[{"programme":"engineering","rate":18},{"programme":"undergraduate","rate":16}],"default_rate":16}',
    },
    {
        "name": "Niagara College",
        "country": "Canada", "city": "Welland, Ontario", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": "Under GUS. General Bachelor's programs of 3 or 4 years duration – 15% of Year 1 Base Tuition.",
        "contract_start": "28/07/2021", "contract_end": "28/07/2025",
        "territory": "Nigeria", "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
        "commission_rules": '{"type":"tiered_by_year","tiers":[{"year":1,"rate":15}],"default_rate":0}',
    },
    {
        "name": "University of Windsor",
        "country": "Canada", "city": "Windsor, Ontario", "region": "Canada",
        "commission_rate": 0.0,
        "commission_notes": (
            "Transfer students to all Honours/General Bachelor's programs – $1,000. "
            "Bachelor of Education – $1,000. BEng Tech – $1,000. "
            "Post Baccalaureate / Post Graduate Certificate – $1,000. "
            "Course-based Masters: 1–19 students = $2,000; 20+ students = $2,200."
        ),
        "incentives": "$500 CAD Year 2 Retention Bonus",
        "contract_start": "26/04/2023", "contract_end": "26/04/2026",
        "territory": "Sub-Saharan Africa", "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Fixed Fee",
        "commission_rules": '{"type":"fixed_by_programme","currency":"CAD","rules":[{"programme":"masters","amount":2000},{"programme":"postgraduate","amount":2000},{"programme":"undergraduate","amount":1000},{"programme":"certificate","amount":1000},{"programme":"diploma","amount":1000}],"default_amount":1000}',
    },
    {
        "name": "Alexander College Vancouver",
        "country": "Canada", "city": "Vancouver, British Columbia", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "International students: 20% of tuition fees for Eligible Programs for first three terms. "
            "Canadian citizens or permanent residents: 15% for first three terms."
        ),
        "contract_start": "29/03/2025", "contract_end": "29/03/2028",
        "territory": "Not limited", "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"flat_pct","rate":20,"note":"20% international students, 15% domestic (first 3 terms)"}',
    },
    {
        "name": "Toronto Metropolitan University",
        "country": "Canada", "city": "Toronto, Ontario", "region": "Canada",
        "commission_rate": 12.0,
        "commission_notes": (
            "12% of tuition fees for first year for all Undergraduate programs. "
            "3% for ESL Foundation 1, ESL Foundation II, and English Boost programs."
        ),
        "contract_start": "01/09/2023", "contract_end": "01/09/2024",
        "territory": "Nigeria, Ghana, Uganda",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"by_programme","rules":[{"programme":"eap","rate":3},{"programme":"esl","rate":3},{"programme":"english","rate":3},{"programme":"foundation","rate":3},{"programme":"undergraduate","rate":12}],"default_rate":12}',
        "notes": "No longer in partnership.",
    },
    {
        "name": "Keyano College",
        "country": "Canada", "city": "Fort McMurray, Alberta", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": "15% of tuition fees for the first year.",
        "contract_start": "03/01/2023", "contract_end": "02/01/2025",
        "territory": "Nigeria, Ghana, Uganda, Ethiopia and other African countries",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Flat Rate",
        "commission_rules": '{"type":"tiered_by_year","tiers":[{"year":1,"rate":15}],"default_rate":0}',
    },
    {
        "name": "Saskatchewan Polytechnic",
        "country": "Canada", "city": "Saskatchewan", "region": "Canada",
        "commission_rate": 10.0,
        "commission_notes": (
            "1–5 students: 10% + no bonus. "
            "6–10 students: 10% + $150 per student. "
            "21+ students: 10% + $700 per student. "
            "5% commission for third and fourth academic semesters."
        ),
        "contract_start": "27/03/2023", "contract_end": "31/01/2026",
        "territory": "West Africa", "contract_status": "Active", "agreement_signed": True,
        "expansion_requested": True, "commission_type": "Tiered",
        "commission_rules": '{"type":"tiered_by_volume","tiers":[{"min":1,"max":5,"rate":15,"bonus_per_student":0},{"min":6,"max":10,"rate":15,"bonus_per_student":150},{"min":21,"rate":15,"bonus_per_student":700}]}',
    },
    {
        "name": "Adler University",
        "country": "Canada", "city": "Vancouver, British Columbia", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": "$3,500 Canadian Dollars (approx. 15%) for the first 2 semesters of tuition paid.",
        "contract_start": "18/09/2023", "contract_end": "18/09/2028",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
        "commission_rules": '{"type":"fixed_amount","currency":"CAD","amount":3500}',
    },
    {
        "name": "Trent University",
        "country": "Canada", "city": "Peterborough, Ontario", "region": "Canada",
        "commission_rate": 10.0,
        "commission_notes": (
            "Undergraduate Programs: 10% of net tuition for first two terms. "
            "Trent-ESL English for University: 15% for first two terms. "
            "Postgraduate Certificate: 10% for first two terms."
        ),
        "contract_start": "21/04/2023", "contract_end": "24/04/2023",
        "territory": "Nigeria", "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "By Programme",
        "notes": "No longer in partnership.", "expansion_requested": True,
    },
    {
        "name": "University of Canada West (GUS)",
        "country": "Canada", "city": "Vancouver, British Columbia", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "30% of Tuition Fees for University Access Program. "
            "20% for first academic year's Tuition Fees for Undergraduate Course. "
            "20% for first academic year's Tuition Fees for Graduate Course."
        ),
        "contract_start": "16/06/2025", "contract_end": "Ongoing",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"by_programme","rules":[{"programme":"foundation","rate":30},{"programme":"access","rate":30},{"programme":"undergraduate","rate":20},{"programme":"postgraduate","rate":20},{"programme":"masters","rate":20},{"programme":"graduate","rate":20},{"programme":"mba","rate":20}],"default_rate":20}',
    },
    {
        "name": "Gregorian College",
        "country": "Canada", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": "20% of tuition fees.",
        "contract_start": "13/04/2023", "contract_end": "13/04/2024",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "University of Northern British Columbia",
        "country": "Canada", "city": "Prince George, British Columbia", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": (
            "Undergraduate Studies: 15% first and second term; 8% third and fourth term. "
            "Graduate Studies: 10% of two-term net Tuition Fees."
        ),
        "contract_start": "01/09/2023", "contract_end": "30/09/2024",
        "territory": "Ghana, Nigeria, Uganda (Primary). Secondary: Benin, Burkina Faso, Côte d'Ivoire, Ethiopia, Kenya, Rwanda, South Africa, Tanzania, Togo, Zimbabwe",
        "contract_status": "Expired", "agreement_signed": True, "expansion_requested": True,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"by_programme","rules":[{"programme":"graduate","rate":10},{"programme":"masters","rate":10},{"programme":"phd","rate":10},{"programme":"postgraduate","rate":10},{"programme":"undergraduate","rate":15}],"default_rate":15}',
    },
    {
        "name": "Eton College",
        "country": "Canada", "region": "Canada",
        "commission_rate": 40.0,
        "commission_notes": (
            "First 8 enrolled students in any Recruitment Year: 40% of tuition fees. "
            "9 or more enrolled students: 50% of tuition fees."
        ),
        "contract_start": "October 2023", "contract_end": "October 2026",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
        "commission_rules": '{"type":"tiered_by_volume","tiers":[{"min":1,"max":8,"rate":40},{"min":9,"rate":50}]}',
    },
    {
        "name": "University of Niagara Falls (GUS)",
        "country": "Canada", "city": "Niagara Falls, Ontario", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "30% of Tuition Fees for EAP (English for Academic Purposes). "
            "20% Postgraduate program. 20% Undergraduate program."
        ),
        "contract_start": "11/03/2024", "contract_end": "11/03/2026",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"by_programme","rules":[{"programme":"eap","rate":30},{"programme":"esl","rate":30},{"programme":"english","rate":30},{"programme":"undergraduate","rate":20},{"programme":"postgraduate","rate":20},{"programme":"masters","rate":20},{"programme":"diploma","rate":20}],"default_rate":20}',
    },
    {
        "name": "North York Academy",
        "country": "Canada", "city": "North York, Ontario", "region": "Canada",
        "commission_rate": 30.0,
        "commission_notes": (
            "Year 1 commission = 30% of actual tuition fee. "
            "Year 2 commission = 15% of actual tuition fee. "
            "Year 3 commission = 10% of actual tuition fee. "
            "Year 4 commission = 10% of actual tuition fee."
        ),
        "contract_start": "07/01/2025", "contract_end": "07/01/2027",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
        "commission_rules": '{"type":"tiered_by_year","tiers":[{"year":1,"rate":30},{"year":2,"rate":15},{"year":3,"rate":10},{"year":4,"rate":10}],"default_rate":10}',
    },
    {
        "name": "Sheridan College",
        "country": "Canada", "city": "Brampton, Ontario", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "20% commission of base tuition for English as a Second Language program. "
            "20% commission of base tuition for post-secondary academic program."
        ),
        "contract_start": "01/01/2025", "contract_end": "01/05/2028",
        "territory": "Africa", "contract_status": "Active", "agreement_signed": True,
        "expansion_requested": True, "commission_type": "Flat Rate",
    },
    {
        "name": "Concordia University, Chicago (GUS)",
        "country": "United States", "city": "Chicago, Illinois", "region": "North America",
        "commission_rate": 0.0,
        "commission_notes": (
            "Postgraduate: $1,500 on deposit; $1,500 on Term 2; $1,000 on Term 3. "
            "Undergraduate: $3,000 on deposit; $2,000 on Term 2."
        ),
        "contract_start": "30/08/2024", "contract_end": "30/08/2025",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Fixed Fee",
        "commission_rules": '{"type":"milestone","currency":"USD","by_programme":[{"programme":"postgraduate","milestones":[{"label":"On student deposit","amount":1500},{"label":"Progression to Term 2","amount":1500},{"label":"Progression to Term 3","amount":1000}]},{"programme":"undergraduate","milestones":[{"label":"On student deposit","amount":3000},{"label":"Progression to Term 2","amount":2000}]},{"programme":"masters","milestones":[{"label":"On student deposit","amount":1500},{"label":"Progression to Term 2","amount":1500},{"label":"Progression to Term 3","amount":1000}]}]}',
    },
    {
        "name": "Canadian College of Business and Technology (GUS)",
        "country": "Canada", "region": "Canada",
        "commission_rate": 30.0,
        "commission_notes": "Diploma and Advanced Diploma programmes = 30%. Other programmes = 30%.",
        "contract_start": "04/07/2023", "contract_end": "04/07/2025",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Flat Rate",
        "commission_rules": '{"type":"flat_pct","rate":30}',
    },
    {
        "name": "Ridley College",
        "country": "Canada", "city": "St. Catharines, Ontario", "region": "Canada",
        "commission_rate": 12.0,
        "commission_notes": (
            "12% of full year tuition fees for new international boarding students; 6% for second year. "
            "For 3+ boarding students: 15% for new students and 7.5% for second year."
        ),
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Cape Breton University",
        "country": "Canada", "city": "Sydney, Nova Scotia", "region": "Canada",
        "commission_rate": 0.0,
        "contract_status": "Active", "agreement_signed": False,
        "commission_type": "Not Specified",
    },
]

UK = [
    {
        "name": "Anglia Ruskin University Cambridge",
        "country": "United Kingdom", "region": "UK",
        "commission_type": "No Contract",
        "contract_status": "Unknown",
        "notes": "Contract Not Seen — reached out to the school for it.",
        "agreement_signed": False,
    },
    {
        "name": "Abbey College Malvern",
        "country": "United Kingdom", "region": "UK",
        "commission_notes": "The Commission payable shall be in accordance with the Net Fees List agreed each year in writing.",
        "contract_start": "04/10/2024", "contract_end": "04/10/2027",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Variable",
    },
    {
        "name": "Abertay University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% of the first year's tuition fee for the first 29 students enrolling. "
            "20% of the first year's tuition fee for 30+ students enrolling."
        ),
        "contract_start": "10/10/2024", "contract_end": "09/10/2026",
        "territory": "Nigeria, Ghana, Uganda",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Arden University (GUS)",
        "country": "United Kingdom", "region": "UK",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "Aston University",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "18/03/2026", "contract_end": "31/10/2028",
        "contract_status": "Active", "renewal_options": "Yes",
        "commission_type": "Not Specified",
    },
    {
        "name": "Birkbeck University of London",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 10.0,
        "commission_notes": (
            "1–7 Students (UG and PG) = 10% of tuition fees. "
            "8+ Students (UG and PG) = 15% of tuition fees."
        ),
        "contract_start": "04/03/2020", "contract_end": "Till terminated",
        "territory": "West Africa",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "British Council Agreement (IELTS)",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 0.0,
        "commission_notes": (
            "3–10 entries = £6,000 (new rates effective 1st April 2024). "
            "11–20 entries = £6,500. "
            "21–40 entries = £7,200. "
            "41–100 entries = £8,100. "
            "101+ entries = £9,300."
        ),
        "contract_start": "01/04/2024", "contract_end": "Not indicated",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Fixed Fee",
    },
    {
        "name": "Birmingham City University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–10 Students (UG & PG) = 15% of tuition fees. "
            "11–20 Students (UG & PG) = 17.5% of tuition fees. "
            "21+ Students (UG & PG) = 20% of tuition fees. "
            "Professional English Course = 10% of tuition fees."
        ),
        "incentives": "Volume bonus applies at 21+ students.",
        "contract_start": "01/05/2023", "contract_end": "01/05/2026",
        "target_students": "September: 10, January: 5",
        "territory": "Nigeria and Ghana",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of Bradford",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 10.0,
        "commission_notes": (
            "1–5 UG Home/EU = 10%. 1–5 UG International = 14%. 1–5 UG Final Year = 10%. 1–5 Pre-sessional/Foundation = 10%. "
            "6–10 UG Home/EU = 14%. 6–10 UG International = 18%. 6–10 UG Final Year = 14%. 6–10 Pre-sessional = 14%. "
            "11–15 UG Home/EU = 15%. 11–15 UG International = 19%. 11–15 UG Final Year = 15%. 11–15 Pre-sessional = 15%. "
            "16–25 UG Home/EU = 16%. 16–25 UG International = 20%. 16–25 UG Final Year = 16%. 16–25 Pre-sessional = 16%. "
            "26+ UG Home/EU = 18%. 26+ UG International = 22%. 26+ UG Final Year = 18%. 26+ Pre-sessional = 18%. "
            "PG: 1–5 = 10%, 6–10 = 14%, 11–15 = 15%, 16–25 = 16%, 26+ = 18%."
        ),
        "contract_start": "27/11/2025", "contract_end": "27/11/2029",
        "territory": "Nigeria",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "Brunel University London",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "20% for any undergraduate course (min 1 student/year). "
            "15% for any postgraduate course (min 1 student/year). "
            "12% for MBBS undergraduate program. "
            "10% for Pre-sessional English (4–20 weeks). "
            "15% for Pre-sessional English (21–52 weeks). "
            "10% for Self-funded Study Abroad programme."
        ),
        "contract_start": "11/12/2024", "contract_end": "11/12/2027",
        "target_students": "2025/2026: 8 students; 2026/2027: 12 students",
        "territory": "Nigeria",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "British School of Management and Science",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "2021", "contract_end": "2022",
        "contract_status": "Expired", "commission_type": "Not Specified",
    },
    {
        "name": "Cardiff Metropolitan University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "20% of tuition fees for Year 0 (Foundation Programme). "
            "20% of tuition fees for Year 1–2 of Undergraduate programmes. "
            "15% of tuition fees for Year 3 of Undergraduate programmes. "
            "15% of tuition fees for Postgraduate programmes. "
            "20% of tuition for International Foundation Course and Pre-sessional English."
        ),
        "contract_start": "04/09/2025", "contract_end": "04/09/2028",
        "target_students": (
            "Year 1: 3 student enrolments (Sept 2025, Jan 2026, May 2026). "
            "Year 2: 4 enrolments. Year 3: 5 enrolments."
        ),
        "territory": "Nigeria, Uganda",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "Coventry University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–20 students = 15% of tuition fees. "
            "21–100 students = 17.5% of tuition fees. "
            "101–150 students = 20% of tuition fees. "
            "151+ students = 25% of tuition fees. "
            "Coventry University Wroclaw: £1,000 per International student; £800 per EU student (max 10 students). "
            "Pre-Sessional English = 10% of tuition fees."
        ),
        "contract_start": "01/09/2024", "contract_end": "01/09/2029",
        "territory": "Nigeria, Ghana & Uganda",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Canterbury Christ Church University",
        "country": "United Kingdom", "region": "UK",
        "commission_notes": "Under GUS.",
        "contract_start": "27/09/2021", "contract_end": "27/09/2025",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Not Specified",
    },
    {
        "name": "Cranfield University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 16.0,
        "commission_notes": (
            "1–5 students = 16% for Pre-Masters, Taught Masters, MSc by research, MPhil, MBA (excl. Indian nationals). "
            "6–15 students = 18% for same programmes. "
            "16+ students = 20% for same programmes. "
            "1+ students = 10% for MBA (Indian nationals only). "
            "15% of first year fee for PhD. "
            "10% for pre-sessional English. "
            "15% for part-time courses (first year). "
            "Excluded: Advanced Motorsport Engineering, Advanced Motorsport Mechatronics, Aerospace Vehicle Design (Sept intake), Air Transport Management."
        ),
        "contract_start": "10/03/2025", "contract_end": "10/03/2027",
        "territory": "Nigeria, Ghana & Uganda",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "De Montfort University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 12.5,
        "commission_notes": (
            "1–4 students = 12.5% of the first year tuition (lowest Net Programme fee). "
            "5–9 students = 15% (from student 1). "
            "10–19 students = 17.5% (from student 1). "
            "20+ students = 20% (from student 1) + 5% Bonus on net revenue."
        ),
        "incentives": "5% Bonus of net revenue if 20+ students enrolled.",
        "contract_start": "13/07/2021", "contract_end": "Automatically renewed when commissions paid after September intake",
        "territory": "Sub-Saharan Africa",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Edinburgh Napier University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% of tuition fee (first year) for all degree programmes (UG). "
            "15% for Masters (MA, MBA, MSc) over one year — based on full tuition fee for duration. "
            "10% for pre-sessional English programmes."
        ),
        "contract_start": "15/03/2024", "contract_end": "15/03/2027",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "Heriot-Watt University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "UK Campus: On-campus degree (UG & PG) = 15%. Pre-sessional English = 15%. "
            "Dubai Campus: Degree Entry Programme = 17.5%. Online Programmes = 10%. "
            "Malaysia Campus: 5–9 students = RM5,500; 10–14 = RM13,750; 15–19 = RM27,500; "
            "20–24 = RM41,250; 25–49 = RM55,000; 50+ = RM82,500. "
            "Malaysia On-campus UG (1–2 yr transfer) = 10%; (3–5 yr UG) = 15%; PG = 15%; Foundation = 18%."
        ),
        "contract_start": "01/06/2025", "contract_end": "01/06/2028",
        "territory": "Nigeria, Ghana, Uganda and Kenya",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "Kingston University London",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% of the first year's international full fee. "
            "Additional 10% (of pre-sessional English course fees) where student does pre-sessional prior to starting the full course."
        ),
        "contract_start": "07/01/2025", "contract_end": "30/09/2026",
        "territory": "Africa",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "BPP University Limited",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "25/03/2024", "contract_end": "25/03/2025",
        "target_students": "Minimum 5 students per quarter",
        "territory": "Nigeria, Ghana, and Uganda",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Not Specified",
    },
    {
        "name": "Leeds Beckett University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–15 students (UG & PG) = 15% of tuition fees. "
            "16+ students = 20% (payable retrospectively for students 1–15)."
        ),
        "contract_start": "06/01/2024", "contract_end": "06/01/2027",
        "territory": "Nigeria",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "London South Bank University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–4 students = 15%. 5–14 students = 17.5%. 15–29 students = 20%. 30+ students = 25%."
        ),
        "incentives": (
            "Backdating bonuses: students 1–4 backdated to 17.5% when 5 reached; "
            "1–14 backdated to 20% when 15 reached; 1–29 backdated to 25% when 30 reached."
        ),
        "contract_end": "Till terminated",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Middlesex University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 12.5,
        "commission_notes": (
            "1–5 students = 12.5%. 16+ students = 15%. "
            "10% progressive commission (year 1) for International Foundation Certificate (IFP) continuing to year 1. "
            "10% commission for overseas campuses in Dubai and Malta."
        ),
        "contract_start": "10/03/2025", "contract_end": "10/03/2027",
        "territory": "Africa",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "Northumbria University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 12.0,
        "commission_notes": (
            "1–9 students = 12% of tuition fee for all full-time courses. "
            "10–49 students = 15% of tuition fee. "
            "50+ students = 15% + 2% Volume Bonus."
        ),
        "incentives": "2% Volume Bonus for 50+ students.",
        "contract_start": "04/09/2024", "contract_end": "31/07/2026",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Oxford Brookes University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–10 students = 15%. 11–25 students = 17.5%. 26–200 students = 20%. "
            "201–250 students = 22.5%. 251+ students = 25%."
        ),
        "contract_start": "07/01/2025", "contract_end": "07/01/2028",
        "territory": "Nigeria, Ghana, Uganda",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Queen's University Belfast",
        "country": "United Kingdom", "region": "UK",
        "commission_notes": "Check Mr. Tolu's email for commission details.",
        "contract_start": "01/03/2023", "contract_end": "31/07/2026",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Not Specified",
    },
    {
        "name": "Queen Margaret University",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "12/03/2026", "contract_end": "31/08/2027",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "Robert Gordon University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "UG: 20% of first academic year tuition fees per student. "
            "PG: 1–5 students = 15%; 6–9 students = 17.5%; 10+ students = 20%. "
            "Fixed fee of £500 per Post Application (Tagged Student). "
            "Online Learning = 15% of first year tuition fee."
        ),
        "incentives": "£500 per tagged/post-application student fee.",
        "contract_start": "25/05/2024", "contract_end": "25/05/2027",
        "territory": "Global except the USA",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "Royal Agricultural University",
        "country": "United Kingdom", "region": "UK",
        "contract_status": "Unknown",
        "notes": "Contract requested — not yet received.",
        "commission_type": "No Contract",
    },
    {
        "name": "Royal Holloway University of London",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 10.0,
        "commission_notes": (
            "1–5 students = 10% for UG/PG. 6–9 students = 12% for UG/PG."
        ),
        "contract_start": "01/09/2021", "contract_end": "30/08/2024",
        "contract_status": "Terminated",
        "notes": "Under Study Group now. Contract terminated by the school.",
        "commission_type": "Tiered",
    },
    {
        "name": "University of Salford",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 10.0,
        "commission_notes": "10% commission on tuition fees.",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "Scotland's Rural College (SRUC)",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "Full-time on-campus degree (UG) = 20%. "
            "Full-time on-campus degree (PG) = 15%. "
            "Short course on-campus programme = 15%."
        ),
        "contract_start": "06/03/2024", "contract_end": "06/03/2028",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "Sheffield Hallam University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "20% = overseas fee-paying students enrolling on first year of undergraduate (level 4). "
            "15% = students enrolling on year 2–3 of UG (level 5/6), PG taught (level 7), or PG research. "
            "10% of deposit retained = student withdraws within first 3 weeks. "
            "15% for International Foundation Programme (IFP); additional 20% if student progresses to level 4. "
            "20% = pre-sessional English. 15% = pre-masters. "
            "5% of first year tuition = Visa Assistance commission (where no flat rate commission paid). "
            "15% = distance learning (PG Certificate, PG Diploma, Masters)."
        ),
        "contract_start": "01/04/2025", "contract_end": "31/03/2028",
        "territory": "Nigeria, Ghana & Uganda",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "Swansea University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% of Course Fee for English Language Training Service. "
            "15% of Course Fee for UG or PG degree (first year of study only). "
            "For students progressing from UG to PG, same structure applies."
        ),
        "contract_start": "14/08/2025", "contract_end": "01/06/2027",
        "territory": "Nigeria, Ghana and Uganda",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "Stirling University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "Direct entry students = 20% of the full tuition fee (per intake). "
            "Study Abroad (1 semester or yearly) and International Summer School = 10% of tuition fee."
        ),
        "contract_start": "01/04/2024", "contract_end": "31/03/2027",
        "territory": "Nigeria and Ghana",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "University of Bedfordshire",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "20% of maximum first-year overseas tuition fee for International Foundation Year (IFY). "
            "20% of first year overseas tuition fee for UG academic programmes (1+ year). "
            "20% of first year overseas tuition fee for PG taught programmes (1+ year). "
            "20% of first year overseas tuition fee for PG research (incl. research masters and PhD)."
        ),
        "contract_start": "05/03/2025", "contract_end": "05/03/2027",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "University of Buckingham",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 0.0,
        "commission_notes": (
            "Undergraduate (paid on 1st year only) = £1,600. "
            "Postgraduate (incl. research) = £1,400. "
            "Foundation = £1,000. "
            "Pre-sessional (per term) / Access Course = £300. "
            "Pre-Masters = £500."
        ),
        "incentives": (
            "Tier 1 Bonus: £2,000 for 5 students. "
            "Tier 2 Bonus: £5,000 for 10 students. "
            "Tier 3 Bonus: £8,000 for 15 students. No bonus shall exceed £8,000 per intake."
        ),
        "contract_start": "01/02/2018", "contract_end": "Indefinite",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Fixed Fee",
    },
    {
        "name": "University of Law (GUS)",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "University of Law Business School Courses = 20%. "
            "University of Law Courses (except BPC, LPC, GDL, MA Law) = 20%. "
            "BPC, LPC, GDL, MA Law for first 4 ULaw students = 15%. "
            "BPC, LPC, GDL, MA Law for 5th+ ULaw student = 20%. "
            "SQE courses, SQE 1 & 2 prep = 10%. Online courses = 20%."
        ),
        "incentives": (
            "Tier 1: £2,000 bonus for 5 students. "
            "Tier 2: £5,000 bonus for 10 students. "
            "Tier 3: £8,000 bonus for 15 students. No bonus exceeds £8,000 per intake."
        ),
        "contract_start": "31/10/2024", "contract_end": "Indefinite",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "University of Lincoln",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–10 students = 15% of tuition fee. "
            "11+ students = 20% (20% also paid retrospectively for first 10 students if 11 enrol). "
            "Pre-sessional English = 10% of net total course tuition fee. "
            "£150 nominal commission if student had existing offer and Representative provided additional support."
        ),
        "contract_start": "01/11/2024", "contract_end": "21/10/2027",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of Central Lancashire",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 17.5,
        "commission_notes": (
            "1–10 students = 17.5% commission. "
            "11–30 students = 20% commission. "
            "31+ students = 22.5% commission."
        ),
        "incentives": (
            "5% bonus where: student on Foundation (yr 0) progresses to yr 1 UG; "
            "UG student progresses to yr 2; or UG student progresses to PG yr 1."
        ),
        "contract_start": "01/11/2023", "contract_end": "31/10/2025",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of the Creative Arts International College (GUS)",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–4 students = 15% for all programs. "
            "5–10 students = 20% for all programs. "
            "11+ students = 25% for all programs."
        ),
        "contract_start": "07/05/2021", "contract_end": "07/05/2026",
        "territory": "Nigeria",
        "notes": "Not a direct partnership — through GUS. Did not reply to expansion request.",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of Derby",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–10 students = 15% for standard full-time courses. "
            "11–20 students = 17.5% for standard full-time courses. "
            "21+ students = 20% for standard full-time courses. "
            "Part-time Standard Courses = 15% regardless of numbers. "
            "Non-Standard Courses = flat 15%."
        ),
        "contract_start": "27/10/2025", "contract_end": "31/08/2028",
        "territory": "Sub-Saharan Africa",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of East Anglia",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 12.0,
        "commission_notes": (
            "Sept 2025 / Jan 2026 — Direct PG & PG Research: "
            "1–4 = 12% (£2,887); 5–14 = 15% (£3,609); 15–29 = 17.5% (£4,210); 30+ = 20% (£4,812). "
            "All International UG = 15%. "
            "Visa Advice only (where student had existing offer) = max £500 standalone. "
            "Summer University (by 1st April 2025): 1 = 10%; 2–9 = 12%; 10–20 = 15%; 21+ = 20%."
        ),
        "contract_start": "16/04/2025", "contract_end": "31/01/2027",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "QA Northumbria",
        "country": "United Kingdom", "region": "UK",
        "commission_notes": (
            "Northumbria University Pathway College to Northumbria UG: follow-on commission 15% (yr 1), 10% (yr 2), 10% (yr 3). "
            "Progressing to PG: 15% on PG course. "
            "Pre-Masters or UG at Northumbria London Campus to PG at Northumbria London: 15%."
        ),
        "contract_status": "Active",
        "commission_type": "By Programme",
    },
    {
        "name": "University of East London",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 22.0,
        "commission_notes": (
            "UG university programme = 22% of Revenue. "
            "PG taught (PGT) university programme = 20% of Revenue. "
            "International Foundation Year = 20%. "
            "International Pathway (follow-on to level 4 and 5) = 7.5%. "
            "Pre-sessional English = 20%. "
            "Pre-sessional English progression to UG = 22%. "
            "Pre-sessional English progression to PGT = 20%."
        ),
        "contract_start": "01/09/2022", "contract_end": "31/08/2025",
        "territory": "Global excluding South Asia",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "University of Leicester",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 10.0,
        "commission_notes": (
            "a) 10% of net tuition fee (first year) for campus-based programmes of max 2 years duration. "
            "b) 15% of net tuition fee (first year) for campus-based programmes of 3+ years. "
            "c) 10% for part-time programmes (Bachelor's, Master's, PhD). "
            "d) 10% for English language programmes. "
            "Sept 2026 / Jan & Apr 2027 — Campus PGT: 1–4 = £3,000/student; "
            "5 students = £3,000 + £2,500 bonus; 10 students = £3,000 + £7,500 bonus; 15 = £3,000 + £11,250 bonus. "
            "STEM Foundation / Int Year 1 / UG / PGR: 1–4 = £3,500/student; "
            "5 students = £3,500 + £7,500 bonus; 6+ = £3,500 + £1,500 per additional student."
        ),
        "incentives": "Volume bonuses at 5, 10, 15 students for PGT and STEM/UG/PGR tracks.",
        "contract_start": "24/03/2025", "contract_end": "24/03/2030",
        "territory": "Nigeria",
        "expansion_requested": True,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "University of Hertfordshire",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": "20% of tuition fees for both UG & PG.",
        "contract_start": "01/11/2022", "contract_end": "21/08/2025",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "University of Huddersfield",
        "country": "United Kingdom", "region": "UK",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "University of Greenwich",
        "country": "United Kingdom", "region": "UK",
        "commission_notes": "Contract requested — not yet received.",
        "contract_start": "04/11/2022", "contract_end": "Indefinite",
        "contract_status": "Active",
        "commission_type": "No Contract",
    },
    {
        "name": "University of Northampton",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 12.5,
        "commission_notes": (
            "Sept/Oct intake: 1–5 = 12.5%; 6–9 = 15%; 10–24 = 20%; 25–50 = 22.5%; 51+ = 25%. "
            "Jan/Feb and May/Jun intakes: 1–9 = 15%; 10–20 = 20%; 21–30 = 22.5%; 31+ = 25%. "
            "Note: 11–15 students = 12.5%; 16+ = 15% (secondary tier)."
        ),
        "contract_start": "04/11/2022", "contract_end": "Indefinite",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
        "notes": "Documents are passworded.",
    },
    {
        "name": "University of Plymouth",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "Final year of UG or Masters or PhD = 15% of first year tuition fee. "
            "Entry to second year of UG = 20% of first year tuition fee. "
            "Entry to first year of UG = 25% of first year tuition fee. "
            "Pre-sessional English = 20% of course fee. "
            "International students paying home fees = 10% of first year tuition fee. "
            "Visa Advice only = one-off £290 consultation fee. "
            "No commission on 2-week programme, Medicine/Dentistry, MBA Top-up, Visiting Scholars, US Federal Aid students."
        ),
        "contract_start": "05/07/2025", "contract_end": "05/07/2027",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "University of Portsmouth",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "Full-time PG taught or research programme = 15% of first year tuition fees. "
            "Full-time UG programme = 15% of first year tuition fees. "
            "Short-term Programmes = 15% of first year tuition fees. "
            "UG student progressing to PG = 10% of tuition fees after alumni discount."
        ),
        "contract_start": "30/05/2019", "contract_end": "Indefinite",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "University of Portsmouth (London Campus)",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–5 students recruited = 15% commission. "
            "6+ students recruited = 20% commission. (2025/2026 Academic Intake)"
        ),
        "contract_start": "2025/2026 intake", "contract_end": "Intake based",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of Strathclyde",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 12.5,
        "commission_notes": (
            "1–5 enrolments = 12.5% (standard). "
            "Sept 2026 / Jan 2027 tiered: base 1–5 = 15%; 6–15 = 17.5%; 16–25 = 20%; 26+ = 25%. "
            "Tiered commission paid on students above base figure. "
            "Sept 2027+ reverts to standard rates unless otherwise notified."
        ),
        "contract_start": "07/11/2022", "contract_end": "Indefinite",
        "territory": "Africa and UAE",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of Sunderland",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% commission of tuition fee (invoices must be submitted on time). "
            "EAP students = 10%. "
            "Students progressing from CEG OnCampus Sunderland = 10%. "
            "Premium commission 20% (1st August 2025 – 31st July 2026). "
            "20% premium commission till August 2027."
        ),
        "incentives": "Premium commission of 20% from Aug 2025 to Aug 2027.",
        "contract_start": "01/09/2024", "contract_end": "31/08/2029",
        "target_students": "2024/25: 10, 2025/26: 15, 2026/27: 20, 2027/28: 25, 2028/29: 25",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "University of Sussex",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 10.0,
        "commission_notes": (
            "1–9 UG/PG students = 10% commission. "
            "10+ students = 15% commission. "
            "1–10 Pre-sessional students = 10%. "
            "11+ Pre-sessional students = 15%. "
            "MBA Courses = 20%. Medical School PG = 10%. "
            "UG Summer courses = 20%. Study Abroad = 15%."
        ),
        "incentives": "£15,000 bonus when 20 students register.",
        "contract_start": "April 2024", "contract_end": "April 2027",
        "territory": "Nigeria",
        "expansion_requested": False,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
        "notes": "Contract sent to partnership.legal email in Feb 2020. Co-signed agreement not confirmed.",
    },
    {
        "name": "University of Teesside",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 16.0,
        "commission_notes": "16% of tuition fee (flat rate).",
        "incentives": (
            "Performance bonus: £180/student for 11+ students. "
            "£270/student for 16+ students. £368/student for 25+ students."
        ),
        "contract_start": "27/03/2023", "contract_end": "26/03/2026",
        "target_students": "10 students",
        "territory": "Uganda and Africa",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "University of Ulster",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "UG International: 15% of gross fee + £1,500 bonus/student + 5% on gross fee in year 2. "
            "PG International: 15% of gross fee + £1,000 bonus/student. "
            "PhD (fee-paying): 15% of gross fee (first year only) + £1,000 bonus/student. "
            "Volume tiers: up to 5 students = 15%; 6–10 = 17.5% on additional students; 11+ = 20% on additional students."
        ),
        "incentives": "£1,500 bonus per UG student; £1,000 bonus per PG/PhD student.",
        "contract_start": "24/04/2024", "contract_end": "20/07/2025",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "University of West England, Bristol",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–7 students = 15% commission. "
            "8+ students = 20% commission."
        ),
        "contract_start": "01/02/2021", "contract_end": "31/01/2026",
        "territory": "Nigeria",
        "expansion_requested": False,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of West London",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "16/06/2026", "contract_end": "01/03/2029",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "University of Wolverhampton",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "1–24 students = 20%. "
            "25+ students = 25%."
        ),
        "incentives": "Marketing Incentive of £5,000 (one-off per academic year) when 50+ students enrolled.",
        "contract_start": "01/07/2025", "contract_end": "31/08/2027",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of South Wales",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–9 students for Bachelor and PG courses = 15%. "
            "10–19 students = 17.5%. "
            "20+ students = 20%."
        ),
        "incentives": (
            "1–4 additional students = £500/student bonus. "
            "5–9 additional students = £700/student. "
            "10–19 additional students = £850/student. "
            "20+ additional students = £1,000/student."
        ),
        "contract_start": "03/09/2025", "contract_end": "31/08/2027",
        "territory": "Nigeria, Ghana, Uganda",
        "expansion_requested": False,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Mander Portman Woodward College",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% commission for the first year of study. "
            "10% commission for subsequent years of study."
        ),
        "contract_start": "10/11/2022", "contract_end": "10/11/2022",
        "territory": "Nigeria, United States, Ireland, Canada, UAE, Australia, Germany, Malaysia, Mauritius, Cyprus",
        "contract_status": "Expired",
        "notes": "No longer in partnership.",
        "commission_type": "By Programme",
    },
    {
        "name": "International College Portsmouth",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "15% commission. "
            "10% commission for UG students who convert to PG students."
        ),
        "contract_start": "30/05/2012", "contract_end": "Indefinite",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "International College Robert Gordon",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": "15% commission.",
        "contract_start": "01/01/2023", "contract_end": "01/01/2024",
        "territory": "Australia, UAE, Singapore, New Zealand, USA, Canada, UK, Germany, Netherlands, Nigeria",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "Glyndwr University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–4 students = 15%. "
            "5–9 students = 17.5%. "
            "10+ students = 20%."
        ),
        "incentives": "£500 extra commission per student (UG; September 2025 only).",
        "contract_start": "25/11/2022", "contract_end": "01/11/2023",
        "territory": "Nigeria, Ghana and Uganda",
        "expansion_requested": True,
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "We Bridge College",
        "country": "United Kingdom", "region": "UK",
        "commission_notes": "Commission not stated.",
        "contract_start": "23/01/2020", "contract_end": "08/07/2022",
        "expansion_requested": False,
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Not Specified",
    },
    {
        "name": "University of Hull",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "Hull York Medical School (HYMS) full-time programme = 10% per paid student. "
            "All other full-time UG or PG degree programmes (incl. pre-sessional English) = 20% fixed per student (Jan 2025+). "
            "Alternatively, £250 for visa advisory services after conditional offer issued. "
            "Pre-sessional English changes/extensions: no additional commission."
        ),
        "contract_start": "01/10/2025", "contract_end": "31/10/2028",
        "territory": "Sub-Saharan Africa",
        "expansion_requested": False,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "University of Dundee",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "20% of first year tuition fee for Sept 2026, Jan 2027, Sept 2027, Jan 2028 entrants. "
            "MBChB & BDs (UG): £3,500 per student. "
            "DClinDent, MSc Human Clinical Embryology, MSc/MPhil (Research) Life Sciences/Medicine (PG): £3,500 per student. "
            "£1,000 to Representative for visa counselling service (students with accepted offer)."
        ),
        "contract_start": "01/12/2024", "contract_end": "Indefinite",
        "territory": "Global except Thailand",
        "expansion_requested": False,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "University of Nottingham",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 12.0,
        "commission_notes": (
            "12% (below target) = new UG or PGT international fee-paying students. "
            "14% (meeting targets) = new UG or PGT international fee-paying students. "
            "10% = students recruited to Centre for English Language Education (CELE). "
            "£2,000 flat fee per student = PG Research (PGR) programmes. "
            "50% of commission owed = where Agent assists conversion/visa for applicant with prior individual application."
        ),
        "contract_start": "30/04/2025", "contract_end": "30/04/2026",
        "target_students": "10 students",
        "territory": "Nigeria",
        "expansion_requested": False,
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "University of Aberdeen",
        "country": "United Kingdom", "region": "UK",
        "contract_status": "Unknown",
        "notes": "Contract should have been sent since Jan 2022 — no contract received yet.",
        "commission_type": "No Contract",
    },
    {
        "name": "University of Kent",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–20 students = 15%. "
            "21–30 students = 17.5%. "
            "31–60 students = 20%. "
            "61+ students = 25%."
        ),
        "contract_start": "14/03/2024", "contract_end": "14/03/2027",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "University of Birmingham",
        "country": "United Kingdom", "region": "UK",
        "contract_status": "Unknown",
        "notes": "No contract with the school.",
        "commission_type": "No Contract",
    },
    {
        "name": "University of Chester",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–4 students: UG/PG/PGR (excl. MBChB) = 15%; IFP = 15%; Pre-sessional = 10%; Pre-masters = 15%; "
            "Alumni = 7.5%; MBChB = £3,000; Chevening Scholar = £500; other scholarship = £350. "
            "5–9 students: above rates at 17.5% (excl. fixed fees). "
            "10+ students: above rates at 20% (excl. fixed fees). "
            "UG/PG after Pre-sessional or IFP progression = same tier rates."
        ),
        "contract_start": "23/04/2025", "contract_end": "Till terminated",
        "territory": "Nigeria",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Mixed",
    },
    {
        "name": "Leeds Trinity University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 22.0,
        "commission_notes": (
            "Undergraduate Programmes = 22% (effective October 2025 intake). "
            "Postgraduate Programmes = 20% (effective October 2025 intake). "
            "Previously: 15% of actual total net tuition fee received."
        ),
        "contract_start": "24/10/2025", "contract_end": "24/10/2028",
        "target_students": "12 students",
        "territory": "Nigeria, Ghana, Uganda, Benin",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "University of Reading",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": "15% of the first year Net Tuition Fee received by the University for the enrolled Programme.",
        "contract_start": "23/03/2023", "contract_end": "Indefinite",
        "territory": "Worldwide except USA",
        "contract_status": "Active", "agreement_signed": True,
        "notes": "Expecting a counter-signed copy from the school.",
        "commission_type": "Flat Rate",
    },
    {
        "name": "Solent University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": "UG, PG, Top Ups, Study Abroad = 20%.",
        "contract_start": "26/10/2023", "contract_end": "Indefinite until terminated",
        "territory": "Nigeria, Ghana, Uganda",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Flat Rate",
    },
    {
        "name": "Suffolk University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "UG & PG = 15%. "
            "Follow-up commission (one further year of UG study) = 10%. "
            "Follow-on commission for students completing Pre-sessional English and enrolling on main programme = 10%. "
            "7.5% if student previously sourced by a different contracted representative."
        ),
        "contract_start": "29/11/2023", "contract_end": "29/11/2026",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "London School of Business",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 10.0,
        "commission_notes": "10% commission for Year 2 UG students.",
        "contract_status": "Active",
        "commission_type": "Flat Rate",
    },
    {
        "name": "Malvern College",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 17.5,
        "commission_notes": (
            "International Foundation Year / IFP / International Year One / International Graduate Diploma / Pre-Masters = 17.5% "
            "(excluding India, Bangladesh, and Nepal for UEL). "
            "Pathway progression to main degree (first year of main programme only) = 10%. "
            "Direct to UG = 17.5% (excluding India/Bangladesh for UEL; Nepal for UEL Pathways only). "
            "Direct to PG Taught = 15%."
        ),
        "contract_start": "24/11/2023", "contract_end": "24/11/2025",
        "contract_status": "Expired",
        "commission_type": "By Programme",
    },
    {
        "name": "Brighton University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–4 students enrolled = 15%. "
            "5–8 students enrolled = 20%. "
            "9+ students enrolled = 25% (payable on all students). "
            "Pre-sessional programme = 10% (counted separately from main total)."
        ),
        "contract_start": "05/12/2024", "contract_end": "05/12/2025",
        "territory": "Africa",
        "contract_status": "Expired", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Staffordshire University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "1–20 students = 15% of fees (minus scholarships/discounts). "
            "21+ students = 20% of fees (minus scholarships/discounts). "
            "English Language programmes (pre-sessional) and summer schools = 15%."
        ),
        "contract_start": "01/12/2025", "contract_end": "28/02/2027",
        "territory": "Nigeria, Ghana and Uganda",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "Southampton Solent University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 20.0,
        "commission_notes": (
            "September 2025 = 20% of first year tuition (year 1 only). "
            "January 2026 = 15% of first year tuition (year 1 only)."
        ),
        "contract_start": "25/09/2025", "contract_end": "25/09/2028",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "By Programme",
    },
    {
        "name": "Wrexham University",
        "country": "United Kingdom", "region": "UK",
        "commission_rate": 15.0,
        "commission_notes": (
            "First 9 students = 15% of Net Tuition Fee per student (one-off). "
            "10–19 students = 18% of Net Tuition Fee per student. "
            "20–34 students = 20% of Net Tuition Fee per student. "
            "35+ students = 25% of Net Tuition Fee per student."
        ),
        "contract_start": "01/12/2025", "contract_end": "01/12/2026",
        "territory": "Nigeria, Uganda, Ghana",
        "contract_status": "Active", "agreement_signed": True,
        "commission_type": "Tiered",
    },
    {
        "name": "QS Student Apply Ltd",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "18/02/2026", "contract_end": "31/12/2026",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "Regent's University London",
        "country": "United Kingdom", "region": "UK",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "University of East London (under Malvern International)",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "04/02/2026", "contract_end": "04/02/2028",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "University of Wolverhampton (under Malvern International)",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "04/03/2026", "contract_end": "04/03/2028",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "University of Cumbria (under Malvern International)",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "04/04/2026", "contract_end": "04/04/2028",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "Liverpool Hope University (under Malvern International)",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "04/05/2026", "contract_end": "04/05/2028",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
    {
        "name": "Aberystwyth University",
        "country": "United Kingdom", "region": "UK",
        "contract_start": "06/01/2026", "contract_end": "06/01/2028",
        "contract_status": "Active", "commission_type": "Not Specified",
    },
]


def seed():
    with app.app_context():
        print("Clearing existing data …")
        CommissionDocument.query.delete()
        Student.query.delete()
        University.query.delete()
        db.session.commit()

        count = 0
        for data in CANADIAN:
            data.setdefault("country", "Canada")
            data.setdefault("commission_rate", 0.0)
            data.setdefault("agreement_signed", True)
            data.setdefault("contract_status", "Active")
            db.session.add(University(**data))
            count += 1

        for data in UK:
            data.setdefault("country", "United Kingdom")
            data.setdefault("region", "UK")
            data.setdefault("commission_rate", 0.0)
            data.setdefault("agreement_signed", True)
            data.setdefault("contract_status", "Active")
            db.session.add(University(**data))
            count += 1

        db.session.commit()
        print(f"Seeded {count} universities ({len(CANADIAN)} Canadian/North American, {len(UK)} UK).")


if __name__ == "__main__":
    seed()
