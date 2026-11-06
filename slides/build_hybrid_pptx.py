#!/usr/bin/env python3
"""
Build native widescreen PPTX presentation for TMS Flights project.
Matches the 12-slide hybrid executive deck and embeds full speaker notes.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "TMS_flights_presentation_hybrid.pptx"
NOTES_FILE = Path(__file__).resolve().parent / "speaker_notes_hybrid.md"

# Color Palette
NAVY = RGBColor(0x0B, 0x19, 0x30)
NAVY2 = RGBColor(0x14, 0x29, 0x43)
INK = RGBColor(0x17, 0x2A, 0x43)
MUTED = RGBColor(0x61, 0x73, 0x8A)
PAPER = RGBColor(0xF5, 0xF3, 0xEE)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEAL = RGBColor(0x29, 0xC6, 0xB3)
ORANGE = RGBColor(0xFF, 0xB5, 0x47)
CORAL = RGBColor(0xF0, 0x78, 0x67)
PALE_TEAL = RGBColor(0xDD, 0xF5, 0xEF)
PALE_ORANGE = RGBColor(0xFF, 0xF0, 0xD7)
PALE_BLUE = RGBColor(0xE6, 0xED, 0xF5)
GRID = RGBColor(0xD8, 0xE0, 0xE7)
ACCENT_BLUE = RGBColor(0x66, 0x89, 0xD6)
DARK_CARD = RGBColor(0x1A, 0x2C, 0x47)
DARK_CARD_BORDER = RGBColor(0x29, 0x41, 0x5A)

FONT_HEADING = "Helvetica"
FONT_BODY = "Helvetica"


def load_speaker_notes():
    notes = {}
    if not NOTES_FILE.exists():
        return notes
    content = NOTES_FILE.read_text(encoding="utf-8")
    sections = content.split("## ")
    for sec in sections[1:]:
        lines = sec.strip().split("\n")
        title_line = lines[0].strip()
        num_str = title_line.split(".")[0].strip()
        try:
            num = int(num_str)
            note_body = "\n".join(lines[1:]).strip()
            notes[num] = note_body
        except ValueError:
            continue
    return notes


def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    notes = load_speaker_notes()

    def add_bg(slide, dark=False):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = NAVY if dark else PAPER
        bg.line.fill.background()
        return bg

    def add_header(slide, section, title, subtitle=None, dark=False):
        # Section Pill
        pill = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.65), Inches(0.42), Inches(max(1.2, len(section) * 0.12 + 0.3)), Inches(0.32)
        )
        pill.fill.solid()
        pill.fill.fore_color.rgb = TEAL
        pill.line.fill.background()
        tf = pill.text_frame
        tf.word_wrap = False
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = section.upper()
        p.font.name = FONT_HEADING
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = NAVY

        # Title
        tb = slide.shapes.add_textbox(Inches(0.62), Inches(0.82), Inches(12.0), Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = WHITE if dark else INK

        # Subtitle
        if subtitle:
            tb2 = slide.shapes.add_textbox(Inches(0.64), Inches(1.42), Inches(12.0), Inches(0.35))
            tf2 = tb2.text_frame
            tf2.word_wrap = True
            tf2.margin_left = tf2.margin_right = tf2.margin_top = tf2.margin_bottom = 0
            p2 = tf2.paragraphs[0]
            p2.text = subtitle
            p2.font.name = FONT_BODY
            p2.font.size = Pt(10.5)
            p2.font.color.rgb = RGBColor(0x9A, 0xAB, 0xB9) if dark else MUTED

    def add_footer(slide, n, sources=(), dark=False):
        c = RGBColor(0x81, 0x92, 0xA6) if dark else RGBColor(0x7A, 0x89, 0x98)
        # Separator line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(6.85), Inches(12.03), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = DARK_CARD_BORDER if dark else GRID
        line.line.fill.background()

        # Left label
        tb = slide.shapes.add_textbox(Inches(0.65), Inches(6.92), Inches(4.0), Inches(0.3))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = "TMS  /  NYC FLIGHTS 2023"
        p.font.name = FONT_HEADING
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = c

        # Source tags
        if sources:
            tb2 = slide.shapes.add_textbox(Inches(4.66), Inches(6.92), Inches(4.0), Inches(0.3))
            tf2 = tb2.text_frame
            p2 = tf2.paragraphs[0]
            p2.alignment = PP_ALIGN.CENTER
            p2.text = "SOURCE  " + "  ".join(f"[{s}]" for s in sources)
            p2.font.name = FONT_HEADING
            p2.font.size = Pt(8.5)
            p2.font.bold = True
            p2.font.color.rgb = c

        # Slide Number
        tb3 = slide.shapes.add_textbox(Inches(10.68), Inches(6.92), Inches(2.0), Inches(0.3))
        tf3 = tb3.text_frame
        p3 = tf3.paragraphs[0]
        p3.alignment = PP_ALIGN.RIGHT
        p3.text = f"{n:02d} / 12"
        p3.font.name = FONT_HEADING
        p3.font.size = Pt(8.5)
        p3.font.bold = True
        p3.font.color.rgb = c

        # Add speaker notes
        if n in notes:
            slide.notes_slide.notes_text_frame.text = notes[n]

    # -------------------------------------------------------------
    # SLIDE 1: Title
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, dark=True)

    # Top pill
    pill1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.72), Inches(0.72), Inches(1.8), Inches(0.32))
    pill1.fill.solid()
    pill1.fill.fore_color.rgb = TEAL
    pill1.line.fill.background()
    p = pill1.text_frame.paragraphs[0]
    p.text = "TMS  /  DATA & ML"
    p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = NAVY; p.alignment = PP_ALIGN.CENTER

    # Main Headline
    tb = s1.shapes.add_textbox(Inches(0.72), Inches(1.35), Inches(10.0), Inches(1.6))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Know before your\nclients do."
    p.font.name = FONT_HEADING; p.font.size = Pt(40); p.font.bold = True; p.font.color.rgb = WHITE

    # Subtitle
    tb_sub = s1.shapes.add_textbox(Inches(0.75), Inches(3.1), Inches(11.0), Inches(0.8))
    tf_sub = tb_sub.text_frame
    p = tf_sub.paragraphs[0]
    p.text = "A flight early-warning system for a New York travel agency,\nbuilt on 435,352 departures from JFK, LGA and EWR. [01]"
    p.font.size = Pt(13); p.font.color.rgb = RGBColor(0xC2, 0xD0, 0xDE)

    # 3 Summary Cards
    cards_data = [
        ("2 hours", "notice before scheduled departure", ORANGE, "05"),
        ("2 alerts", "late-or-cancelled  /  cancellation", TEAL, "06"),
        ("1 year", "real flight history · 2023", ACCENT_BLUE, "01"),
    ]
    for i, (big, small, accent, src) in enumerate(cards_data):
        x = Inches(0.75 + i * 2.5)
        cbox = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(4.15), Inches(2.3), Inches(1.05))
        cbox.fill.solid(); cbox.fill.fore_color.rgb = NAVY2
        cbox.line.color.rgb = DARK_CARD_BORDER
        tf = cbox.text_frame; tf.margin_left = Inches(0.2); tf.margin_top = Inches(0.15)
        p1 = tf.paragraphs[0]; p1.text = big; p1.font.size = Pt(18); p1.font.bold = True; p1.font.color.rgb = accent
        p2 = tf.add_paragraph(); p2.text = small; p2.font.size = Pt(8.5); p2.font.color.rgb = RGBColor(0xC2, 0xD0, 0xDE)

    # Proposal Box
    pbox = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(5.45), Inches(11.8), Inches(1.0))
    pbox.fill.solid(); pbox.fill.fore_color.rgb = NAVY2
    pbox.line.color.rgb = DARK_CARD_BORDER
    tf = pbox.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.18)
    p1 = tf.paragraphs[0]; p1.text = "THE PROPOSAL"; p1.font.size = Pt(8.5); p1.font.bold = True; p1.font.color.rgb = TEAL
    p2 = tf.add_paragraph(); p2.text = "Pilot two human-reviewed alerts, then decide with evidence—not assumptions."; p2.font.size = Pt(13); p2.font.bold = True; p2.font.color.rgb = WHITE
    add_footer(s1, 1, ["01", "05", "06", "07"], dark=True)

    # -------------------------------------------------------------
    # SLIDE 2: Business Case
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, dark=False)
    add_header(s2, "THE BUSINESS CASE", "A bad flight is a client problem first",
               "Give the agency time to warn, check connections and prepare alternatives.", dark=False)

    mcards = [
        ("25.7%", "TRAINING-PERIOD RISK", "Flights late or cancelled, Jan–Sep; 330,883 scheduled departures.", "01", TEAL),
        ("10,738", "CANCELLATIONS", "Every cancellation forces a high-stakes client rebooking decision.", "01", ORANGE),
        ("3 airports", "NEW YORK HUBS", "JFK · LaGuardia (LGA) · Newark (EWR) across 118 destination markets.", "01", ACCENT_BLUE),
    ]
    for i, (big, title, body, src, col) in enumerate(mcards):
        x = Inches(0.65 + i * 4.1)
        bx = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(3.85), Inches(2.3))
        bx.fill.solid(); bx.fill.fore_color.rgb = WHITE; bx.line.color.rgb = GRID
        # Accent left strip
        st = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.0), Inches(0.1), Inches(2.3))
        st.fill.solid(); st.fill.fore_color.rgb = col; st.line.fill.background()
        tf = bx.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.25)
        p1 = tf.paragraphs[0]; p1.text = big; p1.font.size = Pt(28); p1.font.bold = True; p1.font.color.rgb = INK
        p2 = tf.add_paragraph(); p2.text = title; p2.font.size = Pt(9.5); p2.font.bold = True; p2.font.color.rgb = MUTED
        p3 = tf.add_paragraph(); p3.text = body; p3.font.size = Pt(9.5); p3.font.color.rgb = INK

    # Bottom Callout Box
    cbox = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(4.6), Inches(12.0), Inches(1.9))
    cbox.fill.solid(); cbox.fill.fore_color.rgb = NAVY; cbox.line.fill.background()
    tf = cbox.text_frame; tf.margin_left = Inches(0.4); tf.margin_top = Inches(0.25)
    p1 = tf.paragraphs[0]; p1.text = "THE TWO CORE OPERATIONAL QUESTIONS"; p1.font.size = Pt(8.5); p1.font.bold = True; p1.font.color.rgb = TEAL
    p2 = tf.add_paragraph(); p2.text = "1. Will this flight leave >15 min late or be cancelled? (Alert 1: Warning message)"; p2.font.size = Pt(13); p2.font.bold = True; p2.font.color.rgb = WHITE
    p3 = tf.add_paragraph(); p3.text = "2. Will this flight be cancelled? (Alert 2: Prepare rebooking queue)"; p3.font.size = Pt(13); p3.font.bold = True; p3.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)
    p4 = tf.add_paragraph(); p4.text = "Both scores calculated strictly at T = -2 hours before departure. A human always verifies live airline feeds first."; p4.font.size = Pt(10); p4.font.color.rgb = TEAL
    add_footer(s2, 2, ["01", "05"], dark=False)

    # -------------------------------------------------------------
    # SLIDE 3: What the Data Revealed (Task 2)
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, dark=True)
    add_header(s3, "WHAT THE DATA REVEALED", "Risk builds, clusters—and is not just weather",
               "Three findings with direct business impact. Training-period analysis unless stated. [02, 06]", dark=True)

    # Left Box: Delay Accumulation
    b1 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(2.0), Inches(4.2), Inches(4.5))
    b1.fill.solid(); b1.fill.fore_color.rgb = NAVY2; b1.line.color.rgb = DARK_CARD_BORDER
    tf = b1.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]; p.text = "THE DAY GETS HARDER"; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "13.4% [02]"; p.font.size = Pt(24); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "scheduled 05–08h wave"; p.font.size = Pt(9.5); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)
    p = tf.add_paragraph(); p.text = "\n39.9% [02]"; p.font.size = Pt(24); p.font.bold = True; p.font.color.rgb = ORANGE
    p = tf.add_paragraph(); p.text = "scheduled 19–22h evening wave"; p.font.size = Pt(9.5); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)
    p = tf.add_paragraph(); p.text = "\n+26.5 percentage points increase."; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = ORANGE
    p = tf.add_paragraph(); p.text = "Tested: Delay accumulates along tail turns (p < 0.001, Cramér's V = 0.18)."; p.font.size = Pt(8.5); p.font.color.rgb = RGBColor(0x9A, 0xAB, 0xB9)

    # Right Top Box: Daily Burst
    b2 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.1), Inches(2.0), Inches(7.55), Inches(2.1))
    b2.fill.solid(); b2.fill.fore_color.rgb = NAVY2; b2.line.color.rgb = DARK_CARD_BORDER
    tf = b2.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "CANCELLATIONS CLUSTER ON A FEW DAYS"; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = ORANGE
    p = tf.add_paragraph(); p.text = "27 / 273 days [02] accounted for 57.5% of all cancellations."; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "Peaks heavily in summer convective storms (June 6.1%, July 8.7% vs 0.2% in autumn test). Rebooking capacity must be managed in bursts."; p.font.size = Pt(9.5); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)

    # Right Bottom Box: Airport State vs Weather
    b3 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.1), Inches(4.4), Inches(7.55), Inches(2.1))
    b3.fill.solid(); b3.fill.fore_color.rgb = NAVY2; b3.line.color.rgb = DARK_CARD_BORDER
    tf = b3.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "THE BEST WARNING IS WHAT JUST HAPPENED AT THE AIRPORT"; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "Importance: 0.228 (Airport State at T) vs 0.023 (Local Weather)"; p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "Airport delay conditions in the 2 hours before T carry ~10× more predictive weight than weather. Severe network delays propagate regardless of local rain."; p.font.size = Pt(9.5); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)
    add_footer(s3, 3, ["02", "06"], dark=True)

    # -------------------------------------------------------------
    # SLIDE 4: Destination Groups (Clustering - Task 3)
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, dark=False)
    add_header(s4, "TARGET THE RESPONSE", "Destinations have different reliability profiles",
               "Three clustered groups plus a small-airport label; use groups as practical guidance. [03]", dark=False)

    groups_data = [
        ("SHORT-HAUL", "57 airports · 101,287 flights", "21.2% late", "4.3% cancel rate", "Prepare fast rebooking options; high cancellation frequency.", TEAL),
        ("MAIN LONG-HAUL", "45 airports · 226,896 flights", "27.8% late", "1.7% cancel rate", "Prioritize afternoon and evening connection monitoring.", ACCENT_BLUE),
        ("CHRONIC DELAYS", "7 airports · 2,374 flights", "53.1% late", "1.5% cancel rate", "Warn clients very early; audit onward connecting tickets.", CORAL),
    ]
    for i, (name, size, late_r, cancel_r, action, col) in enumerate(groups_data):
        x = Inches(0.65 + i * 4.1)
        bx = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(3.85), Inches(3.9))
        bx.fill.solid(); bx.fill.fore_color.rgb = WHITE; bx.line.color.rgb = GRID
        # Header label inside card
        lbl = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(2.2), Inches(1.8), Inches(0.3))
        lbl.fill.solid(); lbl.fill.fore_color.rgb = col; lbl.line.fill.background()
        p = lbl.text_frame.paragraphs[0]; p.text = name; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = NAVY if col in (TEAL, ORANGE) else WHITE; p.alignment = PP_ALIGN.CENTER

        tf = bx.text_frame; tf.margin_left = Inches(0.25); tf.margin_top = Inches(0.7)
        p = tf.paragraphs[0]; p.text = size; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = MUTED
        p = tf.add_paragraph(); p.text = f"{late_r}  |  {cancel_r}"; p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = INK
        p = tf.add_paragraph(); p.text = f"\nAction:\n{action}"; p.font.size = Pt(9.5); p.font.color.rgb = INK

    # Caution Banner
    c_banner = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(6.1), Inches(12.0), Inches(0.6))
    c_banner.fill.solid(); c_banner.fill.fore_color.rgb = PALE_ORANGE; c_banner.line.color.rgb = ORANGE
    tf = c_banner.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.12)
    p = tf.paragraphs[0]; p.text = "CAUTION: Clustering structure is modest (silhouette score 0.322). Use groups to tailor client tone, not as hard rules. [03]"
    p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = RGBColor(0x8B, 0x45, 0x00)
    add_footer(s4, 4, ["03"], dark=False)

    # -------------------------------------------------------------
    # SLIDE 5: Metrics (Task 4)
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, dark=False)
    add_header(s5, "MEASURE WHAT MATTERS", "The year changes the operating picture",
               "Use a small set of explicit, denominator-aware reliability measures. [01, 04]", dark=False)

    # Left: Seasonal Drift
    b_left = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(2.0), Inches(5.8), Inches(4.5))
    b_left.fill.solid(); b_left.fill.fore_color.rgb = WHITE; b_left.line.color.rgb = GRID
    tf = b_left.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]; p.text = "LATE OR CANCELLED (DRIFT)"; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = MUTED
    p = tf.add_paragraph(); p.text = "\nJan–Sep Training: 25.7%"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "Summer peak reached 39.1% late in July (M3 cancellations: 8.68%)."; p.font.size = Pt(9); p.font.color.rgb = MUTED
    p = tf.add_paragraph(); p.text = "\nOct–Dec Test Part: 14.1%"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = ORANGE
    p = tf.add_paragraph(); p.text = "Calmer autumn; cancellations dropped to 0.21% (224 events)."; p.font.size = Pt(9); p.font.color.rgb = MUTED
    p = tf.add_paragraph(); p.text = "\nKey Takeaway: Models must be compared against period prevalence—never a fixed annual benchmark."; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = INK

    # Right: 5 Metrics Table
    b_right = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.7), Inches(2.0), Inches(5.95), Inches(4.5))
    b_right.fill.solid(); b_right.fill.fore_color.rgb = NAVY; b_right.line.fill.background()
    tf = b_right.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]; p.text = "THE 5 CORE METRICS (FULL YEAR REPRODUCED)"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = TEAL

    metrics_list = [
        ("M1", "On-Time Rate", "79.03%", "dep_delay <= 15 / departed"),
        ("M2", "Average Delay", "13.84 min", "mean dep_delay / departed"),
        ("M3", "Cancellation Rate", "2.47%", "missing dep_time / all scheduled"),
        ("M4", "Severe Delay (>60m)", "8.41%", "dep_delay > 60 / departed"),
        ("M5", "Late or Cancelled", "22.91%", "Prediction 1 target / all scheduled"),
    ]
    for m, name, val, den in metrics_list:
        p = tf.add_paragraph()
        p.text = f"{m}: {name} → {val}  ({den})"
        p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = WHITE
    add_footer(s5, 5, ["01", "04"], dark=False)

    # -------------------------------------------------------------
    # SLIDE 6: Feature Engineering & Leakage (Task 5)
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, dark=True)
    add_header(s6, "BUILT TO BE TRUSTED", "Score only with information available at decision time",
               "Prediction point is strictly two hours before scheduled departure (T = -2h). [05]", dark=True)

    feat_cols = [
        ("SCHEDULE & ROUTE", "Calendar, hour, day of week, carrier, origin, destination, destination cluster group, scheduled airport traffic volume.", TEAL),
        ("AIRPORT STATE AT T", "Actual departures from same origin in (T-2h, T]: recent delay mean, median, late share. Zero cancellation flags.", ORANGE),
        ("WEATHER & AIRCRAFT", "Strict weather known by T. Scheduled-hour weather tested as forecast proxy. Aircraft features filled via carrier medians (D10).", ACCENT_BLUE),
    ]
    for i, (title, body, col) in enumerate(feat_cols):
        x = Inches(0.65 + i * 4.1)
        bx = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.1), Inches(3.85), Inches(3.6))
        bx.fill.solid(); bx.fill.fore_color.rgb = NAVY2; bx.line.color.rgb = DARK_CARD_BORDER
        tf = bx.text_frame; tf.margin_left = Inches(0.25); tf.margin_top = Inches(0.25)
        p = tf.paragraphs[0]; p.text = title; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = col
        p = tf.add_paragraph(); p.text = f"\n{body}"; p.font.size = Pt(9.5); p.font.color.rgb = RGBColor(0xD5, 0xDF, 0xE8)

    # Leakage Guardrail Bottom
    lk_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(5.95), Inches(12.0), Inches(0.75))
    lk_box.fill.solid(); lk_box.fill.fore_color.rgb = RGBColor(0x20, 0x3A, 0x56); lk_box.line.fill.background()
    tf = lk_box.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]; p.text = "LEAKAGE GUARDRAILS & 4 AUTOMATED TESTS:"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "Post-takeoff fields (dep_delay, air_time) forbidden. Missing tail numbers never used as cancellation signals. Passed 4 automated leak tests. [05]"; p.font.size = Pt(9); p.font.color.rgb = WHITE
    add_footer(s6, 6, ["05"], dark=True)

    # -------------------------------------------------------------
    # SLIDE 7: Honest Split & Methodology (Task 6)
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, dark=False)
    add_header(s7, "AN HONEST TEST", "Tune on validation; keep the test months unseen",
               "Time order strictly mirrors real-world deployment. [06]", dark=False)

    split_blocks = [
        ("JAN–JUN (Months 1–6)", "Sub-train Fit\n222,402 flights\nTrain initial candidate models", TEAL),
        ("JUL–SEP (Months 7–9)", "Validation Tuning\n108,481 flights\nTune hyperparameters & cut-offs", ORANGE),
        ("OCT–DEC (Months 10–12)", "Final Hold-out Test\n104,469 flights\nScored strictly once at end", ACCENT_BLUE),
    ]
    for i, (title, body, col) in enumerate(split_blocks):
        x = Inches(0.65 + i * 4.1)
        bx = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(3.85), Inches(2.2))
        bx.fill.solid(); bx.fill.fore_color.rgb = WHITE; bx.line.color.rgb = GRID
        # left accent line
        st = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.0), Inches(0.1), Inches(2.2))
        st.fill.solid(); st.fill.fore_color.rgb = col; st.line.fill.background()
        tf = bx.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.2)
        p = tf.paragraphs[0]; p.text = title; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = INK
        p = tf.add_paragraph(); p.text = body; p.font.size = Pt(9.5); p.font.color.rgb = MUTED

    # Bottom Explanation Box: Why not accuracy?
    acc_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(4.5), Inches(12.0), Inches(2.0))
    acc_box.fill.solid(); acc_box.fill.fore_color.rgb = PALE_BLUE; acc_box.line.color.rgb = GRID
    tf = acc_box.text_frame; tf.margin_left = Inches(0.35); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "WHY ACCURACY IS NEVER A HEADLINE METRIC (TASK 6 & DECISION D8)"; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = RGBColor(0x31, 0x50, 0x6E)
    p = tf.add_paragraph(); p.text = "• \"Nobody is late\" achieves 85.9% accuracy on the test set, but catches exactly ZERO delayed flights."; p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = INK
    p = tf.add_paragraph(); p.text = "• \"Nobody is cancelled\" achieves 99.79% accuracy, completely useless for client rebooking."; p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = INK
    p = tf.add_paragraph(); p.text = "• We evaluate models using PR-AUC (Precision-Recall Area Under Curve), where the dumb baseline equals period prevalence. [06]"; p.font.size = Pt(9.5); p.font.color.rgb = MUTED
    add_footer(s7, 7, ["06"], dark=False)

    # -------------------------------------------------------------
    # SLIDE 8: Model Results Table (Task 6)
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, dark=True)
    add_header(s8, "THE RESULT", "Both alerts rank risk above the dumb baseline",
               "PR-AUC on held-out Oct–Dec flights; intervals reflect day-level resampling. [06]", dark=True)

    # Table Box
    t_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(2.0), Inches(12.0), Inches(3.2))
    t_box.fill.solid(); t_box.fill.fore_color.rgb = NAVY2; t_box.line.color.rgb = DARK_CARD_BORDER
    tf = t_box.text_frame; tf.margin_left = Inches(0.4); tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = f"{'PREDICTION':<22}{'DUMB BASELINE':<18}{'MODEL PR-AUC':<18}{'95% INTERVAL':<20}{'OUTCOME':<15}"
    p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = RGBColor(0x9A, 0xAB, 0xB9)

    rows = [
        ("Late or Cancelled", "0.141", "0.339 (Neural Net)", "0.301–0.376", "2.4× Lift (p < 0.001)"),
        ("Cancelled Only", "0.0021", "0.120 (Logistic Reg)", "0.002–0.233", "57× Lift (Prioritize)"),
    ]
    for pred, dumb, model, ci, out in rows:
        p = tf.add_paragraph()
        p.text = f"\n{pred:<22}{dumb:<18}{model:<18}{ci:<20}{out:<15}"
        p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = WHITE

    # Footnote Box
    f_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(5.4), Inches(12.0), Inches(1.2))
    f_box.fill.solid(); f_box.fill.fore_color.rgb = NAVY2; f_box.line.color.rgb = DARK_CARD_BORDER
    tf = f_box.text_frame; tf.margin_left = Inches(0.35); tf.margin_top = Inches(0.18)
    p = tf.paragraphs[0]; p.text = "INTERPRETATION & VERIFICATION:"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "• Both models beat their dumb prevalence baselines with high statistical significance (paired bootstrap p < 0.001).\n• Cancellation interval is wide because only 224 cancellations occurred in test; model serves as an effective queue prioritization tool. [06]"; p.font.size = Pt(9); p.font.color.rgb = RGBColor(0xD5, 0xDF, 0xE8)
    add_footer(s8, 8, ["01", "06"], dark=True)

    # -------------------------------------------------------------
    # SLIDE 9: Decision Card 1 (Delay Alert - Task 7)
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, dark=False)
    add_header(s9, "DECISION CARD  /  ALERT 1", "Warn clients about a possible delay",
               "Late-or-cancelled score · test quarter · human review before messaging. [07]", dark=False)

    stats1 = [
        (".597", "Validation Cutoff", TEAL),
        ("11.5%", "Test Flights Flagged", ACCENT_BLUE),
        ("37.4%", "Flag Precision", ORANGE),
        ("30.5%", "Problem Flights Caught", CORAL),
    ]
    for i, (val, label_t, col) in enumerate(stats1):
        x = Inches(0.65 + i * 3.08)
        bx = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(2.85), Inches(1.5))
        bx.fill.solid(); bx.fill.fore_color.rgb = WHITE; bx.line.color.rgb = GRID
        st = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.0), Inches(0.08), Inches(1.5))
        st.fill.solid(); st.fill.fore_color.rgb = col; st.line.fill.background()
        tf = bx.text_frame; tf.margin_left = Inches(0.2); tf.margin_top = Inches(0.2)
        p = tf.paragraphs[0]; p.text = val; p.font.size = Pt(24); p.font.bold = True; p.font.color.rgb = INK
        p = tf.add_paragraph(); p.text = label_t; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = MUTED

    # Bottom Detail Boxes
    b_val = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(3.75), Inches(7.4), Inches(2.8))
    b_val.fill.solid(); b_val.fill.fore_color.rgb = NAVY; b_val.line.fill.background()
    tf = b_val.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "WHAT THE TEST QUARTER LOOKED LIKE (11,974 FLAGS)"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "• Caught 4,481 true positive delay/cancel events (~130 flagged flights/day)."; p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "• Lift: 2.7× over a random shortlist of the same volume.\n• Capacity View: Top 20% budget flags 227/day with 31.2% precision and 44.3% recall.\n• Blind Spot: Early mornings (5.8% recall vs 51% evening) because delays haven't compounded yet. [07]"; p.font.size = Pt(9); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)

    b_act = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(3.75), Inches(4.35), Inches(2.8))
    b_act.fill.solid(); b_act.fill.fore_color.rgb = PALE_ORANGE; b_act.line.color.rgb = ORANGE
    tf = b_act.text_frame; tf.margin_left = Inches(0.25); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "ACTION + HUMAN CHECK"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = RGBColor(0x8B, 0x45, 0x00)
    p = tf.add_paragraph(); p.text = "1. Verify Airline Status:\nCheck airline live feed before sending SMS."; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = INK
    p = tf.add_paragraph(); p.text = "\n2. Group Differentiation:\nWarn earlier on G2 long-haul evening flights; prepare rebooking for G1 short-haul. [03, 07]"; p.font.size = Pt(9); p.font.color.rgb = INK
    add_footer(s9, 9, ["07"], dark=False)

    # -------------------------------------------------------------
    # SLIDE 10: Decision Card 2 (Cancellation Alert - Task 7)
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, dark=True)
    add_header(s10, "DECISION CARD  /  ALERT 2", "Prepare rebooking for cancellation risk",
               "A prioritization queue, not a promise that a flight will be cancelled. [07]", dark=True)

    stats2 = [
        (".137", "Validation Cutoff", TEAL),
        ("484", "Test Flags", ACCENT_BLUE),
        ("19.4%", "Flag Precision", ORANGE),
        ("42.0%", "Cancellations Caught", CORAL),
    ]
    for i, (val, label_t, col) in enumerate(stats2):
        x = Inches(0.65 + i * 3.08)
        bx = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(2.85), Inches(1.5))
        bx.fill.solid(); bx.fill.fore_color.rgb = NAVY2; bx.line.color.rgb = DARK_CARD_BORDER
        st = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.0), Inches(0.08), Inches(1.5))
        st.fill.solid(); st.fill.fore_color.rgb = col; st.line.fill.background()
        tf = bx.text_frame; tf.margin_left = Inches(0.2); tf.margin_top = Inches(0.2)
        p = tf.paragraphs[0]; p.text = val; p.font.size = Pt(24); p.font.bold = True; p.font.color.rgb = WHITE
        p = tf.add_paragraph(); p.text = label_t; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = RGBColor(0xC2, 0xD0, 0xDE)

    # Left Box
    b_val2 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(3.75), Inches(6.0), Inches(2.8))
    b_val2.fill.solid(); b_val2.fill.fore_color.rgb = NAVY2; b_val2.line.color.rgb = DARK_CARD_BORDER
    tf = b_val2.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "QUEUE PERFORMANCE (94 / 224 CAUGHT)"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "• Identifies 94 cancellations (~5.3 flags/day) with 91× lift over random."; p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "• Capacity View: Top 1% budget flags 11/day (10.2% precision, 47.8% recall).\n• Never Auto-Rebook: Staff verify alternative seat availability and prepare rebooking options before seats sell out. [07]"; p.font.size = Pt(9); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)

    # Right Box
    b_care = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.95), Inches(3.75), Inches(5.7), Inches(2.8))
    b_care.fill.solid(); b_care.fill.fore_color.rgb = RGBColor(0x2A, 0x1E, 0x22); b_care.line.color.rgb = CORAL
    tf = b_care.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "CONCENTRATION & KNOWN WEAK SPOTS"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = ORANGE
    p = tf.add_paragraph(); p.text = "• 115 cancellations fell on Dec 18 (121 in ISO Week 51).\n• Normal weather on that day (rain 12% vs 11% median); cause unrecorded in data.\n• Newark Blind Spot: 0% recall at EWR (vs 45% JFK, 54% LGA). Staff must apply manual vigilance to Newark flights. [06, 07]"; p.font.size = Pt(9); p.font.color.rgb = RGBColor(0xE4, 0xD6, 0xD1)
    add_footer(s10, 10, ["01", "07"], dark=True)

    # -------------------------------------------------------------
    # SLIDE 11: Limits & Monitoring (Task 7 & 8)
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11, dark=False)
    add_header(s11, "LIMITS & MONITORING", "Keep a person in the loop—and watch drift",
               "The test quarter is an honest audit, not a permanent guarantee. [01, 06, 07]", dark=False)

    limits_data = [
        ("SEASONAL DRIFT", "Late-or-cancelled risk fell from 25.7% in train to 14.1% in test; cancellation dropped from 3.18% to 0.21%. [01]", ORANGE),
        ("EARLY-MORNING GAP", "Alert 1 caught only 5.8% of morning delays; Alert 2 caught 0% of Newark cancellations. [06, 07]", CORAL),
        ("EXTREME CLUSTERS", "115 / 224 test cancellations landed on 18 December; root cause is unexplained by local weather. [01, 07]", ACCENT_BLUE),
    ]
    for i, (title, body, col) in enumerate(limits_data):
        y = Inches(2.0 + i * 1.35)
        bx = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), y, Inches(7.2), Inches(1.15))
        bx.fill.solid(); bx.fill.fore_color.rgb = WHITE; bx.line.color.rgb = GRID
        st = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), y, Inches(0.1), Inches(1.15))
        st.fill.solid(); st.fill.fore_color.rgb = col; st.line.fill.background()
        tf = bx.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]; p.text = title; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = MUTED
        p = tf.add_paragraph(); p.text = body; p.font.size = Pt(9.5); p.font.color.rgb = INK

    # Right Monitoring Box
    mon_box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.15), Inches(2.0), Inches(4.5), Inches(4.6))
    mon_box.fill.solid(); mon_box.fill.fore_color.rgb = NAVY; mon_box.line.fill.background()
    tf = mon_box.text_frame; tf.margin_left = Inches(0.35); tf.margin_top = Inches(0.3)
    p = tf.paragraphs[0]; p.text = "CONCRETE RE-CHECK RULES (LINE 9)"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "\nAlert 1 Trigger:"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "Audit / retrain if weekly recall falls below 14% for two consecutive weeks. [07]"; p.font.size = Pt(9.5); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)
    p = tf.add_paragraph(); p.text = "\nAlert 2 Trigger:"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "Audit 4-week blocks with >=30 cancellations if pooled recall falls below 23%. [07]"; p.font.size = Pt(9.5); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)
    p = tf.add_paragraph(); p.text = "\nHuman In The Loop:\nWeekly review by designated flight lead ensures drift is caught early."; p.font.size = Pt(9); p.font.color.rgb = TEAL
    add_footer(s11, 11, ["01", "06", "07"], dark=False)

    # -------------------------------------------------------------
    # SLIDE 12: AI Governance & Decision (Task 8 & Golden Rule #6)
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12, dark=True)
    add_header(s12, "GOVERNANCE & DECISION", "Responsible AI, verified methods—and a careful pilot",
               "Golden Rule #6 compliance, independent audits, and operational next steps. [01–07, README]", dark=True)

    # Left Column: AI Assistance & Self-Verification
    ai_box1 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(2.0), Inches(5.8), Inches(1.3))
    ai_box1.fill.solid(); ai_box1.fill.fore_color.rgb = NAVY2; ai_box1.line.color.rgb = DARK_CARD_BORDER
    tf = ai_box1.text_frame; tf.margin_left = Inches(0.25); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]; p.text = "AI ASSISTANCE (WHERE AI HELPED)"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "Drafted baseline notebook code, helper utilities (utils.py), and slide layouts; assisted in memory profiling during Task 6 modeling. [README]"; p.font.size = Pt(8.5); p.font.color.rgb = RGBColor(0xD5, 0xDF, 0xE8)

    ai_box2 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(3.45), Inches(5.8), Inches(1.85))
    ai_box2.fill.solid(); ai_box2.fill.fore_color.rgb = NAVY2; ai_box2.line.color.rgb = DARK_CARD_BORDER
    tf = ai_box2.text_frame; tf.margin_left = Inches(0.25); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]; p.text = "WHAT I INDEPENDENTLY CHECKED (VERIFIED)"; p.font.size = Pt(8.5); p.font.bold = True; p.font.color.rgb = ORANGE
    p = tf.add_paragraph(); p.text = "• Recomputed all 435,352 flight counts and 15 metric assertions in code.\n• Audited 4 automated leak tests (verified zero future data at T-2h).\n• Executed notebooks 01–07 top-to-bottom with seed 42 (100% reproducible).\n• Reconciled every slide figure with the project notebook ledger."; p.font.size = Pt(8); p.font.color.rgb = RGBColor(0xD5, 0xDF, 0xE8)

    ai_box3 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(5.45), Inches(5.8), Inches(1.2))
    ai_box3.fill.solid(); ai_box3.fill.fore_color.rgb = RGBColor(0x18, 0x23, 0x38); ai_box3.line.color.rgb = DARK_CARD_BORDER
    tf = ai_box3.text_frame; tf.margin_left = Inches(0.25); tf.margin_top = Inches(0.12)
    p = tf.paragraphs[0]; p.text = "DATA LIMITATIONS ACKNOWLEDGED"; p.font.size = Pt(8); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph(); p.text = "Single-year data (2023) limits annual seasonality assessment. Strong autumn drift (late 25.7% → 14.1%; cancels 3.18% → 0.21%). Weather is observed, not forecast."; p.font.size = Pt(8); p.font.color.rgb = RGBColor(0xC2, 0xD0, 0xDE)

    # Right Column: The Decision & Ask
    d_box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.75), Inches(2.0), Inches(5.9), Inches(2.8))
    d_box.fill.solid(); d_box.fill.fore_color.rgb = NAVY2; d_box.line.color.rgb = DARK_CARD_BORDER
    tf = d_box.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]; p.text = "THE DECISION"; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = TEAL
    p = tf.add_paragraph(); p.text = "Approve a careful pilot. Earn the right to scale."; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "\n01 REVIEW: A named person verifies live airline status before contact.\n02 MONITOR: Weekly drift review; trigger stop rule if recall falls.\n03 IMPROVE: Integrate live weather forecasts & cancellation timestamps."; p.font.size = Pt(9); p.font.color.rgb = RGBColor(0xCF, 0xD9, 0xE3)

    ask_box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.75), Inches(4.95), Inches(5.9), Inches(1.7))
    ask_box.fill.solid(); ask_box.fill.fore_color.rgb = NAVY2; ask_box.line.color.rgb = TEAL
    tf = ask_box.text_frame; tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.18)
    p = tf.paragraphs[0]; p.text = "THE ASK"; p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = ORANGE
    p = tf.add_paragraph(); p.text = "Agree the daily alert capacity & assign review owner"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = WHITE
    p = tf.add_paragraph(); p.text = "Capacity target: ~130 delay alerts/day and ~5 cancellation preparations/day. Human ownership is mandatory before launching pilot."; p.font.size = Pt(8.5); p.font.color.rgb = RGBColor(0xC2, 0xD0, 0xDE)
    add_footer(s12, 12, ["01", "02", "03", "04", "05", "06", "07"], dark=True)

    prs.save(str(OUT))
    print(f"Successfully generated 12 widescreen PPTX slides at: {OUT}")


if __name__ == "__main__":
    create_deck()

