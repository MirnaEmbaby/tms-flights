from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "TMS_flights_presentation_hybrid.pdf"
W, H = 13.333, 7.5

NAVY = "#0B1930"
NAVY2 = "#142943"
INK = "#172A43"
MUTED = "#61738A"
PAPER = "#F5F3EE"
WHITE = "#FFFFFF"
TEAL = "#29C6B3"
ORANGE = "#FFB547"
CORAL = "#F07867"
PALE_TEAL = "#DDF5EF"
PALE_ORANGE = "#FFF0D7"
PALE_BLUE = "#E6EDF5"
GRID = "#D8E0E7"
FONT = "DejaVu Sans"


def new_slide(dark: bool = False):
    fig = plt.figure(figsize=(W, H), facecolor=NAVY if dark else PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.set_facecolor(NAVY if dark else PAPER)
    return fig, ax


def text(ax, x, y, value, size=12, color=INK, weight="normal", ha="left",
         va="top", alpha=1, linespacing=1.3, z=5):
    ax.text(x, y, value, fontsize=size, color=color, fontfamily=FONT,
            fontweight=weight, ha=ha, va=va, alpha=alpha,
            linespacing=linespacing, zorder=z)


def wrap(value: str, width: int) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False))


def box(ax, x, y, w, h, color=WHITE, radius=0.16, edge=None, lw=0.8, z=1):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.02,rounding_size={radius}",
                       linewidth=lw if edge else 0,
                       edgecolor=edge or color, facecolor=color, zorder=z)
    ax.add_patch(p)
    return p


def tag(ax, x, y, source, dark=False):
    bg = "#203A56" if dark else PALE_BLUE
    fg = "#C7D6E6" if dark else "#31506E"
    box(ax, x, y - 0.22, 0.48, 0.26, bg, radius=0.08, z=7)
    text(ax, x + 0.24, y - 0.09, f"[{source}]", 7.3, fg, "bold", ha="center",
         va="center", z=8)


def label(ax, x, y, value, color=TEAL, dark=False):
    fg = NAVY if color in (TEAL, ORANGE) else WHITE
    box(ax, x, y - 0.28, max(0.82, len(value) * 0.073 + 0.25), 0.32,
        color, radius=0.08, z=4)
    text(ax, x + 0.12, y - 0.12, value.upper(), 7.5, fg, "bold", va="center", z=5)


def footer(ax, n, sources=(), dark=False):
    c = "#8192A6" if dark else "#7A8998"
    text(ax, 0.48, 0.28, "TMS  /  NYC FLIGHTS 2023", 7.4, c, "bold", va="center")
    if sources:
        text(ax, 6.66, 0.28, "SOURCE  " + "  ".join(f"[{s}]" for s in sources),
             7.3, c, "bold", ha="center", va="center")
    text(ax, 12.84, 0.28, f"{n:02d} / 12", 7.4, c, "bold", ha="right", va="center")
    ax.plot([0.48, 12.85], [0.55, 0.55], color="#29415A" if dark else GRID, lw=0.7)


def header(ax, section, title, subtitle=None, dark=False):
    c = "#9AABB9" if dark else MUTED
    title_c = WHITE if dark else INK
    label(ax, 0.55, 7.08, section, TEAL, dark)
    text(ax, 0.55, 6.56, title, 25, title_c, "bold")
    if subtitle:
        text(ax, 0.57, 6.04, subtitle, 10.2, c)


def metric_card(ax, x, y, w, h, big, title, body, source, accent=TEAL, dark=False):
    box(ax, x, y, w, h, NAVY2 if dark else WHITE, radius=0.15,
        edge="#25405C" if dark else None, z=1)
    ax.add_patch(FancyBboxPatch((x, y), 0.075, h,
                                boxstyle="round,pad=0,rounding_size=0.035",
                                facecolor=accent, edgecolor=accent, zorder=2))
    text(ax, x + 0.23, y + h - 0.2, big, 25, WHITE if dark else INK, "bold")
    text(ax, x + 0.23, y + h - 0.68, title, 10, accent if dark else MUTED, "bold")
    text(ax, x + 0.23, y + h - 1.03, wrap(body, max(18, int(w * 7.1))),
         9, "#D5DFE8" if dark else INK, linespacing=1.35)
    tag(ax, x + w - 0.58, y + 0.35, source, dark)


def line(ax, x1, y1, x2, y2, color=GRID, lw=1, alpha=1, z=0):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, alpha=alpha,
            solid_capstyle="round", zorder=z)


def slide1(pdf):
    fig, ax = new_slide(True)
    # Abstract route arcs evoke a network without using decorative stock imagery.
    for i, c in enumerate([TEAL, ORANGE, CORAL, "#7398E8", "#A584E8"]):
        verts = [(7.2, 5.8 - i * .15), (8.5, 6.6 - i * .1),
                 (9.1 + i * .26, 4.6 - i * .22), (11.3 + i * .18, 5.0 - i * .34)]
        patch = PathPatch(MplPath(verts, [MplPath.MOVETO, MplPath.CURVE4,
                                         MplPath.CURVE4, MplPath.CURVE4]),
                          fill=False, lw=1.7, edgecolor=c, alpha=.72, zorder=1)
        ax.add_patch(patch)
        ax.add_patch(Circle(verts[-1], 0.045, color=c, zorder=2))
    label(ax, 0.7, 6.74, "TMS  /  DATA & ML", TEAL, True)
    text(ax, 0.7, 5.82, "Know before your\nclients do.", 36, WHITE, "bold", linespacing=1.12)
    text(ax, 0.72, 4.22,
         "A flight early-warning system for a New York travel agency,\n"
         "built on 435,352 departures from JFK, LGA and EWR. [01]",
         12, "#C2D0DE", linespacing=1.55)
    cards = [
        ("2 hours", "notice before scheduled departure", ORANGE, "05"),
        ("2 alerts", "late-or-cancelled  /  cancellation", TEAL, "06"),
        ("1 year", "real flight history · 2023", "#9CB6FF", "01"),
    ]
    for i, (big, small, accent, src) in enumerate(cards):
        x = .72 + i * 2.36
        box(ax, x, 2.43, 2.16, .92, "#142943", radius=.14, edge="#29415A")
        text(ax, x + .18, 3.13, big, 17, accent, "bold")
        text(ax, x + .18, 2.78, small, 7.6, "#C2D0DE")
        tag(ax, x + 1.57, 2.62, src, True)
    text(ax, .72, 1.45, "THE PROPOSAL", 8.5, TEAL, "bold")
    text(ax, .72, 1.08,
         "Pilot two human-reviewed alerts, then decide with evidence—not assumptions.",
         12, WHITE, "bold")
    footer(ax, 1, ["01", "05", "06", "07"], True)
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide2(pdf):
    fig, ax = new_slide(False)
    header(ax, "THE BUSINESS CASE", "A bad flight is a client problem first",
           "Give the agency time to warn, check connections and prepare alternatives.")
    metric_card(ax, .62, 3.7, 3.82, 1.85, "25.7%", "TRAINING-PERIOD RISK",
                "Flights late or cancelled, Jan–Sep; 330,883 scheduled flights.",
                "01", TEAL)
    metric_card(ax, 4.75, 3.7, 3.82, 1.85, "10,738", "CANCELLATIONS",
                "Every cancellation can force a rebooking decision.",
                "01", ORANGE)
    metric_card(ax, 8.88, 3.7, 3.82, 1.85, "3 airports", "NEW YORK DEPARTURES",
                "JFK · LaGuardia (LGA) · Newark (EWR).",
                "01", "#6689D6")
    box(ax, .62, 1.38, 12.08, 1.72, NAVY, radius=.17)
    text(ax, .93, 2.76, "THE TWO QUESTIONS", 8.2, TEAL, "bold")
    text(ax, .93, 2.36, "Will this flight be late or cancelled?", 15, WHITE, "bold")
    text(ax, .93, 1.99, "Should the agency prepare a rebooking?", 12, "#CFD9E3")
    line(ax, 6.45, 1.73, 6.45, 2.58, "#38516B", 1.1)
    text(ax, 6.82, 2.62, "Both scores are intended for the two-hour point. [05]",
         10, "#CFD9E3")
    text(ax, 6.82, 2.16, "A person verifies live airline status before acting.",
         10, "#CFD9E3")
    footer(ax, 2, ["01", "05"])
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide3(pdf):
    fig, ax = new_slide(True)
    header(ax, "WHAT THE DATA REVEALED", "Risk builds, clusters—and is not just weather",
           "Three findings with a business use. Training-period analysis unless stated. [02, 06]",
           True)
    # Hour-group contrast.
    box(ax, .62, 1.33, 4.03, 4.18, NAVY2, edge="#29415A")
    text(ax, .9, 5.18, "THE DAY GETS HARDER", 8, TEAL, "bold")
    text(ax, .9, 4.72, "13.4%  [02]", 22, WHITE, "bold")
    text(ax, .92, 4.34, "scheduled 05–08 h", 9, "#CFD9E3")
    ax.add_patch(FancyBboxPatch((.94, 3.67), 3.25 * .335, .18,
                                boxstyle="round,pad=0.02,rounding_size=.08",
                                facecolor=TEAL, edgecolor=TEAL))
    text(ax, .9, 3.35, "39.9%  [02]", 22, WHITE, "bold")
    text(ax, .92, 2.97, "scheduled 19–22 h", 9, "#CFD9E3")
    ax.add_patch(FancyBboxPatch((.94, 2.3), 3.25, .18,
                                boxstyle="round,pad=0.02,rounding_size=.08",
                                facecolor=ORANGE, edgecolor=ORANGE))
    text(ax, .9, 1.85, "+26.5 percentage points. [02]", 9.5, ORANGE, "bold")
    # Daily clustering.
    box(ax, 4.88, 3.62, 7.82, 1.89, "#142943", edge="#29415A")
    text(ax, 5.18, 5.18, "CANCELLATIONS CLUSTER ON A FEW DAYS", 8, ORANGE, "bold")
    text(ax, 5.18, 4.68, "27 / 273 days  [02]", 20, WHITE, "bold")
    text(ax, 8.17, 4.76, "accounted for 57.5% of cancellations. [02]",
         11, "#CFD9E3", va="center")
    # Airport state vs weather.
    box(ax, 4.88, 1.33, 7.82, 1.93, "#142943", edge="#29415A")
    text(ax, 5.18, 2.82, "THE BEST WARNING IS WHAT JUST HAPPENED AT THE AIRPORT",
         8, TEAL, "bold")
    text(ax, 5.18, 2.31, "0.228", 20, WHITE, "bold")
    text(ax, 6.55, 2.35, "recent airport-state importance", 9, "#CFD9E3", va="center")
    text(ax, 9.17, 2.31, "0.023", 20, ORANGE, "bold")
    text(ax, 10.49, 2.35, "weather", 9, "#CFD9E3", va="center")
    text(ax, 5.18, 1.74, "About 10× stronger in this validation importance comparison. [06]",
         8.8, "#CFD9E3")
    footer(ax, 3, ["02", "06"], True)
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide4(pdf):
    fig, ax = new_slide(False)
    header(ax, "TARGET THE RESPONSE", "Destinations have different reliability profiles",
           "Three clustered groups plus a small-airport label; use the groups as guidance, not certainty.")
    groups = [
        ("SHORT-HAUL", "57 airports", "101,287 flights", "21.2% late",
         "Prepare rebooking options; cancellation rate was 4.3%.", TEAL),
        ("MAIN LONG-HAUL", "45 airports", "226,896 flights", "27.8% late",
         "Prioritize afternoon and evening connection checks.", "#6689D6"),
        ("CHRONIC DELAYS", "7 airports", "2,374 flights", "53.1% late",
         "Warn early and check onward connections.", CORAL),
    ]
    for i, (name, airports, flights, rate, action, accent) in enumerate(groups):
        x = .62 + i * 4.1
        box(ax, x, 2.25, 3.82, 3.17, WHITE, edge=GRID)
        label(ax, x + .24, 5.1, name, accent)
        text(ax, x + .25, 4.54, airports, 10, MUTED, "bold")
        text(ax, x + .25, 4.13, flights, 9, MUTED)
        text(ax, x + .25, 3.52, rate, 21, INK, "bold")
        text(ax, x + .25, 2.94, wrap(action, 34), 9, INK)
        tag(ax, x + 3.14, 2.48, "03")
    box(ax, .62, 1.05, 12.08, .73, PALE_ORANGE, radius=.12)
    text(ax, .88, 1.54, "CAUTION", 8, "#A65B00", "bold")
    text(ax, 1.88, 1.54,
         "The structure is modest (silhouette 0.322). Avoid strong claims about small groups. [03]",
         9, INK)
    footer(ax, 4, ["03"])
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide5(pdf):
    fig, ax = new_slide(False)
    header(ax, "MEASURE WHAT MATTERS", "The year changes the operating picture",
           "Use a small set of explicit, denominator-aware reliability measures.")
    # Train/test cards with baseline bars.
    box(ax, .62, 1.35, 7.0, 4.2, WHITE, edge=GRID)
    text(ax, .94, 5.18, "LATE OR CANCELLED", 8, MUTED, "bold")
    for idx, (name, val, col, src) in enumerate([
        ("Jan–Sep train", 25.7, TEAL, "01"),
        ("Oct–Dec test", 14.1, ORANGE, "01"),
    ]):
        y = 4.45 - idx * 1.12
        text(ax, .96, y + .17, name, 9, INK, "bold")
        ax.add_patch(FancyBboxPatch((2.65, y - .12), 3.48 * val / 30, .34,
                                    boxstyle="round,pad=0.02,rounding_size=.08",
                                    facecolor=col, edgecolor=col))
        text(ax, 6.44, y + .17, f"{val:.1f}%", 12, INK, "bold", ha="right")
        tag(ax, 6.78, y - .02, src)
    text(ax, .96, 1.72,
         "Cancellation rate: 3.18% train → 0.21% test. [01]\n"
         "This drift is why test performance must be shown against its own prevalence.",
         9, MUTED, linespacing=1.5)
    box(ax, 7.92, 1.35, 4.78, 4.2, NAVY, radius=.16)
    text(ax, 8.24, 5.18, "THE FIVE METRICS", 8, TEAL, "bold")
    metric_rows = [
        ("M1", "on-time rate", "departed flights"),
        ("M2", "mean departure delay", "minutes · departed"),
        ("M3", "cancellation rate", "all scheduled flights"),
        ("M4", ">60 min late", "departed flights"),
        ("M5", "late or cancelled", "all scheduled flights"),
    ]
    for j, (m, title, den) in enumerate(metric_rows):
        y = 4.66 - j * .56
        text(ax, 8.25, y, m, 8, ORANGE, "bold")
        text(ax, 8.77, y, title, 9, WHITE, "bold")
        text(ax, 11.95, y, den, 7.1, "#B8C6D4", ha="right")
        line(ax, 8.25, y - .18, 12.35, y - .18, "#29415A", .6)
    text(ax, .66, .91, "Full-year checks: M1 79.03% · M2 13.84 min · M3 2.47% · M4 8.41% · M5 22.91%. [04]",
         8.4, INK, "bold")
    footer(ax, 5, ["01", "04"])
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide6(pdf):
    fig, ax = new_slide(True)
    header(ax, "BUILT TO BE TRUSTED", "Score only with information available at decision time",
           "The prediction point is two hours before scheduled departure. [05]", True)
    # Timeline.
    line(ax, 1.05, 4.95, 12.25, 4.95, "#42607B", 2)
    moments = [(1.2, "KNOWN IN ADVANCE", TEAL),
               (5.0, "T = −2 HOURS", ORANGE),
               (9.15, "DEPARTURE", CORAL)]
    for x, name, c in moments:
        ax.add_patch(Circle((x, 4.95), .13, facecolor=c, edgecolor=NAVY, lw=2, zorder=4))
        text(ax, x, 5.3, name, 8, c, "bold", ha="center")
    # Feature clusters.
    items = [
        (.72, 2.08, 3.58, 1.62, "SCHEDULE & ROUTE", "Calendar · carrier · origin/destination\nScheduled flight volume", TEAL),
        (4.88, 2.08, 3.58, 1.62, "RECENT AIRPORT STATE", "Only earlier departures known by T\nNo earlier cancellation flag", ORANGE),
        (9.04, 2.08, 3.58, 1.62, "WEATHER & AIRCRAFT", "Strict weather is available by T\nScheduled-hour weather is a forecast stand-in", "#9CB6FF"),
    ]
    for x, y, w, h, title, body, accent in items:
        box(ax, x, y, w, h, NAVY2, edge="#29415A")
        text(ax, x + .22, y + h - .28, title, 8, accent, "bold")
        text(ax, x + .22, y + h - .68, body, 8.2, "#D5DFE8", linespacing=1.5)
    box(ax, .72, 1.06, 11.9, .58, "#203A56", radius=.12)
    text(ax, .95, 1.35,
         "Leakage guardrails: exclude post-departure outcomes and tail-missing flags; fill unknown plane data using Jan–Sep carrier statistics. [05]",
         8.0, WHITE, va="center")
    footer(ax, 6, ["05"], True)
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide7(pdf):
    fig, ax = new_slide(False)
    header(ax, "AN HONEST TEST", "Tune on validation; keep the test months unseen",
           "Time order mirrors how the system would be built and checked in practice.")
    # Timeline blocks.
    y = 3.55
    blocks = [
        (.72, 3.1, "JAN–JUN", "Fit candidates\n222,402 flights", TEAL, "06"),
        (3.98, 3.22, "JUL–SEP", "Tune and choose\n108,481 flights", ORANGE, "06"),
        (7.36, 4.7, "OCT–DEC", "Final test · once\n104,469 flights", "#6689D6", "06"),
    ]
    for x, w, months, detail, color, src in blocks:
        box(ax, x, y, w, 1.67, WHITE, edge=GRID)
        ax.add_patch(FancyBboxPatch((x, y), .09, 1.67,
                                    boxstyle="round,pad=0,rounding_size=.035",
                                    facecolor=color, edgecolor=color))
        text(ax, x + .28, 4.92, months, 12, INK, "bold")
        text(ax, x + .28, 4.35, detail, 9, MUTED, linespacing=1.5)
        tag(ax, x + w - .62, y + .38, src)
    text(ax, .82, 3.02, "Then refit selected settings on Jan–Sep: 330,883 flights. [06]",
         10, INK, "bold")
    box(ax, .72, 1.26, 11.9, 1.18, PALE_BLUE, radius=.13)
    text(ax, 1.0, 2.13, "WHY NOT ACCURACY?", 8, "#31506E", "bold")
    text(ax, 1.0, 1.76,
         "“Nobody is late” is 85.9% accurate on test and finds no late flights. [06]",
         10, INK, "bold")
    text(ax, 1.0, 1.43,
         "We compare PR-AUC with the dumb answer on the same period; prevalence is the baseline. [06]",
         8.7, MUTED)
    footer(ax, 7, ["06"])
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide8(pdf):
    fig, ax = new_slide(True)
    header(ax, "THE RESULT", "Both alerts rank risk above the dumb baseline",
           "Precision–recall AUC on held-out Oct–Dec flights; intervals reflect day-level resampling. [06]",
           True)
    # Table frame.
    x0, y0 = .72, 2.0
    colx = [1.0, 5.15, 7.38, 9.85, 11.55]
    headers = ["PREDICTION", "DUMB BASELINE", "MODEL PR-AUC", "95% INTERVAL", "READOUT"]
    for x, h in zip(colx, headers):
        text(ax, x, 5.38, h, 7.5, "#9AABB9", "bold")
    line(ax, .9, 5.08, 12.35, 5.08, "#42607B", 1)
    rows = [
        ("Late or\ncancelled", "0.141", "0.339", "0.301–0.376", "2.4× prevalence", TEAL),
        ("Cancelled", "0.0021", "0.120", "0.002–0.233", "rare-event caution", ORANGE),
    ]
    for j, row in enumerate(rows):
        y = 4.2 - j * 1.27
        name, dumb, model, ci, note, color = row
        text(ax, 1.0, y, name, 12, WHITE, "bold")
        text(ax, 5.15, y, dumb, 12, "#CFD9E3", "bold")
        text(ax, 7.38, y, model, 18, color, "bold")
        text(ax, 9.85, y, ci, 10, "#CFD9E3")
        text(ax, 11.55, y, note, 8, "#CFD9E3")
        tag(ax, 4.5, y - .36, "06", True)
        line(ax, .9, y - .56, 12.35, y - .56, "#29415A", .7)
    box(ax, .9, 1.24, 11.45, .85, "#142943", edge="#29415A")
    text(ax, 1.17, 1.81,
         "Cancellation scores are useful for prioritization—not certainty. The interval is wide because the test set had only 224 cancellations. [01, 06]",
         8.7, "#D5DFE8", va="center")
    text(ax, .93, .92,
         "REFRESH REQUIRED  /  Stored model outputs predate the D10 imputation update; rerun notebooks 05–07 before final submission. [05–07]",
         7.2, "#FFD08A", "bold")
    footer(ax, 8, ["01", "06"], True)
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide9(pdf):
    fig, ax = new_slide(False)
    header(ax, "DECISION CARD  /  ALERT 1", "Warn clients about a possible delay",
           "Late-or-cancelled score · test quarter · human review before messaging. [07]")
    # Large results row.
    stats = [
        (".597", "validation cutoff", TEAL),
        ("11.5%", "of test flights flagged", "#6689D6"),
        ("37.4%", "of flags were right", ORANGE),
        ("30.5%", "of problem flights caught", CORAL),
    ]
    for i, (v, name, c) in enumerate(stats):
        x = .62 + i * 3.08
        box(ax, x, 3.98, 2.82, 1.37, WHITE, edge=GRID)
        text(ax, x + .18, 4.99, v, 21, INK, "bold")
        text(ax, x + .18, 4.48, name, 8.2, MUTED, "bold")
        tag(ax, x + 2.19, 4.12, "07")
        ax.add_patch(FancyBboxPatch((x, 3.98), .06, 1.37,
                                    boxstyle="round,pad=0,rounding_size=.03",
                                    facecolor=c, edgecolor=c))
    box(ax, .62, 1.52, 7.4, 1.93, NAVY, radius=.15)
    text(ax, .91, 3.12, "WHAT THE TEST QUARTER LOOKED LIKE", 8, TEAL, "bold")
    text(ax, .91, 2.63, "11,974 flags", 17, WHITE, "bold")
    text(ax, 3.25, 2.64, "4,481 true positives", 12, "#CFD9E3", "bold")
    text(ax, .91, 2.12,
         "About 130 flagged flights per day; lift 2.7× over a random shortlist. [07]",
         9, "#CFD9E3")
    box(ax, 8.36, 1.52, 4.34, 1.93, PALE_ORANGE, radius=.15)
    text(ax, 8.68, 3.12, "ACTION + HUMAN CHECK", 8, "#A65B00", "bold")
    text(ax, 8.68, 2.69, "Message · check connections", 11, INK, "bold")
    text(ax, 8.68, 2.26,
         "Verify live airline status first. Mornings are a weak spot: 5.8% recall. [07]",
         8.5, INK)
    text(ax, .66, .84,
         "REFRESH REQUIRED  /  Model outputs predate the D10 update; rerun notebooks 05–07 before final submission. [05–07]",
         6.8, "#A65B00", "bold")
    footer(ax, 9, ["07"])
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide10(pdf):
    fig, ax = new_slide(True)
    header(ax, "DECISION CARD  /  ALERT 2", "Prepare rebooking for cancellation risk",
           "A prioritization list, not a promise that a flight will be cancelled. [07]", True)
    stats = [
        (".137", "validation cutoff", TEAL),
        ("484", "test flags", "#9CB6FF"),
        ("19.4%", "flag precision", ORANGE),
        ("42%", "cancellations caught", CORAL),
    ]
    for i, (v, name, c) in enumerate(stats):
        x = .62 + i * 3.08
        box(ax, x, 4.32, 2.82, 1.42, NAVY2, edge="#29415A")
        text(ax, x + .2, 5.28, v, 22, WHITE, "bold")
        text(ax, x + .2, 4.78, name, 8.2, "#C2D0DE", "bold")
        tag(ax, x + 2.19, 4.45, "07", True)
        ax.add_patch(FancyBboxPatch((x, 4.32), .06, 1.42,
                                    boxstyle="round,pad=0,rounding_size=.03",
                                    facecolor=c, edgecolor=c))
    box(ax, .62, 1.55, 6.0, 2.1, "#142943", edge="#29415A")
    text(ax, .94, 3.28, "94 / 224", 22, WHITE, "bold")
    text(ax, 3.1, 3.24, "cancellations identified", 10, "#CFD9E3", va="center")
    text(ax, .94, 2.68, "5.3 flags per day · lift 91× over random. [07]",
         9, "#CFD9E3")
    text(ax, .94, 2.15, "Offer rebooking options; never auto-rebook.", 10, TEAL, "bold")
    box(ax, 6.94, 1.55, 5.76, 2.1, "#3A2D2B", edge="#6C4A3F")
    text(ax, 7.27, 3.28, "HANDLE WITH CARE", 8, ORANGE, "bold")
    text(ax, 7.27, 2.82, "115 of the 224 test cancellations fell on one day.",
         10, WHITE, "bold")
    text(ax, 7.27, 2.34,
         "Only one test quarter and 224 events: the measured result is highly uncertain. [01, 07]",
         8.5, "#E4D6D1")
    text(ax, .66, .84,
         "REFRESH REQUIRED  /  Model outputs predate the D10 update; rerun notebooks 05–07 before final submission. [05–07]",
         6.8, "#FFD08A", "bold")
    footer(ax, 10, ["01", "07"], True)
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide11(pdf):
    fig, ax = new_slide(False)
    header(ax, "LIMITS & MONITORING", "Keep a person in the loop—and watch drift",
           "The test quarter is not a guarantee of future performance.")
    limits = [
        ("SEASONAL DRIFT", "Late-or-cancelled rate fell from 25.7% in train to 14.1% in test. [01]",
         ORANGE),
        ("EARLY-MORNING GAP", "Alert 1 caught 5.8% of morning problem flights; Newark cancellation recall was 0%. [06, 07]",
         CORAL),
        ("RARE EVENT", "115 / 224 test cancellations landed on 18 December; cause is unexplained. [01, 07]",
         "#6689D6"),
    ]
    for i, (title, body, accent) in enumerate(limits):
        y = 4.53 - i * 1.03
        box(ax, .68, y - .54, 7.22, .79, WHITE, edge=GRID)
        ax.add_patch(Circle((.99, y - .15), .10, color=accent, zorder=3))
        text(ax, 1.23, y + .06, title, 8, MUTED, "bold")
        text(ax, 1.23, y - .21, wrap(body, 77), 8.6, INK)
    box(ax, 8.25, 1.47, 4.45, 3.9, NAVY, radius=.16)
    text(ax, 8.58, 5.01, "A TENTATIVE CHECK RULE", 8, TEAL, "bold")
    text(ax, 8.58, 4.49, "Alert 1", 12, WHITE, "bold")
    text(ax, 8.58, 4.13, "Review if weekly recall is below 14%\nfor two weeks running. [07]",
         8.5, "#CFD9E3", linespacing=1.5)
    line(ax, 8.58, 3.51, 12.23, 3.51, "#29415A", .8)
    text(ax, 8.58, 3.22, "Alert 2", 12, WHITE, "bold")
    text(ax, 8.58, 2.84, "Review 4-week blocks with ≥30\ncancellations if recall is below 23%. [07]",
         8.5, "#CFD9E3", linespacing=1.5)
    text(ax, 8.58, 1.88, "Thresholds are tentative; the evidence is limited.",
         7.5, ORANGE)
    text(ax, .66, .84,
         "Model score snapshot predates D10 correction; refresh downstream analyses before submission. [05–07]",
         6.8, "#A65B00", "bold")
    footer(ax, 11, ["01", "06", "07"])
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def slide12(pdf):
    fig, ax = new_slide(True)
    # Closural slide with large executive call and three concise commitments.
    label(ax, .72, 6.72, "THE DECISION", TEAL, True)
    text(ax, .72, 6.14, "Approve a careful pilot.\nEarn the right to scale.", 30, WHITE, "bold",
         linespacing=1.15)
    text(ax, .75, 4.55,
         "Start with human-reviewed alerts. Measure capacity, outcomes and drift before changing client operations.",
         11, "#C2D0DE", linespacing=1.5)
    commitments = [
        ("01", "REVIEW", "A named person verifies live status before any client contact.", TEAL),
        ("02", "MONITOR", "Check performance weekly; pause and investigate when the stop rule triggers.", ORANGE),
        ("03", "IMPROVE", "Add real forecast data and cancellation timestamps when available.", "#9CB6FF"),
    ]
    for i, (n, title, body, accent) in enumerate(commitments):
        y = 3.6 - i * .82
        ax.add_patch(Circle((.98, y), .23, color=accent))
        text(ax, .98, y, n, 8.5, NAVY, "bold", ha="center", va="center")
        text(ax, 1.42, y + .14, title, 8, accent, "bold")
        text(ax, 2.6, y + .14, body, 8.7, WHITE, va="center")
    box(ax, 9.1, 1.77, 3.55, 2.1, "#142943", radius=.16, edge="#29415A")
    text(ax, 9.42, 3.51, "THE ASK", 8, TEAL, "bold")
    text(ax, 9.42, 3.08, "Agree the daily alert capacity\nand who owns the review.",
         12, WHITE, "bold", linespacing=1.5)
    text(ax, 9.42, 2.16, "Pilot duration is a business choice—not a model result.",
         7.5, "#C2D0DE")
    text(ax, .75, 1.06,
         "Data: nycflights23 (CC0). Results, limitations and methods are traceable in notebooks 01–07. [01–07]",
         8, "#AABAC9")
    footer(ax, 12, ["01", "02", "03", "04", "05", "06", "07"], True)
    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def main():
    plt.rcParams.update({
        "font.family": FONT,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.dpi": 160,
    })
    slides = [slide1, slide2, slide3, slide4, slide5, slide6,
              slide7, slide8, slide9, slide10, slide11, slide12]
    with PdfPages(OUT, metadata={
        "Title": "TMS Flights — Know before your clients do",
        "Author": "TMS",
        "Subject": "12-slide data-science decision presentation",
    }) as pdf:
        for build in slides:
            build(pdf)
    print(f"Wrote {len(slides)} slides to {OUT}")


if __name__ == "__main__":
    main()
