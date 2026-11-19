import os
import json
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas that generates page numbers dynamically on two-pass rendering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header
        self.drawString(54, 750, "DROSAT Educational Platform - Official Knowledge Base (Catalog 2026)")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.line(54, 50, 558, 50)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, page_str)
        self.drawString(54, 38, "CONFIDENTIAL & PROPRIETARY - DROSAT RAG KNOWLEDGE BASE")
        self.restoreState()

def generate_items():
    items = []
    
    # -------------------------------------------------------------
    # Sector 1: courses_curriculum (400 items: CRS-0001 to CRS-0400)
    # -------------------------------------------------------------
    subjects = [
        ("Physics", ["Classical Mechanics", "Electromagnetism", "Modern Physics", "Wave Optics", "Thermodynamics", "Nuclear Physics"]),
        ("Chemistry", ["Organic Chemistry", "Analytical Chemistry", "Electrochemistry", "Transition Elements", "Chemical Equilibrium"]),
        ("Mathematics", ["Calculus & Integration", "Algebra & Solid Geometry", "Statics", "Dynamics", "Trigonometry", "Statistics"]),
        ("Biology", ["Molecular Genetics", "Human Physiology", "Immune System", "Reproduction in Living Organisms", "Cellular Biology"]),
        ("Arabic Language", ["Advanced Grammar (Nahw)", "Rhetoric (Balagha)", "Literature & Texts", "Reading Comprehension", "Spelling & Dictation"]),
        ("English Language", ["Advanced Grammar & Syntax", "Vocabulary in Context", "Novel Analysis (Great Expectations)", "Essay Writing"]),
        ("French Language", ["Grammar & Verb Conjugations", "Situational Dialogues", "Reading Comprehension", "Written Expression"]),
        ("German Language", ["A1-B1 Grammar", "Conversational Skills", "Vocabulary Drills", "Reading Strategies"]),
        ("History", ["Modern Egyptian History (1919-1952)", "Ottoman Era in Egypt", "World War II In-depth", "Arab Nationalism"]),
        ("Geography", ["Political Geography", "Geopolitical Boundaries", "Global Natural Resources", "Economic Development Geography"]),
        ("Philosophy & Logic", ["Applied Ethics & Bioethics", "Environmental Philosophy", "Formal Logic & Syllogism", "Scientific Method"])
    ]
    
    grade_levels = [
        "1st Secondary (Grade 10)",
        "2nd Secondary - Scientific (Grade 11)",
        "2nd Secondary - Literary (Grade 11)",
        "3rd Secondary / Thanaweya Amma (Grade 12)",
        "3rd Preparatory (Grade 9)"
    ]
    
    instructors = [
        "Mr. Mohamed Abdelmaaboud", "Dr. Hany El-Sayed", "Mr. Ahmed Essam", "Prof. Mahmoud Soliman",
        "Mr. Tarek El-Kady", "Dr. Sherif Maged", "Ms. Rania Tawfik", "Mr. Yasser Ragab",
        "Dr. Walid Radwan", "Mr. Karim Fouad", "Prof. Ezzat Kamel", "Mr. Haitham Sabry"
    ]
    
    item_counter = 1
    for i in range(400):
        item_id = f"CRS-{item_counter:04d}"
        subj_name, modules = subjects[i % len(subjects)]
        grade = grade_levels[i % len(grade_levels)]
        instructor = instructors[i % len(instructors)]
        module = modules[(i // len(subjects)) % len(modules)]
        price = random.choice([120, 150, 180, 200, 220, 250, 280, 320])
        lesson_count = random.choice([6, 8, 10, 12, 16])
        hours = lesson_count * 2
        
        content = (
            f"Course Code: {item_id}. Subject: {subj_name} for {grade}. "
            f"Course Title: {subj_name} Intensive Mastery: {module}. "
            f"Lead Instructor: {instructor}. "
            f"Curriculum Overview: Comprehensive course covering {module} in depth with weekly problem sets, "
            f"past exam walkthroughs, and conceptual assessments tailored to the Ministry of Education exam specifications. "
            f"Structure: {lesson_count} full video lectures ({hours} academic hours), includes 2 milestone quizzes, "
            f"and downloadable PDF study notes. "
            f"Enrollment Price: {price} EGP per month. Access validity: 60 days from purchase with unlimited playback."
        )
        
        items.append({
            "item_id": item_id,
            "sector": "courses_curriculum",
            "title": f"{subj_name} - {module} ({grade})",
            "content": content
        })
        item_counter += 1
        
    # -------------------------------------------------------------
    # Sector 2: teachers_centers (300 items: TCH-0001 to TCH-0300)
    # -------------------------------------------------------------
    centers = [
        ("Al-Amal Educational Center", "Nasr City, Abbas El-Akkad St, Cairo"),
        ("Al-Safwa Academy", "Maadi, Degla Zone, Cairo"),
        ("Smart Vision Center", "Dokki, Mesaha Square, Giza"),
        ("Future Generation Center", "Mohandessin, Shehab St, Giza"),
        ("Al-Tahrir Learning Hub", "Heliopolis, Korba District, Cairo"),
        ("Alexandria Scholars Center", "Roushdy, Horreya Avenue, Alexandria"),
        ("Smouha Excellence Center", "Smouha, Victor Emmanuel Square, Alexandria"),
        ("Mansoura Academic Center", "Gomhoureya St, Mansoura"),
        ("Tanta Educational Hall", "El-Bahr St, Tanta"),
        ("Zagazig Elite Center", "Mohafza District, Zagazig"),
        ("New Cairo Educational Complex", "5th Settlement, North 90th St, New Cairo"),
        ("El-Sherouk Learning Center", "District 1, El-Sherouk City")
    ]
    
    days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    shifts = ["10:00 AM - 12:00 PM", "01:00 PM - 03:00 PM", "03:30 PM - 05:30 PM", "06:00 PM - 08:00 PM"]
    
    for i in range(300):
        item_id = f"TCH-{i+1:04d}"
        subj_name, _ = subjects[i % len(subjects)]
        grade = grade_levels[i % len(grade_levels)]
        instructor = instructors[i % len(instructors)]
        center_name, address = centers[i % len(centers)]
        day_slot = days[i % len(days)]
        alt_day = days[(i + 3) % len(days)]
        shift = shifts[i % len(shifts)]
        room = f"Hall {random.choice(['A', 'B', 'C', 'Auditorium 1', 'Main Theater'])}"
        capacity = random.choice([60, 80, 100, 150, 200])
        phone = f"01{random.choice(['0', '1', '2', '5'])}{random.randint(10000000, 99999999)}"
        
        content = (
            f"Teacher Schedule & Center ID: {item_id}. "
            f"Instructor: {instructor}. Specialty: {subj_name} for {grade}. "
            f"Affiliated Educational Center: {center_name}, located at {address}. "
            f"Weekly Attendance Times: Every {day_slot} and {alt_day} during shift {shift} in {room} (Seat Capacity: {capacity} students). "
            f"Seat Booking Protocol: Requires DROSAT student QR badge or platform admission voucher. "
            f"Direct Center Assistance Hotline: {phone} (Available 9:00 AM to 9:00 PM). "
            f"Facilities: Air-conditioned auditorium, high-definition live screens, and strict attendance scanning."
        )
        
        items.append({
            "item_id": item_id,
            "sector": "teachers_centers",
            "title": f"{instructor} @ {center_name} ({subj_name})",
            "content": content
        })

    # -------------------------------------------------------------
    # Sector 3: policies_support (300 items: POL-0001 to POL-0300)
    # -------------------------------------------------------------
    policy_topics = [
        "Kashier Payment Gateway Integration & Card Verification",
        "Fawry Offline Payment Code Generation & Expiration Policy",
        "Vodafone Cash & Mobile Wallet Direct Top-up Workflow",
        "Printed Booklet & Physical Homework Sheet Courier Delivery",
        "Lesson Access Code Redemption & Device Binding Rules",
        "Course Refund & Subscription Cancellation Guarantee Policy",
        "Video Streaming Playback Troubleshooting & Quality Controls",
        "Account Security, Two-Factor Authentication & Multi-Device Ban",
        "Parental Dashboard Linking & Progress Report Notifications",
        "Exam Anti-Cheating System & Automatic Tab-Switch Locking",
        "Student Community Guidelines & Comment Moderation Rules",
        "Scholarship Program & Honor Student Fee Exemption Protocol",
        "Offline Download Access via DROSAT Mobile App",
        "Technical Helpdesk Escalation & WhatsApp Support SLAs",
        "Lost Code Replacement & Payment Proof Verification Guidelines"
    ]
    
    for i in range(300):
        item_id = f"POL-{i+1:04d}"
        topic = policy_topics[i % len(policy_topics)]
        sub_id = (i // len(policy_topics)) + 1
        
        content = (
            f"Platform Policy & Support Item: {item_id}. "
            f"Category / Subject: {topic} (Clause {sub_id}). "
            f"Rule Specifics & Procedural Standard: Students transacting on DROSAT under {topic} "
            f"must comply with platform operational standard {item_id}. For payments via Kashier or Fawry, "
            f"transaction confirmation is processed asynchronously within 120 seconds. Fawry reference numbers remain "
            f"valid for exactly 48 hours from checkout generation. If booklet shipping is requested, deliveries "
            f"to Greater Cairo arrive within 48 business hours; provincial governorates take 72-96 hours via Bosta Courier. "
            f"Device Policy: Each student account is cryptographically bound to a single mobile device and one desktop browser. "
            f"Simultaneous logins trigger a security lock requiring identity verification via registered guardian phone number. "
            f"Dispute Escalation: Submit transaction receipt or inquiry ticket directly to support@drosat.com or hotline 19876."
        )
        
        items.append({
            "item_id": item_id,
            "sector": "policies_support",
            "title": f"{topic} (Rule {item_id})",
            "content": content
        })
        
    return items

def build_pdf(items, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=64
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=20
    )
    
    sector_banner_style = ParagraphStyle(
        'SectorBanner',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=14,
        spaceAfter=8
    )
    
    item_header_style = ParagraphStyle(
        'ItemHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=2
    )
    
    item_body_style = ParagraphStyle(
        'ItemBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=8
    )

    story = []
    
    # Title Page Header
    story.append(Paragraph("DROSAT Educational Platform", title_style))
    story.append(Paragraph(
        "<b>Official Master Catalog & Sector Knowledge Base (2026 Edition)</b><br/>"
        "Total Discrete Structured Items: 1,000 | Sectors: Courses & Curriculum, Teachers & Centers, Policies & Support.<br/>"
        "<i>Engineered for Retrieval-Augmented Generation (RAG) Ingestion & Semantic Search.</i>",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=15))
    
    current_sector = None
    
    for item in items:
        if item['sector'] != current_sector:
            current_sector = item['sector']
            sector_name_clean = current_sector.replace('_', ' ').upper()
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"SECTOR: {sector_name_clean}", sector_banner_style))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E0"), spaceAfter=8))
        
        flowables = [
            Paragraph(f"<b>[{item['item_id']}]</b> {item['title']} &nbsp;|&nbsp; <i>Sector: {item['sector']}</i>", item_header_style),
            Paragraph(item['content'], item_body_style),
            HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#E2E8F0"), spaceAfter=6)
        ]
        story.append(KeepTogether(flowables))
        
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ PDF build complete: {output_path}")

if __name__ == '__main__':
    items = generate_items()
    print(f"Generated {len(items)} discrete items across 3 sectors:")
    counts = {}
    for it in items:
        counts[it['sector']] = counts.get(it['sector'], 0) + 1
    for sec, cnt in counts.items():
        print(f"  - {sec}: {cnt} items")
        
    pdf_out = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/drosat_knowledge_base.pdf"))
    build_pdf(items, pdf_out)
    
    # Also save structured JSON for reference
    json_out = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/drosat_items.json"))
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON items exported: {json_out}")
