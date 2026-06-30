"""
Seed TGM Finance with real university data from both CSV files.
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
    },
    {
        "name": "Braemar College",
        "country": "Canada", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": "20% of tuition fees",
        "contract_start": "01/02/2020", "contract_end": "31/12/2021",
        "target_students": "8 students", "territory": "Global",
        "contract_status": "Expired", "agreement_signed": True,
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
    },
    {
        "name": "Niagara College",
        "country": "Canada", "city": "Welland, Ontario", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": "Under GUS. General Bachelor's programs of 3 or 4 years duration – 15% of Year 1 Base Tuition.",
        "contract_start": "28/07/2021", "contract_end": "28/07/2025",
        "territory": "Nigeria", "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "University of Windsor",
        "country": "Canada", "city": "Windsor, Ontario", "region": "Canada",
        "commission_rate": 0.0,
        "commission_notes": (
            "Transfer students to all Honours and General Bachelor's programs (3 or 4 years) – $1,000. "
            "Bachelor of Education – $1,000 per student. "
            "Bachelor of Engineering Technology (BEng Tech) – $1,000 per student. "
            "Bachelor Programs for University Graduates – $1,000 per student. "
            "Certificate Programs – $1,000 per student. "
            "Post Baccalaureate / Post Graduate Certificate Programs – $1,000. "
            "Course-based Masters / Master of Management: 1–19 students = $2,000; 20+ students = $2,200."
        ),
        "incentives": "$500 CAD Year 2 Retention Bonus",
        "contract_start": "26/04/2023", "contract_end": "26/04/2026",
        "territory": "Sub-Saharan Africa", "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "Alexander College Vancouver",
        "country": "Canada", "city": "Vancouver, British Columbia", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "International students: 20% of tuition fees for Eligible Programs for first three terms. "
            "Canadian citizens or permanent residents: 15% of tuition fees for Eligible Programs for first three terms."
        ),
        "contract_start": "29/03/2025", "contract_end": "29/03/2028",
        "territory": "Not limited", "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "Toronto Metropolitan University",
        "country": "Canada", "city": "Toronto, Ontario", "region": "Canada",
        "commission_rate": 12.0,
        "commission_notes": (
            "12% of tuition fees for first year for all Undergraduate programs. "
            "3% of tuition fees for first year for all ESL Foundation 1 programs. "
            "3% of tuition fees for first year for all ESL Foundation II programs. "
            "3% of tuition fees for first year for English Boost programs."
        ),
        "contract_start": "01/09/2023", "contract_end": "01/09/2024",
        "territory": "Nigeria, Ghana, Uganda",
        "contract_status": "Expired", "agreement_signed": True,
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
    },
    {
        "name": "Saskatchewan Polytechnic",
        "country": "Canada", "city": "Saskatchewan", "region": "Canada",
        "commission_rate": 10.0,
        "commission_notes": (
            "1–5 students (All programs): 10% commission of tuition fees for first and second academic semesters. "
            "6–10 students (All programs): 10% commission + $150 per student. "
            "21+ students (All programs): 10% commission + $700 per student. "
            "5% commission for third and fourth academic semesters."
        ),
        "contract_start": "27/03/2023", "contract_end": "31/01/2026",
        "territory": "West Africa", "contract_status": "Active", "agreement_signed": True,
        "expansion_requested": True,
    },
    {
        "name": "Adler University",
        "country": "Canada", "city": "Vancouver, British Columbia", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": "$3,500 Canadian Dollars (approx. 15%) for the first 2 semesters of tuition paid.",
        "contract_start": "18/09/2023", "contract_end": "18/09/2028",
        "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "Trent University",
        "country": "Canada", "city": "Peterborough, Ontario", "region": "Canada",
        "commission_rate": 10.0,
        "commission_notes": (
            "Undergraduate Programs: 10% of net undergraduate tuition for the first two (2) terms. "
            "Trent-ESL English for University: 15% of net ESL tuition for a maximum of first two (2) terms. "
            "Postgraduate Certificate Programs: 10% of net PGC tuition for the first two (2) terms."
        ),
        "contract_start": "21/04/2023", "contract_end": "24/04/2023",
        "territory": "Nigeria", "contract_status": "Expired", "agreement_signed": True,
        "notes": "No longer in partnership.", "expansion_requested": True,
    },
    {
        "name": "University of Canada West (GUS)",
        "country": "Canada", "city": "Vancouver, British Columbia", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "30% of the Tuition Fees paid by the student for the University Access Program. "
            "20% commission of the first academic year's Tuition Fees for an Undergraduate Course. "
            "20% of the first academic year's Tuition Fees for a Graduate Course."
        ),
        "contract_start": "16/06/2025", "contract_end": "Ongoing",
        "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "Gregorian College",
        "country": "Canada", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": "20% of tuition fees.",
        "contract_start": "13/04/2023", "contract_end": "13/04/2024",
        "contract_status": "Expired", "agreement_signed": True,
    },
    {
        "name": "University of Northern British Columbia",
        "country": "Canada", "city": "Prince George, British Columbia", "region": "Canada",
        "commission_rate": 15.0,
        "commission_notes": (
            "Undergraduate Studies: 15% first and second term Tuition Fees; 8% third and fourth term Tuition Fees. "
            "Graduate Studies: 10% of two-term net Tuition Fees."
        ),
        "contract_start": "01/09/2023", "contract_end": "30/09/2024",
        "territory": (
            "Ghana, Nigeria, Uganda (Primary). "
            "Secondary: Benin, Burkina Faso, Côte d'Ivoire, Ethiopia, Kenya, Rwanda, South Africa, Tanzania, Togo, Zimbabwe"
        ),
        "contract_status": "Expired", "agreement_signed": True, "expansion_requested": True,
    },
    {
        "name": "Eton College",
        "country": "Canada", "region": "Canada",
        "commission_rate": 40.0,
        "commission_notes": (
            "For the first 8 enrolled students in any Recruitment Year: 40% of the tuition fees paid. "
            "For 9 or more enrolled students in any Recruitment Year: 50% of the tuition fees paid."
        ),
        "contract_start": "October 2023", "contract_end": "October 2026",
        "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "University of Niagara Falls (GUS)",
        "country": "Canada", "city": "Niagara Falls, Ontario", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "30% of the Tuition Fees for the EAP (English for Academic Purposes). "
            "20% Postgraduate program. 20% Undergraduate program."
        ),
        "contract_start": "11/03/2024", "contract_end": "11/03/2026",
        "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "North York Academy",
        "country": "Canada", "city": "North York, Ontario", "region": "Canada",
        "commission_rate": 30.0,
        "commission_notes": (
            "First year commission = 30% of the actual tuition fee. "
            "Second year commission = 15% of the actual tuition fee. "
            "Third year commission = 10% of the actual tuition fee. "
            "Fourth year commission = 10% of the actual tuition fee."
        ),
        "contract_start": "07/01/2025", "contract_end": "07/01/2027",
        "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "Sheridan College",
        "country": "Canada", "city": "Brampton, Ontario", "region": "Canada",
        "commission_rate": 20.0,
        "commission_notes": (
            "20% commission percentage of base tuition for English as a Second Language program. "
            "20% commission percentage of base tuition for post-secondary academic program."
        ),
        "contract_start": "01/01/2025", "contract_end": "01/05/2028",
        "territory": "Africa", "contract_status": "Active", "agreement_signed": True,
        "expansion_requested": True,
    },
    {
        "name": "Concordia University, Chicago (GUS)",
        "country": "United States", "city": "Chicago, Illinois", "region": "North America",
        "commission_rate": 0.0,
        "commission_notes": (
            "Postgraduate: $1,500 upon student deposit received; $1,500 upon progression to Term 2; $1,000 upon progression to Term 3. "
            "Undergraduate: $3,000 upon student deposit received; $2,000 upon progression to Term 2."
        ),
        "contract_start": "30/08/2024", "contract_end": "30/08/2025",
        "contract_status": "Expired", "agreement_signed": True,
    },
    {
        "name": "Canadian College of Business and Technology (GUS)",
        "country": "Canada", "region": "Canada",
        "commission_rate": 30.0,
        "commission_notes": "Diploma and Advanced Diploma programmes = 30%. Other programmes = 30%.",
        "contract_start": "04/07/2023", "contract_end": "04/07/2025",
        "contract_status": "Expired", "agreement_signed": True,
    },
    {
        "name": "Ridley College",
        "country": "Canada", "city": "St. Catharines, Ontario", "region": "Canada",
        "commission_rate": 12.0,
        "commission_notes": (
            "12% of full year tuition fees for new international boarding students and 6% for second year. "
            "For 3 or more international boarding students: 15% for new students and 7.5% for second year."
        ),
        "contract_status": "Active", "agreement_signed": True,
    },
    {
        "name": "Cape Breton University",
        "country": "Canada", "city": "Sydney, Nova Scotia", "region": "Canada",
        "commission_rate": 0.0,
        "contract_status": "Active", "agreement_signed": False,
    },
]

UK = [
    {"name": "Aberystwyth University", "duration": "2 years", "contract_start": "06/01/2026", "contract_end": "06/01/2028", "contract_status": "Active"},
    {"name": "Abbey College Malvern", "duration": "3 years", "contract_start": "04/10/2024", "contract_end": "04/10/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Abertay University", "duration": "2 years", "contract_start": "10/10/2024", "contract_end": "09/10/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Arden University (GUS)", "contract_status": "Active"},
    {"name": "Aston University", "duration": "2 years", "contract_start": "18/03/2026", "contract_end": "31/10/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Birkbeck University of London", "duration": "Not specified", "contract_start": "04/03/2020", "contract_end": "Till terminated", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "British Council Agreement (IELTS)", "duration": "Not specified", "contract_start": "01/04/2024", "contract_end": "Not indicated", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Birmingham City University", "duration": "3 years", "contract_start": "01/05/2023", "contract_end": "01/05/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Bradford", "duration": "4 years", "contract_start": "27/11/2025", "contract_end": "27/11/2029", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Brunel University London", "duration": "3 years", "contract_start": "11/12/2024", "contract_end": "11/12/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "British School of Management and Science", "contract_start": "2021", "contract_end": "2022", "contract_status": "Expired", "renewal_options": "No"},
    {"name": "Cardiff Metropolitan University", "duration": "3 years", "contract_start": "04/09/2025", "contract_end": "04/09/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Coventry University", "duration": "5 years", "contract_start": "01/09/2025", "contract_end": "01/09/2031", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Canterbury Christ Church University", "duration": "2 years", "contract_start": "12/01/2026", "contract_end": "12/01/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Cranfield University", "duration": "4 years", "contract_start": "10/03/2025", "contract_end": "10/03/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "De Montfort University", "contract_start": "13/07/2021", "contract_end": "Automatically renewed when commissions paid after September intake", "contract_status": "Active", "renewal_options": "Undecided"},
    {"name": "Edinburgh Napier University", "duration": "3 years", "contract_start": "15/03/2024", "contract_end": "15/03/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Heriot-Watt University", "duration": "3 years", "contract_start": "01/06/2025", "contract_end": "01/06/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Kingston University London", "duration": "1 year", "contract_start": "07/01/2025", "contract_end": "30/09/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "BPP University Limited", "contract_start": "25/03/2024", "contract_end": "25/03/2025", "contract_status": "Expired", "renewal_options": "Not yet"},
    {"name": "Leeds Beckett University", "duration": "3 years", "contract_start": "06/01/2024", "contract_end": "06/01/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "London South Bank University", "duration": "Not specified", "contract_start": "09/12/2024", "contract_end": "Till terminated", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Middlesex University", "duration": "2 years", "contract_start": "10/03/2025", "contract_end": "10/03/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Northumbria University", "duration": "2 years", "contract_start": "04/09/2024", "contract_end": "31/07/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Oxford Brookes University", "duration": "3 years", "contract_start": "07/01/2025", "contract_end": "07/01/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Queen's University Belfast", "duration": "3 years", "contract_start": "01/03/2023", "contract_end": "31/07/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Queen Margaret University", "duration": "1 year", "contract_start": "12/03/2026", "contract_end": "31/08/2027", "contract_status": "Active"},
    {"name": "Robert Gordon University", "duration": "3 years", "contract_start": "25/05/2024", "contract_end": "25/05/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Royal Agricultural University", "contract_status": "Unknown", "notes": "Contract information not found."},
    {"name": "Royal Holloway University of London", "duration": "3 years", "contract_start": "01/09/2021", "contract_end": "30/08/2024", "contract_status": "Terminated", "renewal_options": "No", "notes": "Under Study Group. Partnership terminated."},
    {"name": "Regent's University London", "contract_status": "Active"},
    {"name": "University of Salford", "contract_status": "Active"},
    {"name": "Scotland's Rural College (SRUC)", "duration": "1 year", "contract_start": "06/03/2025", "contract_end": "06/03/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Sheffield Hallam University", "duration": "3 years", "contract_start": "01/04/2025", "contract_end": "31/03/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Swansea University", "duration": "2 years", "contract_start": "14/08/2025", "contract_end": "01/06/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Stirling University", "duration": "3 years", "contract_start": "01/04/2024", "contract_end": "31/03/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Bedfordshire", "duration": "2 years", "contract_start": "05/03/2025", "contract_end": "05/03/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Buckingham", "contract_start": "01/02/2018", "contract_end": "Notice to terminate sent March 2025", "contract_status": "Terminated"},
    {"name": "University of Law (GUS)", "contract_start": "31/10/2024", "contract_end": "Indefinite", "contract_status": "Active"},
    {"name": "University of Lincoln", "duration": "3 years", "contract_start": "01/04/2024", "contract_end": "21/10/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Central Lancashire", "duration": "2 years", "contract_start": "01/11/2025", "contract_end": "31/07/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of the Creative Arts International College (GUS)", "duration": "5 years", "contract_start": "01/04/2026", "contract_end": "07/05/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Derby", "duration": "3 years", "contract_start": "27/10/2025", "contract_end": "31/08/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of East Anglia", "duration": "2 years", "contract_start": "16/04/2025", "contract_end": "31/01/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of East London", "duration": "3 years", "contract_start": "01/09/2025", "contract_end": "31/08/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Leicester", "contract_start": "11/02/2025", "contract_end": "11/02/2030", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Hertfordshire", "duration": "3 years", "contract_start": "01/11/2025", "contract_end": "31/08/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Huddersfield", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Greenwich", "contract_start": "04/11/2022", "contract_end": "Indefinite", "contract_status": "Active"},
    {"name": "University of Northampton", "contract_status": "Unknown", "notes": "Documents passworded."},
    {"name": "University of Plymouth", "duration": "2 years", "contract_start": "05/07/2025", "contract_end": "05/07/2027", "contract_status": "Active"},
    {"name": "University of Portsmouth", "duration": "3 years", "contract_start": "10/11/2023", "contract_end": "31/07/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Portsmouth (London Campus)", "contract_start": "2025/2026 intake", "contract_end": "Intake based", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Strathclyde", "contract_start": "07/11/2022", "contract_end": "Indefinite", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Sunderland", "duration": "5 years", "contract_start": "01/09/2024", "contract_end": "31/08/2029", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Sussex", "duration": "3 years", "contract_start": "April 2024", "contract_end": "April 2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Teesside", "duration": "3 years", "contract_start": "27/03/2023", "contract_end": "26/03/2026", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Ulster", "duration": "2 years", "contract_start": "21/07/2025", "contract_end": "20/07/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of West England, Bristol", "duration": "5 years", "contract_start": "01/02/2026", "contract_end": "31/01/2031", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of West London", "duration": "3 years", "contract_start": "16/06/2026", "contract_end": "01/03/2029", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Wolverhampton", "duration": "2 years", "contract_start": "01/07/2025", "contract_end": "31/08/2027", "contract_status": "Active"},
    {"name": "University of South Wales", "duration": "2 years", "contract_start": "03/09/2025", "contract_end": "31/08/2027", "contract_status": "Active"},
    {"name": "Mander Portman Woodward College", "contract_start": "10/11/2022", "contract_end": "10/11/2022", "contract_status": "Expired"},
    {"name": "International College Portsmouth", "contract_start": "30/05/2012", "contract_end": "Indefinite", "contract_status": "Active"},
    {"name": "International College Robert Gordon", "duration": "1 year", "contract_start": "01/01/2023", "contract_end": "01/01/2024", "contract_status": "Expired"},
    {"name": "Glyndwr University", "duration": "1 year", "contract_start": "25/11/2022", "contract_end": "01/11/2023", "contract_status": "Expired"},
    {"name": "We Bridge College", "contract_start": "25/01/2023", "contract_end": "25/01/2025", "contract_status": "Expired"},
    {"name": "University of Hull", "duration": "3 years", "contract_start": "01/10/2025", "contract_end": "01/10/2028", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "University of Dundee", "contract_start": "01/12/2024", "contract_end": "Indefinite", "contract_status": "Active"},
    {"name": "University of Nottingham", "duration": "2 years", "contract_start": "30/04/2025", "contract_end": "30/04/2026", "contract_status": "Active"},
    {"name": "University of Aberdeen", "contract_status": "Active"},
    {"name": "QA Northumbria", "contract_status": "Active"},
    {"name": "University of Kent", "duration": "3 years", "contract_start": "14/03/2024", "contract_end": "14/03/2027", "contract_status": "Active"},
    {"name": "University of Birmingham", "contract_status": "Active"},
    {"name": "University of Chester", "contract_start": "23/04/2025", "contract_end": "Till terminated", "contract_status": "Active"},
    {"name": "Leeds Trinity University", "duration": "3 years", "contract_start": "24/10/2025", "contract_end": "24/10/2028", "contract_status": "Active"},
    {"name": "University of Reading", "contract_start": "23/03/2023", "contract_end": "Indefinite", "contract_status": "Active"},
    {"name": "Solent University", "contract_start": "26/10/2023", "contract_end": "Indefinite until terminated", "contract_status": "Active"},
    {"name": "Suffolk University", "duration": "3 years", "contract_start": "29/11/2023", "contract_end": "29/11/2026", "contract_status": "Active"},
    {"name": "London School of Business", "contract_status": "Active"},
    {"name": "Malvern College", "duration": "2 years", "contract_start": "24/11/2023", "contract_end": "24/11/2025", "contract_status": "Expired"},
    {"name": "Brighton University", "duration": "1 year", "contract_start": "05/12/2024", "contract_end": "05/12/2025", "contract_status": "Expired"},
    {"name": "Staffordshire University", "duration": "2 years", "contract_start": "01/12/2025", "contract_end": "28/02/2027", "contract_status": "Active", "renewal_options": "Yes"},
    {"name": "Southampton Solent University", "duration": "3 years", "contract_start": "25/09/2025", "contract_end": "25/09/2028", "contract_status": "Active"},
    {"name": "Wrexham University", "duration": "1 year", "contract_start": "01/12/2025", "contract_end": "01/12/2026", "contract_status": "Active"},
    {"name": "QS Student Apply Ltd", "duration": "1 year", "contract_start": "18/02/2026", "contract_end": "31/12/2026", "contract_status": "Active"},
    {"name": "University of East London (under Malvern International)", "duration": "2 years", "contract_start": "04/02/2026", "contract_end": "04/02/2028", "contract_status": "Active"},
    {"name": "University of Wolverhampton (under Malvern International)", "duration": "3 years", "contract_start": "04/03/2026", "contract_end": "04/03/2028", "contract_status": "Active"},
    {"name": "University of Cumbria (under Malvern International)", "duration": "4 years", "contract_start": "04/04/2026", "contract_end": "04/04/2028", "contract_status": "Active"},
    {"name": "Liverpool Hope University (under Malvern International)", "duration": "5 years", "contract_start": "04/05/2026", "contract_end": "04/05/2028", "contract_status": "Active"},
]


def seed():
    with app.app_context():
        print("Clearing existing test data …")
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
