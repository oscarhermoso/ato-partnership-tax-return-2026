"""Add fillable form fields to the ATO Partnership tax return 2026 (NAT 0659).

Detects the printed white character boxes and lays fields over them:
  - runs of adjacent character boxes -> comb text field (one char per box)
  - single boxes next to Yes/No/Title/status labels -> checkbox
  - wide money boxes -> right-aligned text field
  - signature boxes -> plain text field
"""
import sys
import pymupdf

SRC = "ex_0659-6.2026.pdf"
DST = "ex_0659-6.2026-fillable.pdf"
WHITE = (1.0, 1.0, 1.0)
CHECK_LABELS = {"Yes", "No", "Mr", "Mrs", "Miss", "Ms",
                "B1", "B2", "B3", "Z2", "G1", "G2", "E1", "E2", "E3"}
RUN_GAP = 4.0  # max gap (pt) between boxes in the same comb run


def boxes_on(page):
    out = []
    for dr in page.get_drawings():
        if dr.get("fill") != WHITE:
            continue
        for it in dr["items"]:
            if it[0] != "re":
                continue
            r = it[1]
            # printed char boxes are stroked; page 1 TFN boxes are fill-only
            if dr["type"] == "fs" or (dr["type"] == "f" and 12 < r.width < 14 and 16 < r.height < 18):
                if r.height < 60 and r.width < 480:
                    out.append(pymupdf.Rect(r))
    # a few boxes are drawn twice in the source
    seen, uniq = set(), []
    for r in out:
        key = tuple(round(v) for v in r)
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    return uniq


def words_in(words, r):
    inner = pymupdf.Rect(r.x0 + 2, r.y0 + 3, r.x1 - 2, r.y1 - 3)
    return [w for w in words if pymupdf.Rect(w[:4]).intersects(inner)]


def label_left(words, r, reach=60):
    """Closest words on the same line to the left of r."""
    cands = [w for w in words
             if w[2] <= r.x0 + 1 and w[2] > r.x0 - reach
             and abs((w[1] + w[3]) / 2 - (r.y0 + r.y1) / 2) < 7]
    cands.sort(key=lambda w: w[2])
    return " ".join(w[4] for w in cands[-4:])


def build(page, pno, words):
    boxes = boxes_on(page)
    # skip the "SMITH ST" example boxes and the office-use area
    sample = page.search_for("Place") if pno == 0 else []
    office = page.search_for("Office use only")
    fields = []
    small = []
    for r in boxes:
        if office and r.y0 > office[0].y0 - 5 and r.x0 > office[0].x0 - 10:
            continue
        if sample and sample[0].y0 - 30 < r.y0 < sample[0].y0 and r.x0 > sample[0].x0:
            continue
        inside = words_in(words, r)
        if r.width < 14:
            if inside:
                continue
            small.append(r)
            continue
        texts = [w[4] for w in inside]
        if texts and texts != [".00"]:
            continue  # note/instruction panel
        fr = pymupdf.Rect(r)
        if texts == [".00"]:
            fr.x1 = inside[0][0] - 1
        kind = "sig" if r.height > 20 else "money"
        fields.append((kind, fr, 1, label_left(words, r, 150)))

    # group small boxes into horizontal runs
    # cluster into rows first (box tops can differ by a fraction of a point)
    small.sort(key=lambda r: r.y0)
    rows = []
    for r in small:
        if rows and r.y0 - rows[-1][0].y0 < 1.5:
            rows[-1].append(r)
        else:
            rows.append([r])
    small = [r for row in rows for r in sorted(row, key=lambda r: r.x0)]
    runs = []
    for r in small:
        if runs:
            last = runs[-1][-1]
            if abs(last.y0 - r.y0) < 1.5 and 0 <= r.x0 - last.x1 < RUN_GAP:
                runs[-1].append(r)
                continue
        runs.append([r])
    def separated(a, b):  # digit groups split by a printed comma or point
        return abs(a[0].y0 - b[0].y0) < 1.5 and RUN_GAP <= b[0].x0 - a[-1].x1 < 10

    for i, run in enumerate(runs):
        rect = pymupdf.Rect(run[0].x0, run[0].y0, run[-1].x1, run[-1].y1)
        numeric = (i + 1 < len(runs) and separated(run, runs[i + 1])) or \
                  (i > 0 and separated(runs[i - 1], run))
        lab = label_left(words, run[0])
        last_word = lab.split()[-1] if lab else ""
        if len(run) == 1 and last_word in CHECK_LABELS:
            fields.append(("check", rect, 1, lab))
        else:
            fields.append(("num" if numeric else "comb", rect, len(run), lab))

    # reading order: top-to-bottom, left-to-right (rows within 4pt)
    fields.sort(key=lambda f: (round(f[1].y0 / 4), f[1].x0))
    return fields


def main():
    doc = pymupdf.open(SRC)
    n = 0
    for pno, page in enumerate(doc):
        words = page.get_text("words")
        for idx, (kind, rect, count, lab) in enumerate(build(page, pno, words)):
            w = pymupdf.Widget()
            w.field_name = f"p{pno + 1:02d}_{idx:03d}"
            w.field_label = lab or w.field_name
            w.rect = rect
            w.border_width = 0
            w.border_color = None
            w.fill_color = None
            w.text_font = "Helv"
            w.text_color = (0, 0, 0)
            if kind == "check":
                w.field_type = pymupdf.PDF_WIDGET_TYPE_CHECKBOX
                w.field_value = False
                w.text_font = "ZaDb"
            else:
                w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
                w.text_fontsize = 10
                if kind in ("comb", "num"):
                    w.text_maxlen = count
                    w.field_flags = pymupdf.PDF_TX_FIELD_IS_COMB
            w = page.add_widget(w)
            if kind in ("num", "money"):
                # right-justify amounts, as the ATO expects
                doc.xref_set_key(w.xref, "Q", "2")
            n += 1
    # let viewers rebuild appearances (needed for right-aligned combs)
    doc.xref_set_key(doc.pdf_catalog(), "AcroForm/NeedAppearances", "true")
    doc.save(DST, garbage=3, deflate=True)
    print(f"added {n} fields -> {DST}")


if __name__ == "__main__":
    if "--dump" in sys.argv:
        doc = pymupdf.open(SRC)
        for pno, page in enumerate(doc):
            for kind, rect, count, lab in build(page, pno, page.get_text("words")):
                if kind not in ("comb", "num") or count == 1:
                    print(pno + 1, kind, count, [round(x) for x in rect], repr(lab))
    else:
        main()
