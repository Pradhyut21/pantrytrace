"""Generate the eight-page PDF pitch from editable text and actual UI evidence."""
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

PROJECT = Path(__file__).resolve().parents[1]
WORK = PROJECT.parents[1] / "work" / "pitch"
OUT = PROJECT.parent / "pantrytrace-pitch.pdf"
WORK.mkdir(parents=True, exist_ok=True)
for name, file in (("Georgia", "georgia.ttf"), ("GeorgiaBold", "georgiab.ttf"),
                   ("Arial", "arial.ttf"), ("ArialBold", "arialbd.ttf")):
    pdfmetrics.registerFont(TTFont(name, "C:/Windows/Fonts/" + file))

W, H = 960, 540
GREEN, CREAM = HexColor("#173f34"), HexColor("#f6f6ef")
MUTED, PALE = HexColor("#62716b"), HexColor("#b9c797")
c = Canvas(str(OUT), pagesize=(W, H))
c.setTitle("PantryTrace - Every recall decision needs a receipt")
c.setAuthor("PantryTrace pre-event prototype")


def txt(x, y, value, size=19, font="Arial", color=GREEN):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, H - y, value)


def para(x, y, value, width, size=19, leading=27, font="Arial", color=GREEN):
    style = ParagraphStyle("p", fontName=font, fontSize=size, leading=leading,
                           textColor=color, spaceAfter=0)
    block = Paragraph(escape(value).replace("\n", "<br/>"), style)
    _, height = block.wrap(width, H)
    block.drawOn(c, x, H - y - height)
    return height


def page(number, dark=False):
    c.setFillColor(GREEN if dark else CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    txt(42, 30, "PANTRYTRACE", 10, "ArialBold", PALE if dark else MUTED)
    txt(893, 30, f"{number:02d}", 10, "Arial", PALE if dark else MUTED)


def foot(value, url=None, dark=False):
    para(42, 500, value, 875, 9, 12, color=PALE if dark else MUTED)
    if url:
        c.linkURL(url, (42, 14, 918, 44), relative=0, thickness=0)


def image_crop(name, bounds, x, top, width, height=None):
    source = Image.open(PROJECT / "docs" / "screenshots" / "workbench.png")
    im = source.crop(bounds)
    im.save(WORK / (name + ".png"))
    height = height or width * im.height / im.width
    c.drawImage(ImageReader(im), x, H - top - height, width=width, height=height,
                preserveAspectRatio=True, mask="auto")


# 1 - Minimal cover.
page(1, True)
txt(42, 132, "PantryTrace", 62, "Georgia", CREAM)
para(42, 181, "Every recall decision\nneeds a receipt", 820, 45, 55, "Georgia", CREAM)
para(44, 359, "Internal recall triage for food-bank coordinators", 800, 21, 29, color=CREAM)
txt(44, 428, "SOLVING FRAGMENTED INTELLIGENCE", 13, "ArialBold", PALE)
foot("Declared pre-event prototype | Prepared 19 October 2026 | All operational records are synthetic", dark=True)
c.showPage()

# 2 - Grounded target-user problem.
page(2)
txt(42, 94, "A notice starts the investigation", 36, "Georgia")
para(42, 133, "The coordinator still has to inspect stock, find the lot records\nand identify partner transfers.", 865, 23, 31)
columns = [(42, "Notice", "Product identity\nAffected lots"),
           (350, "Stock", "Supplier alias\nMissing lot"),
           (656, "Transfers", "Partner location\nQuantity moved")]
for x, heading, body in columns:
    txt(x, 286, heading, 29, "Georgia")
    para(x, 310, body, 265, 20, 29)
para(42, 414, "Partner-agency guidance requires inventory inspection and quarantine of recalled product.",
     860, 19, 27, "ArialBold")
foot("Source: Foodbank of Southeastern Virginia and the Eastern Shore, Partner Agency Manual, January 2026, recall section. foodbankonline.org/wp-content/uploads/2026/01/PAM-Jan-2026.pdf",
     "https://foodbankonline.org/wp-content/uploads/2026/01/PAM-Jan-2026.pdf")
c.showPage()

# 3 - Real fixture output, quantities distinguish on-hand and outbound.
page(3)
txt(42, 94, "A missing lot becomes a solvable question", 34, "Georgia")
txt(42, 205, "36 = 30 + 6", 48, "Georgia")
txt(44, 242, "received", 17, color=MUTED)
txt(166, 242, "on hand", 17, color=MUTED)
txt(277, 242, "transferred", 17, color=MUTED)
para(42, 280, "An exact batch join and supplier alias\nresolve lot NS260902.", 360, 21, 29)
para(42, 379, "30 on-hand units proposed for quarantine.\n6 outbound units retained separately.", 360, 19, 27)
image_crop("stock-result", (294, 570, 1406, 995), 424, 153, 492)
para(424, 364, "Actual workbench: missing lot, receipt retrieval,\nthen a supported internal draft.", 490, 18, 26)
foot("Synthetic fixture proof: data/intake_ledger.csv LEDGER-A01; inventory INV-A01; transfer TRANSFER-A01. Direct outbound transfers only. No action is executed.")
c.showPage()

# 4 - Architecture with an actual execution-trace crop.
page(4)
txt(42, 94, "The critic changes the plan", 36, "Georgia")
steps = [(170, "01", "Propose from available stock records"),
         (235, "02", "Critic identifies the missing lot"),
         (300, "03", "Query alias and exact intake batch"),
         (365, "04", "Recompute, or retain human review")]
for y, n, text in steps:
    txt(42, y, n, 25, "Georgia", MUTED)
    para(102, y - 21, text, 490, 21, 28)
image_crop("execution-trace", (1020, 800, 1400, 1285), 635, 130, 252)
para(42, 427, "Bounded deterministic roles share evidence and retry.\nThe current controller does not claim LLM autonomy.", 550, 17, 25)
foot("Actual local execution trace from the synthetic ambiguous case. Pattern references: ReAct (arxiv.org/abs/2210.03629), Self-RAG (arxiv.org/abs/2310.11511); these methods are not reproduced.",
     "https://arxiv.org/abs/2310.11511")
c.showPage()

# 5 - Abstention is visible product behavior.
page(5)
txt(42, 94, "Conflicting receipts stay unresolved", 36, "Georgia")
txt(42, 226, "18", 84, "Georgia")
para(46, 252, "units require human inspection", 390, 21, 29)
txt(536, 226, "10", 84, "Georgia")
para(540, 252, "units match an affected lot", 375, 21, 29)
para(42, 350, "Two receipts disagree about the same batch. The system\nkeeps both records and requests a physical label check.", 865, 23, 32)
para(42, 437, "Every operational action remains an internal draft for a person to approve.", 865, 18, 26)
foot("Executed synthetic conflict case: INV-C01; LEDGER-C01 vs LEDGER-C02. INV-C02 matches lot NS260902. No food-safety clearance or public recall alert is produced.")
c.showPage()

# 6 - Transparent scope of regression proof.
page(6, True)
txt(42, 94, "Measured on the declared development set", 34, "Georgia", CREAM)
txt(42, 245, "9 / 9", 91, "Georgia", CREAM)
para(46, 273, "development items correct\nafter evidence retrieval", 425, 24, 33, color=CREAM)
txt(576, 230, "8 / 9", 51, "Georgia", PALE)
para(579, 254, "inventory-only baseline", 330, 21, 29, color=CREAM)
txt(44, 388, "44 automated tests pass", 27, "ArialBold", CREAM)
para(44, 414, "Four authored synthetic scenarios. This regression set is not an independent\nholdout or a real-world accuracy estimate.", 855, 18, 26, color=CREAM)
foot("Proof: python -m pantrytrace evaluate; python -m unittest discover -s tests -v. The baseline is the same controller before missing-evidence retrieval. Results checked 19 October 2026.", dark=True)
c.showPage()

# 7 - Sponsor claims are bounded by actual execution evidence.
page(7)
txt(42, 94, "Sponsor proof, stated precisely", 36, "Georgia")
rows = [
    (164, "Meterless", "VERIFIED LOCALLY", "Official H-MEM remember, recall, audit and feedback"),
    (249, "Zetaris", "LIVE INSTANCE PENDING", "Read-only adapter and explicit connected-record path"),
    (334, "NVIDIA", "NO LIVE CALL", "Optional critique adapter; contribution unmeasured"),
    (419, "Cursor", "ACTUAL USE PENDING", "Required eligible-window development still to complete"),
]
for y, name, status, detail in rows:
    txt(42, y, name, 27, "Georgia")
    txt(295, y - 5, status, 16, "ArialBold")
    para(295, y + 6, detail, 620, 18, 26)
foot("Proof: artifacts/meterless-smoke.json; official H-MEM commit a3f15cee1b108c436827cdd10740fd113016e354. Remote API calls in that smoke check: 0. See docs/sponsor-integration-research.md for provider contracts.")
c.showPage()

# 8 - Honest preparation/build boundary and focused next proof.
page(8, True)
para(42, 87, "Prepared openly.\nBuilt during the window.", 815, 44, 54, "Georgia", CREAM)
txt(44, 264, "19 OCT 2026", 16, "ArialBold", PALE)
para(44, 281, "Declare this pre-event prototype,\ncode, fixtures and media.", 456, 22, 30, color=CREAM)
txt(44, 391, "22 OCT 2026, 05:30 IST", 16, "ArialBold", PALE)
para(44, 408, "Build opens. Complete new work\nin Cursor and capture the proof.", 470, 21, 29, color=CREAM)
txt(600, 264, "NEXT PROOF", 16, "ArialBold", PALE)
para(600, 285, "Real Zetaris views\nBroader held-out cases\nCoordinator review\nSponsor execution traces", 310, 21, 34, color=CREAM)
foot("Official event: hackathon.genai.works/event/open-agent-hackathon-2026. Build opening: 22 October 2026, 00:00 UTC. Final organizer announcements and eligibility decisions control.",
     "https://hackathon.genai.works/event/open-agent-hackathon-2026", dark=True)
c.showPage()
c.save()
print(OUT)
